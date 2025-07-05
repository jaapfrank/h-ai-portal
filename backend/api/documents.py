"""
FastAPI endpoints voor document processing
Ondersteunt factuur en declaratie verwerking met ERP integratie
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
import io

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, Field

from agents.invoice_agent import get_invoice_agent
from agents.receipt_agent import get_receipt_agent
from services.graph_api_service import get_graph_service
from services.document_intelligence_service import get_document_intelligence_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Document Processing"])


# Pydantic models voor API requests/responses
class InvoiceProcessingRequest(BaseModel):
    """Request model voor invoice processing"""
    days_back: int = Field(default=1, description="Aantal dagen terug om te scannen")
    mailbox: Optional[str] = Field(None, description="Specifieke mailbox om te scannen")


class InvoiceProcessingResponse(BaseModel):
    """Response model voor invoice processing"""
    session_id: str = Field(..., description="Processing session ID")
    status: str = Field(..., description="Processing status")
    total_messages: int = Field(..., description="Aantal gevonden berichten")
    processed_count: int = Field(..., description="Aantal verwerkte facturen")
    success_count: int = Field(..., description="Aantal succesvol verwerkte facturen")
    error_count: int = Field(..., description="Aantal errors")
    results: List[Dict[str, Any]] = Field(..., description="Verwerking resultaten")


class ReceiptUploadResponse(BaseModel):
    """Response model voor receipt upload"""
    receipt_id: str = Field(..., description="Receipt ID")
    success: bool = Field(..., description="Verwerking geslaagd")
    expense_proposal: Optional[Dict[str, Any]] = Field(None, description="Generated expense proposal")
    approval_status: str = Field(..., description="Approval status")
    processing_stages: Dict[str, Any] = Field(..., description="Processing stage details")


class DocumentAnalysisResponse(BaseModel):
    """Response model voor document analyse"""
    success: bool = Field(..., description="Analyse geslaagd")
    document_type: str = Field(..., description="Type document")
    confidence_score: float = Field(..., description="Confidence score")
    extracted_fields: Dict[str, Any] = Field(..., description="Geëxtraheerde velden")


# Helper functions
def get_user_from_request(request: Request) -> str:
    """Extract user ID van request (placeholder - zou JWT parsing zijn)"""
    return request.headers.get("X-User-ID", "demo_user")


# API Endpoints

@router.post("/invoices/process", response_model=InvoiceProcessingResponse)
async def start_invoice_processing(
    request: InvoiceProcessingRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
    invoice_agent = Depends(get_invoice_agent)
):
    """
    Start automatische factuurverwerking vanaf mailbox
    """
    try:
        user_id = get_user_from_request(http_request)
        logger.info(f"Start invoice processing voor user {user_id}, {request.days_back} dagen terug")
        
        # Start invoice processing session
        session_result = await invoice_agent.start_invoice_processing_session(request.days_back)
        
        if session_result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=session_result.get("error", "Processing failed"))
        
        return InvoiceProcessingResponse(
            session_id=session_result["session_id"],
            status=session_result.get("current_stage", "unknown"),
            total_messages=session_result.get("total_messages", 0),
            processed_count=session_result.get("processed_count", 0),
            success_count=session_result.get("success_count", 0),
            error_count=session_result.get("error_count", 0),
            results=session_result.get("results", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij invoice processing: {e}")
        raise HTTPException(status_code=500, detail=f"Invoice processing fout: {str(e)}")


@router.get("/invoices/status")
async def get_invoice_processing_status(
    http_request: Request,
    invoice_agent = Depends(get_invoice_agent)
):
    """
    Verkrijg status van huidige invoice processing
    """
    try:
        status = await invoice_agent.get_processing_status()
        return status
        
    except Exception as e:
        logger.error(f"Fout bij ophalen invoice status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/receipts/upload", response_model=ReceiptUploadResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    project_code: Optional[str] = Form(None),
    cost_center: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    suggested_category: Optional[str] = Form(None),
    http_request: Request = None,
    receipt_agent = Depends(get_receipt_agent)
):
    """
    Upload en verwerk receipt/bonnetje voor declaratie
    """
    try:
        user_id = get_user_from_request(http_request)
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Geen bestand geüpload")
        
        # Check file type
        allowed_types = ["image/jpeg", "image/png", "image/tiff", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Niet ondersteund bestandstype: {file.content_type}")
        
        # Read file data
        file_data = await file.read()
        
        # Prepare metadata
        metadata = {}
        if project_code:
            metadata["project_code"] = project_code
        if cost_center:
            metadata["cost_center"] = cost_center
        if location:
            metadata["location"] = location
        if suggested_category:
            metadata["suggested_category"] = suggested_category
        
        logger.info(f"Processing receipt upload {file.filename} for user {user_id}")
        
        # Process receipt
        result = await receipt_agent.process_receipt_upload(
            file_data,
            file.filename,
            user_id,
            metadata
        )
        
        if not result["success"]:
            raise HTTPException(status_code=422, detail=result.get("error", "Receipt processing failed"))
        
        return ReceiptUploadResponse(
            receipt_id=result["receipt_id"],
            success=result["success"],
            expense_proposal=result.get("expense_proposal"),
            approval_status=result.get("approval_status", "pending"),
            processing_stages=result.get("processing_stages", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij receipt upload: {e}")
        raise HTTPException(status_code=500, detail=f"Receipt upload fout: {str(e)}")


@router.get("/receipts/expenses/{user_id}")
async def get_user_expenses(
    user_id: str,
    days: int = 30,
    http_request: Request = None,
    receipt_agent = Depends(get_receipt_agent)
):
    """
    Verkrijg expense overzicht voor gebruiker
    """
    try:
        # In productie zou je hier autorisatie checken
        current_user = get_user_from_request(http_request)
        
        summary = await receipt_agent.get_user_expense_summary(user_id, days)
        
        return summary
        
    except Exception as e:
        logger.error(f"Fout bij ophalen user expenses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/receipts/approve/{expense_id}")
async def approve_expense(
    expense_id: str,
    decision: str = Form(...),  # approved, rejected, needs_info
    comments: str = Form(""),
    http_request: Request = None,
    receipt_agent = Depends(get_receipt_agent)
):
    """
    Approve of reject expense declaratie
    """
    try:
        approver_id = get_user_from_request(http_request)
        
        if decision not in ["approved", "rejected", "needs_info"]:
            raise HTTPException(status_code=400, detail="Invalid decision")
        
        result = await receipt_agent.process_expense_approval(
            expense_id,
            approver_id,
            decision,
            comments
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Approval processing failed"))
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij expense approval: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    file: UploadFile = File(...),
    document_type: str = Form("auto"),  # auto, invoice, receipt, generic
    http_request: Request = None,
    doc_intelligence = Depends(get_document_intelligence_service)
):
    """
    Analyseer document met Azure Document Intelligence
    """
    try:
        user_id = get_user_from_request(http_request)
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="Geen bestand geüpload")
        
        # Read file data
        file_data = await file.read()
        
        logger.info(f"Analyzing document {file.filename} as {document_type} for user {user_id}")
        
        # Choose analysis method based on document type
        if document_type == "invoice" or (document_type == "auto" and file.filename.lower().endswith('.pdf')):
            result = await doc_intelligence.analyze_invoice(file_data, file.filename)
        elif document_type == "receipt" or (document_type == "auto" and any(file.filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png'])):
            result = await doc_intelligence.analyze_receipt(file_data, file.filename)
        else:
            result = await doc_intelligence.analyze_document_generic(file_data, file.filename)
        
        if not result["success"]:
            raise HTTPException(status_code=422, detail=result.get("error", "Document analysis failed"))
        
        return DocumentAnalysisResponse(
            success=result["success"],
            document_type=result.get("document_type", "unknown"),
            confidence_score=result.get("confidence_score", 0.0),
            extracted_fields=result.get("extracted_fields", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij document analyse: {e}")
        raise HTTPException(status_code=500, detail=f"Document analyse fout: {str(e)}")


@router.get("/health")
async def document_processing_health():
    """
    Health check voor document processing services
    """
    try:
        # Test alle services
        graph_service = get_graph_service()
        doc_intelligence = get_document_intelligence_service()
        
        graph_health = await graph_service.test_connection()
        doc_intel_health = await doc_intelligence.test_connection()
        
        overall_status = "healthy" if (
            graph_health["status"] == "success" and 
            doc_intel_health["status"] == "success"
        ) else "unhealthy"
        
        return {
            "status": overall_status,
            "graph_api": graph_health,
            "document_intelligence": doc_intel_health,
            "agents": {
                "invoice_agent": "initialized",
                "receipt_agent": "initialized"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Document processing health check gefaald: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/statistics")
async def get_processing_statistics(
    days: int = 30,
    http_request: Request = None,
    invoice_agent = Depends(get_invoice_agent),
    receipt_agent = Depends(get_receipt_agent)
):
    """
    Verkrijg processing statistieken voor dashboard
    """
    try:
        user_id = get_user_from_request(http_request)
        
        # Haal statistieken op
        invoice_stats = await invoice_agent.get_processing_statistics(days)
        
        # In productie zou dit een aggregatie zijn van alle users/processing
        stats = {
            "period_days": days,
            "invoice_processing": invoice_stats,
            "receipt_processing": {
                "total_receipts_processed": 0,
                "total_amount_processed": 0.0,
                "by_category": {},
                "approval_rate": 0.0
            },
            "system_performance": {
                "average_processing_time": 0.0,
                "success_rate": 0.0,
                "error_rate": 0.0
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Fout bij ophalen statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Router toevoegen aan main app
def include_documents_router(app):
    """Helper functie om documents router toe te voegen aan FastAPI app"""
    app.include_router(router)
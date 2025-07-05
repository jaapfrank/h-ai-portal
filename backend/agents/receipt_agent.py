"""
ReceiptAgent - Agent voor declaratieverwerking uit foto's
Verwerkt bonnetjes en receipts voor onkostendeclaraties
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
from decimal import Decimal
import base64
import io
from PIL import Image

from ..services.document_intelligence_service import get_document_intelligence_service
from ..services.letta_memory_service import get_letta_service
from ..core.config import get_config

logger = logging.getLogger(__name__)


class ReceiptProcessingAgent:
    """
    Agent voor verwerking van receipt/bonnetje foto's
    Focus op onkostendeclaraties en expense management
    """
    
    def __init__(self):
        self.doc_intelligence = get_document_intelligence_service()
        self.letta_service = get_letta_service()
        
        # Receipt processing configuration
        self.expense_categories = {
            "fuel": ["brandstof", "tank", "shell", "bp", "esso", "total"],
            "food": ["restaurant", "cafe", "mcdonald", "kfc", "lunch", "dinner"],
            "transport": ["taxi", "uber", "bus", "trein", "parkeren", "parking"],
            "accommodation": ["hotel", "motel", "booking", "airbnb"],
            "supplies": ["office", "depot", "supplies", "kantoor"],
            "other": []
        }
        
        # Expense limits per category (in EUR)
        self.expense_limits = {
            "fuel": 500.0,
            "food": 50.0,
            "transport": 200.0,
            "accommodation": 300.0,
            "supplies": 100.0,
            "other": 25.0
        }
    
    async def process_receipt_upload(self, 
                                   image_data: bytes, 
                                   filename: str, 
                                   user_id: str,
                                   metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verwerk uploaded receipt/bonnetje
        
        Args:
            image_data: Image data als bytes
            filename: Bestandsnaam
            user_id: ID van gebruiker die declareert
            metadata: Extra metadata (locatie, project, etc.)
            
        Returns:
            Verwerkingsresultaat met declaratie voorstel
        """
        try:
            logger.info(f"Start receipt verwerking voor {filename} van user {user_id}")
            
            processing_result = {
                "receipt_id": f"REC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}",
                "filename": filename,
                "user_id": user_id,
                "uploaded_at": datetime.utcnow().isoformat(),
                "success": False,
                "processing_stages": {},
                "expense_proposal": None,
                "approval_status": "pending"
            }
            
            # Stage 1: Image preprocessing en validation
            preprocessing_result = await self._preprocess_image(image_data, filename)
            processing_result["processing_stages"]["preprocessing"] = preprocessing_result
            
            if not preprocessing_result["success"]:
                processing_result["error"] = preprocessing_result["error"]
                return processing_result
            
            # Stage 2: OCR via Document Intelligence
            ocr_result = await self._extract_receipt_data(preprocessing_result["processed_image"], filename)
            processing_result["processing_stages"]["ocr"] = ocr_result
            
            if not ocr_result["success"]:
                processing_result["error"] = ocr_result["error"]
                return processing_result
            
            # Stage 3: Expense categorization en validation
            categorization_result = await self._categorize_expense(ocr_result["extracted_data"], metadata)
            processing_result["processing_stages"]["categorization"] = categorization_result
            
            # Stage 4: Generate expense proposal
            proposal_result = await self._generate_expense_proposal(
                ocr_result["extracted_data"],
                categorization_result,
                user_id,
                metadata
            )
            processing_result["processing_stages"]["proposal"] = proposal_result
            processing_result["expense_proposal"] = proposal_result.get("proposal")
            
            # Stage 5: Approval workflow determination
            approval_result = await self._determine_approval_workflow(proposal_result.get("proposal"))
            processing_result["processing_stages"]["approval"] = approval_result
            processing_result["approval_status"] = approval_result.get("status", "pending")
            
            processing_result["success"] = True
            processing_result["completed_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Receipt verwerking voltooid voor {filename}")
            return processing_result
            
        except Exception as e:
            logger.error(f"Fout bij receipt verwerking voor {filename}: {e}")
            return {
                "receipt_id": processing_result.get("receipt_id", "unknown"),
                "filename": filename,
                "user_id": user_id,
                "success": False,
                "error": str(e),
                "uploaded_at": datetime.utcnow().isoformat()
            }
    
    async def _preprocess_image(self, image_data: bytes, filename: str) -> Dict[str, Any]:
        """Preprocess image voor optimale OCR"""
        try:
            # Validate image
            if len(image_data) == 0:
                return {"success": False, "error": "Lege image data"}
            
            # Check file size (max 10MB voor receipts)
            max_size = 10 * 1024 * 1024
            if len(image_data) > max_size:
                return {"success": False, "error": f"Image te groot: {len(image_data)/1024/1024:.1f}MB (max 10MB)"}
            
            # For now, return original image - in productie zou je hier kunnen:
            # - Image rotation detection
            # - Contrast/brightness enhancement
            # - Noise reduction
            # - Format conversion
            
            return {
                "success": True,
                "processed_image": image_data,
                "original_size": len(image_data),
                "preprocessing_applied": ["validation"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _extract_receipt_data(self, image_data: bytes, filename: str) -> Dict[str, Any]:
        """Extract data via Azure Document Intelligence"""
        try:
            # Use receipt model
            result = await self.doc_intelligence.analyze_receipt(image_data, filename)
            
            if result["success"]:
                return {
                    "success": True,
                    "extracted_data": result,
                    "confidence_score": result.get("confidence_score", 0.0)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "OCR failed")
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _categorize_expense(self, receipt_data: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Categoriseer expense op basis van receipt data"""
        try:
            extracted_fields = receipt_data.get("extracted_fields", {})
            
            # Extract merchant info voor categorisatie
            merchant_name = extracted_fields.get("merchant_name", {}).get("value", "").lower()
            
            # Determine category
            determined_category = "other"
            confidence = 0.0
            
            for category, keywords in self.expense_categories.items():
                for keyword in keywords:
                    if keyword in merchant_name:
                        determined_category = category
                        confidence = 0.8
                        break
                if confidence > 0:
                    break
            
            # Additional categorization via metadata
            if metadata and metadata.get("suggested_category"):
                suggested = metadata["suggested_category"].lower()
                if suggested in self.expense_categories:
                    determined_category = suggested
                    confidence = max(confidence, 0.6)
            
            # Extract amount voor validation
            amount = 0.0
            amount_field = extracted_fields.get("total_amount", {})
            if amount_field.get("value"):
                try:
                    amount = float(amount_field["value"])
                except:
                    pass
            
            # Validate against limits
            limit_check = self._check_expense_limits(determined_category, amount)
            
            return {
                "success": True,
                "category": determined_category,
                "confidence": confidence,
                "amount": amount,
                "limit_check": limit_check,
                "merchant_name": merchant_name
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_expense_limits(self, category: str, amount: float) -> Dict[str, Any]:
        """Check of bedrag binnen expense limits valt"""
        limit = self.expense_limits.get(category, self.expense_limits["other"])
        
        return {
            "within_limit": amount <= limit,
            "amount": amount,
            "limit": limit,
            "percentage": (amount / limit * 100) if limit > 0 else 100,
            "requires_justification": amount > limit
        }
    
    async def _generate_expense_proposal(self, 
                                       receipt_data: Dict[str, Any],
                                       categorization: Dict[str, Any],
                                       user_id: str,
                                       metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Genereer expense declaration proposal"""
        try:
            extracted_fields = receipt_data.get("extracted_fields", {})
            
            proposal = {
                "expense_id": f"EXP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}",
                "user_id": user_id,
                "category": categorization.get("category", "other"),
                "amount": categorization.get("amount", 0.0),
                "currency": "EUR",  # Default, could be extracted
                "merchant": categorization.get("merchant_name", "Onbekend"),
                "description": self._generate_expense_description(categorization, extracted_fields),
                "date": self._extract_expense_date(extracted_fields),
                "location": self._extract_location(extracted_fields, metadata),
                "project_code": metadata.get("project_code") if metadata else None,
                "cost_center": metadata.get("cost_center") if metadata else None,
                "receipt_details": {
                    "confidence_score": receipt_data.get("confidence_score", 0.0),
                    "merchant_address": extracted_fields.get("merchant_address", {}).get("value"),
                    "transaction_time": extracted_fields.get("transaction_time", {}).get("value")
                },
                "compliance": {
                    "within_policy": categorization.get("limit_check", {}).get("within_limit", False),
                    "requires_justification": categorization.get("limit_check", {}).get("requires_justification", True),
                    "policy_limit": categorization.get("limit_check", {}).get("limit", 0.0)
                }
            }
            
            return {
                "success": True,
                "proposal": proposal
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_expense_description(self, categorization: Dict[str, Any], extracted_fields: Dict[str, Any]) -> str:
        """Genereer expense description"""
        category = categorization.get("category", "other")
        merchant = categorization.get("merchant_name", "")
        amount = categorization.get("amount", 0.0)
        
        # Category-specific descriptions
        descriptions = {
            "fuel": f"Brandstofkosten bij {merchant}",
            "food": f"Maaltijd/catering bij {merchant}",
            "transport": f"Transport/reiskosten bij {merchant}",
            "accommodation": f"Accommodatie bij {merchant}",
            "supplies": f"Kantoorbenodigdheden bij {merchant}",
            "other": f"Overige kosten bij {merchant}"
        }
        
        base_description = descriptions.get(category, f"Expense bij {merchant}")
        
        return f"{base_description} - €{amount:.2f}"
    
    def _extract_expense_date(self, extracted_fields: Dict[str, Any]) -> str:
        """Extract expense date van receipt"""
        transaction_date = extracted_fields.get("transaction_date", {}).get("value")
        
        if transaction_date:
            return transaction_date
        else:
            # Fallback naar vandaag
            return datetime.utcnow().strftime("%Y-%m-%d")
    
    def _extract_location(self, extracted_fields: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> str:
        """Extract/determine location"""
        # From metadata if provided
        if metadata and metadata.get("location"):
            return metadata["location"]
        
        # From merchant address
        merchant_address = extracted_fields.get("merchant_address", {}).get("value")
        if merchant_address:
            # Extract city from address (simplified)
            return merchant_address.split(",")[-1].strip() if "," in merchant_address else merchant_address
        
        return "Onbekend"
    
    async def _determine_approval_workflow(self, proposal: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Bepaal approval workflow voor expense"""
        try:
            if not proposal:
                return {"status": "error", "error": "Geen proposal beschikbaar"}
            
            amount = proposal.get("amount", 0.0)
            within_policy = proposal.get("compliance", {}).get("within_policy", False)
            
            # Approval logic
            if amount <= 25.0 and within_policy:
                status = "auto_approved"
                approver = "system"
                requires_review = False
            elif amount <= 100.0 and within_policy:
                status = "manager_approval"
                approver = "direct_manager"
                requires_review = True
            else:
                status = "finance_approval"
                approver = "finance_team"
                requires_review = True
            
            return {
                "status": status,
                "approver": approver,
                "requires_review": requires_review,
                "approval_deadline": self._calculate_approval_deadline(),
                "workflow_rules": {
                    "amount_threshold": amount,
                    "within_policy": within_policy,
                    "auto_approve_limit": 25.0
                }
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _calculate_approval_deadline(self) -> str:
        """Bereken approval deadline"""
        from datetime import timedelta
        deadline = datetime.utcnow() + timedelta(days=7)  # 7 dagen voor approval
        return deadline.strftime("%Y-%m-%d")
    
    async def get_user_expense_summary(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Verkrijg expense summary voor gebruiker"""
        try:
            # In productie uit database
            return {
                "user_id": user_id,
                "period_days": days,
                "total_expenses": 0.0,
                "expense_count": 0,
                "by_category": {},
                "pending_approvals": 0,
                "rejected_count": 0,
                "compliance_score": 100.0
            }
            
        except Exception as e:
            logger.error(f"Fout bij ophalen expense summary: {e}")
            return {"error": str(e)}
    
    async def process_expense_approval(self, expense_id: str, approver_id: str, decision: str, comments: str = "") -> Dict[str, Any]:
        """Verwerk expense approval decision"""
        try:
            if decision not in ["approved", "rejected", "needs_info"]:
                return {"success": False, "error": "Ongeldige approval decision"}
            
            # In productie zou dit database updates doen
            approval_result = {
                "expense_id": expense_id,
                "approver_id": approver_id,
                "decision": decision,
                "comments": comments,
                "approved_at": datetime.utcnow().isoformat(),
                "success": True
            }
            
            # Trigger volgende stap in workflow
            if decision == "approved":
                # Zou ERP booking trigger kunnen zijn
                approval_result["next_step"] = "erp_booking"
            elif decision == "rejected":
                approval_result["next_step"] = "notify_user"
            
            return approval_result
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Singleton instance
_receipt_agent_instance: Optional[ReceiptProcessingAgent] = None

def get_receipt_agent() -> ReceiptProcessingAgent:
    """Verkrijg singleton instance van ReceiptProcessingAgent"""
    global _receipt_agent_instance
    if _receipt_agent_instance is None:
        _receipt_agent_instance = ReceiptProcessingAgent()
    return _receipt_agent_instance
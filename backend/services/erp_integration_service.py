"""
ERP Integration Service voor Hoeflon AI Portal
Koppelt verwerkte documenten aan Ridder ERP systeem
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json
import pyodbc

from ..core.config import get_config
from ..database.connections import RidderDatabaseManager

logger = logging.getLogger(__name__)


class ERPIntegrationService:
    """
    Service voor integratie met Ridder ERP systeem
    Verwerkt facturen en declaraties naar ERP boekingen
    """
    
    def __init__(self):
        self.ridder_db = RidderDatabaseManager()
        self.config = get_config("database")
    
    async def create_invoice_booking(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creëer boekingsvoorstel voor factuur in Ridder ERP
        
        Args:
            invoice_data: Verwerkte factuur data
            
        Returns:
            Booking result met ERP referenties
        """
        try:
            logger.info(f"Creating ERP booking voor factuur {invoice_data.get('invoice_number')}")
            
            # Extract required fields
            supplier_name = invoice_data.get("supplier_name")
            invoice_number = invoice_data.get("invoice_number")
            total_amount = float(invoice_data.get("total_amount", 0))
            invoice_date = invoice_data.get("invoice_date")
            
            # Validate required fields
            if not all([supplier_name, invoice_number, total_amount > 0]):
                return {
                    "success": False,
                    "error": "Ontbrekende vereiste velden voor ERP booking"
                }
            
            # Check for duplicate invoices
            duplicate_check = await self._check_duplicate_invoice(supplier_name, invoice_number)
            if duplicate_check["is_duplicate"]:
                return {
                    "success": False,
                    "error": f"Duplicate factuur gevonden: {duplicate_check['existing_reference']}"
                }
            
            # Get or create supplier
            supplier_result = await self._get_or_create_supplier(supplier_name, invoice_data)
            if not supplier_result["success"]:
                return supplier_result
            
            supplier_code = supplier_result["supplier_code"]
            
            # Generate booking proposal
            booking_proposal = {
                "transaction_type": "PURCHASE_INVOICE",
                "supplier_code": supplier_code,
                "invoice_number": invoice_number,
                "invoice_date": invoice_date,
                "total_amount": total_amount,
                "currency": invoice_data.get("currency", "EUR"),
                "account_code": invoice_data.get("account_code", "4000"),
                "cost_center": invoice_data.get("cost_center", "ADMIN"),
                "project_code": invoice_data.get("project_code"),
                "description": f"Factuur {invoice_number} van {supplier_name}",
                "payment_terms": invoice_data.get("payment_terms", 30),
                "created_by": "AI_SYSTEM",
                "created_at": datetime.utcnow().isoformat(),
                "requires_approval": invoice_data.get("requires_approval", False)
            }
            
            # In productie zou hier de werkelijke ERP API call zijn
            # Voor nu simuleren we het booking process
            
            erp_reference = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{len(invoice_number):04d}"
            
            return {
                "success": True,
                "erp_reference": erp_reference,
                "supplier_code": supplier_code,
                "booking_proposal": booking_proposal,
                "requires_approval": booking_proposal["requires_approval"],
                "next_steps": self._determine_next_steps(booking_proposal)
            }
            
        except Exception as e:
            logger.error(f"Fout bij ERP invoice booking: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_expense_booking(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creëer boekingsvoorstel voor declaratie in Ridder ERP
        
        Args:
            expense_data: Verwerkte expense data
            
        Returns:
            Booking result met ERP referenties
        """
        try:
            logger.info(f"Creating ERP booking voor expense {expense_data.get('expense_id')}")
            
            user_id = expense_data.get("user_id")
            amount = float(expense_data.get("amount", 0))
            category = expense_data.get("category", "other")
            
            if not all([user_id, amount > 0]):
                return {
                    "success": False,
                    "error": "Ontbrekende vereiste velden voor expense booking"
                }
            
            # Get employee info
            employee_info = await self._get_employee_info(user_id)
            if not employee_info["success"]:
                return employee_info
            
            # Map expense category to account code
            account_mapping = {
                "fuel": "4210",      # Brandstofkosten
                "food": "4220",      # Representatiekosten
                "transport": "4230", # Reiskosten
                "accommodation": "4240", # Hotelkosten
                "supplies": "4300",  # Kantoorkosten
                "other": "4900"      # Overige kosten
            }
            
            account_code = account_mapping.get(category, "4900")
            
            booking_proposal = {
                "transaction_type": "EXPENSE_CLAIM",
                "employee_code": employee_info["employee_code"],
                "expense_id": expense_data.get("expense_id"),
                "amount": amount,
                "currency": expense_data.get("currency", "EUR"),
                "account_code": account_code,
                "cost_center": expense_data.get("cost_center", employee_info.get("cost_center", "ADMIN")),
                "project_code": expense_data.get("project_code"),
                "description": expense_data.get("description", f"Declaratie {category}"),
                "expense_date": expense_data.get("date"),
                "merchant": expense_data.get("merchant"),
                "location": expense_data.get("location"),
                "created_by": "AI_SYSTEM",
                "created_at": datetime.utcnow().isoformat(),
                "approval_status": expense_data.get("approval_status", "pending")
            }
            
            erp_reference = f"EXP-{datetime.utcnow().strftime('%Y%m%d')}-{expense_data.get('expense_id', 'XXXX')[-8:]}"
            
            return {
                "success": True,
                "erp_reference": erp_reference,
                "employee_code": employee_info["employee_code"],
                "booking_proposal": booking_proposal,
                "requires_approval": expense_data.get("approval_status") != "auto_approved",
                "next_steps": ["awaiting_approval" if booking_proposal["approval_status"] == "pending" else "ready_for_payment"]
            }
            
        except Exception as e:
            logger.error(f"Fout bij ERP expense booking: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _check_duplicate_invoice(self, supplier_name: str, invoice_number: str) -> Dict[str, Any]:
        """Check voor duplicate facturen"""
        try:
            # In productie zou dit een database query zijn naar bestaande facturen
            # Voor nu simuleren we geen duplicates
            
            return {
                "is_duplicate": False,
                "existing_reference": None
            }
            
        except Exception as e:
            logger.error(f"Fout bij duplicate check: {e}")
            return {
                "is_duplicate": False,
                "error": str(e)
            }
    
    async def _get_or_create_supplier(self, supplier_name: str, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verkrijg of creëer leverancier in ERP systeem"""
        try:
            # Normalize supplier name voor lookup
            normalized_name = supplier_name.upper().strip()
            
            # In productie zou dit een database lookup zijn
            # Voor nu genereren we een supplier code
            
            # Simple mapping van bekende leveranciers
            known_suppliers = {
                "SHELL": "SHELL001",
                "BP": "BP001", 
                "TOTAL": "TOTAL001",
                "OFFICE DEPOT": "OFFICE001",
                "STAPLES": "STAPLES001"
            }
            
            supplier_code = None
            for known, code in known_suppliers.items():
                if known in normalized_name:
                    supplier_code = code
                    break
            
            if not supplier_code:
                # Generate new supplier code
                supplier_code = f"SUP{len(normalized_name):03d}{datetime.utcnow().strftime('%m%d')}"
            
            return {
                "success": True,
                "supplier_code": supplier_code,
                "supplier_name": supplier_name,
                "is_new": supplier_code not in known_suppliers.values()
            }
            
        except Exception as e:
            logger.error(f"Fout bij supplier lookup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_employee_info(self, user_id: str) -> Dict[str, Any]:
        """Verkrijg employee informatie voor expense booking"""
        try:
            # In productie zou dit een lookup zijn in HR database/Azure AD
            # Voor nu een placeholder implementatie
            
            # Generate employee code gebaseerd op user_id
            employee_code = f"EMP{user_id[-4:].upper()}"
            
            return {
                "success": True,
                "employee_code": employee_code,
                "user_id": user_id,
                "cost_center": "ADMIN",  # Default cost center
                "department": "General"
            }
            
        except Exception as e:
            logger.error(f"Fout bij employee lookup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _determine_next_steps(self, booking_proposal: Dict[str, Any]) -> List[str]:
        """Bepaal volgende stappen in workflow"""
        next_steps = []
        
        if booking_proposal.get("requires_approval"):
            next_steps.append("awaiting_approval")
        else:
            next_steps.append("ready_for_posting")
        
        if booking_proposal.get("project_code"):
            next_steps.append("project_allocation")
        
        return next_steps
    
    async def get_pending_approvals(self, approver_user_id: str) -> Dict[str, Any]:
        """Verkrijg pending approvals voor gebruiker"""
        try:
            # In productie uit approval workflow database
            return {
                "approver_id": approver_user_id,
                "pending_invoices": [],
                "pending_expenses": [],
                "total_amount": 0.0,
                "oldest_pending": None
            }
            
        except Exception as e:
            logger.error(f"Fout bij ophalen pending approvals: {e}")
            return {"error": str(e)}
    
    async def process_approval(self, 
                             approval_type: str,  # invoice, expense
                             reference_id: str,
                             approver_id: str,
                             decision: str,
                             comments: str = "") -> Dict[str, Any]:
        """Process approval decision"""
        try:
            if decision not in ["approved", "rejected"]:
                return {
                    "success": False,
                    "error": "Invalid approval decision"
                }
            
            # In productie zou dit approval workflow updates doen
            approval_result = {
                "success": True,
                "approval_type": approval_type,
                "reference_id": reference_id,
                "approver_id": approver_id,
                "decision": decision,
                "comments": comments,
                "approved_at": datetime.utcnow().isoformat()
            }
            
            if decision == "approved":
                approval_result["next_step"] = "posting_to_erp"
            else:
                approval_result["next_step"] = "notification_sent"
            
            return approval_result
            
        except Exception as e:
            logger.error(f"Fout bij approval processing: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_integration_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Verkrijg ERP integratie statistieken"""
        try:
            # In productie uit integration logging database
            return {
                "period_days": days,
                "invoices_processed": 0,
                "expenses_processed": 0,
                "success_rate": 100.0,
                "average_processing_time": 0.0,
                "pending_approvals": 0,
                "error_count": 0,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Fout bij integration statistics: {e}")
            return {"error": str(e)}


# Singleton instance
_erp_integration_instance: Optional[ERPIntegrationService] = None

def get_erp_integration_service() -> ERPIntegrationService:
    """Verkrijg singleton instance van ERPIntegrationService"""
    global _erp_integration_instance
    if _erp_integration_instance is None:
        _erp_integration_instance = ERPIntegrationService()
    return _erp_integration_instance
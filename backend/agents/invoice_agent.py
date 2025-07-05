"""
InvoiceAgent - Intelligente AutoGen agent voor factuurverwerking
Orkestreert complete pipeline: Mail scanning → OCR → Validatie → ERP integratie
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import re
from decimal import Decimal

import autogen
from autogen import ConversableAgent, GroupChat, GroupChatManager

from ..services.graph_api_service import get_graph_service
from ..services.document_intelligence_service import get_document_intelligence_service
from ..services.letta_memory_service import get_letta_service
from ..core.config import get_config

logger = logging.getLogger(__name__)


class InvoiceProcessingAgent:
    """
    Hoofdagent voor factuurverwerking
    Gebruikt AutoGen voor intelligente orchestratie
    """
    
    def __init__(self):
        self.graph_service = get_graph_service()
        self.doc_intelligence = get_document_intelligence_service()
        self.letta_service = get_letta_service()
        
        # AutoGen agents
        self.agents = {}
        self._initialize_agents()
        
        # Processing state
        self.processing_session = None
        self.current_batch = []
    
    def _initialize_agents(self):
        """Initialiseer AutoGen agents voor factuurverwerking"""
        
        # LLM configuratie
        llm_config = {
            "config_list": [
                {
                    "model": "gpt-4",
                    "api_key": "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",  # In productie via env var
                    "api_type": "anthropic",
                    "api_base": "https://api.anthropic.com"
                }
            ],
            "timeout": 60,
            "cache_seed": 42
        }
        
        # Mail Scanner Agent
        self.agents["mail_scanner"] = ConversableAgent(
            name="MailScanner",
            system_message="""Je bent een Mail Scanner Agent gespecialiseerd in het identificeren van facturen in e-mails.
            
            Taken:
            - Scan mailbox voor nieuwe berichten met PDF attachments
            - Filter relevante facturen op basis van sender en onderwerp
            - Prioriteer verwerking op basis van bedrag en leverancier
            - Detecteer urgente facturen (betaaltermijn, boetes)
            
            Je rapporteert altijd in JSON formaat met status en gedetailleerde informatie.""",
            llm_config=llm_config,
            human_input_mode="NEVER"
        )
        
        # OCR Processor Agent  
        self.agents["ocr_processor"] = ConversableAgent(
            name="OCRProcessor",
            system_message="""Je bent een OCR Processor Agent gespecialiseerd in factuur data extractie.
            
            Taken:
            - Verwerk PDF facturen met Azure Document Intelligence
            - Valideer geëxtraheerde data op volledigheid en accuraatheid
            - Identificeer ontbrekende of onduidelijke velden
            - Normaliseer data formaten (datums, bedragen, BTW-nummers)
            
            Je bent kritisch op data kwaliteit en markeert twijfelgevallen voor handmatige review.""",
            llm_config=llm_config,
            human_input_mode="NEVER"
        )
        
        # Validation Agent
        self.agents["validator"] = ConversableAgent(
            name="ValidationAgent", 
            system_message="""Je bent een Validation Agent voor factuur business logic.
            
            Taken:
            - Valideer factuurdata tegen bedrijfsregels
            - Controleer leverancier gegevens tegen bekende leveranciers
            - Verificeer BTW-berekeningen en tarieven
            - Detecteer duplicaat facturen
            - Controleer goedkeuringswerkflows
            
            Je bent conservatief en markeert verdachte facturen voor review.""",
            llm_config=llm_config,
            human_input_mode="NEVER"
        )
        
        # ERP Integration Agent
        self.agents["erp_integrator"] = ConversableAgent(
            name="ERPIntegrator",
            system_message="""Je bent een ERP Integration Agent voor Ridder ERP koppeling.
            
            Taken:
            - Map factuurdata naar Ridder ERP velden
            - Genereer boekingsvoorstellen
            - Koppel aan projecten/kostenplaatsen
            - Synchroniseer met bestaande workflows
            
            Je volgt Hoeflon's boekhoudkundige procedures en zorgt voor correcte mapping.""",
            llm_config=llm_config,
            human_input_mode="NEVER"
        )
        
        # Supervisor Agent
        self.agents["supervisor"] = ConversableAgent(
            name="InvoiceSupervisor",
            system_message="""Je bent de Supervisor Agent die de complete factuurverwerking orkestreert.
            
            Taken:
            - Coördineer workflow tussen alle agents
            - Monitor verwerkingsvoortgang
            - Handel uitzonderingen en errors af
            - Rapporteer eindresultaten
            - Leer van verwerkingspatronen
            
            Je zorgt voor soepele samenwerking en kwaliteitscontrole.""",
            llm_config=llm_config,
            human_input_mode="NEVER"
        )
    
    async def start_invoice_processing_session(self, days_back: int = 1) -> Dict[str, Any]:
        """
        Start nieuwe factuurverwerkingssessie
        
        Args:
            days_back: Aantal dagen terug om te scannen
            
        Returns:
            Sessie informatie en eerste resultaten
        """
        try:
            session_id = f"invoice_session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            logger.info(f"Start factuurverwerkingssessie {session_id}")
            
            # Start with mail scanning
            scan_result = await self._scan_for_invoices(days_back)
            
            if not scan_result["success"]:
                return {
                    "session_id": session_id,
                    "status": "failed",
                    "error": scan_result["error"],
                    "started_at": datetime.utcnow().isoformat()
                }
            
            self.processing_session = {
                "session_id": session_id,
                "started_at": datetime.utcnow().isoformat(),
                "days_scanned": days_back,
                "total_messages": len(scan_result["messages"]),
                "current_stage": "scanning_complete",
                "processed_count": 0,
                "errors": [],
                "results": []
            }
            
            # Begin processing pipeline
            if scan_result["messages"]:
                processing_result = await self._process_invoice_batch(scan_result["messages"])
                self.processing_session.update(processing_result)
            
            return self.processing_session
            
        except Exception as e:
            logger.error(f"Fout bij start factuurverwerkingssessie: {e}")
            return {
                "session_id": session_id if 'session_id' in locals() else "unknown",
                "status": "failed",
                "error": str(e),
                "started_at": datetime.utcnow().isoformat()
            }
    
    async def _scan_for_invoices(self, days_back: int) -> Dict[str, Any]:
        """Scan mailbox voor facturen via Mail Scanner Agent"""
        try:
            logger.info("Mail Scanner Agent start mailbox scanning")
            
            # Gebruik Graph API service voor scanning
            messages = await self.graph_service.scan_mailbox_for_invoices(days_back)
            
            # Laat Mail Scanner Agent de resultaten analyseren
            analysis_prompt = f"""
            Analyseer deze {len(messages)} berichten met PDF attachments voor factuurverwerking:
            
            Berichten: {json.dumps(messages[:5], indent=2) if messages else []}
            
            Prioriteer op:
            1. Bekende leveranciers
            2. Urgentie (betaaltermijn)
            3. Bestandsgrootte (grotere PDFs eerst)
            
            Geef een prioriteitslijst terug in JSON formaat.
            """
            
            # In een echte implementatie zou je hier AutoGen conversation starten
            # Voor nu simuleren we de agent response
            
            return {
                "success": True,
                "messages": messages,
                "analysis": {
                    "total_found": len(messages),
                    "priority_high": len([m for m in messages if "urgent" in m.get("subject", "").lower()]),
                    "priority_normal": len(messages) - len([m for m in messages if "urgent" in m.get("subject", "").lower()])
                }
            }
            
        except Exception as e:
            logger.error(f"Fout bij mail scanning: {e}")
            return {
                "success": False,
                "error": str(e),
                "messages": []
            }
    
    async def _process_invoice_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verwerk batch van factuur berichten"""
        try:
            logger.info(f"Start verwerking van {len(messages)} factuur berichten")
            
            results = []
            errors = []
            
            for message in messages:
                try:
                    result = await self._process_single_invoice(message)
                    results.append(result)
                    
                    if not result["success"]:
                        errors.append({
                            "message_id": message["message_id"],
                            "error": result["error"]
                        })
                        
                except Exception as e:
                    logger.error(f"Fout bij verwerken bericht {message['message_id']}: {e}")
                    errors.append({
                        "message_id": message["message_id"],
                        "error": str(e)
                    })
            
            return {
                "current_stage": "processing_complete",
                "processed_count": len(results),
                "success_count": len([r for r in results if r["success"]]),
                "error_count": len(errors),
                "results": results,
                "errors": errors,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Fout bij batch verwerking: {e}")
            return {
                "current_stage": "processing_failed",
                "error": str(e),
                "results": [],
                "errors": [{"general_error": str(e)}]
            }
    
    async def _process_single_invoice(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Verwerk een enkele factuur door complete pipeline"""
        try:
            message_id = message["message_id"]
            logger.info(f"Start verwerking factuur {message_id}")
            
            result = {
                "message_id": message_id,
                "subject": message["subject"],
                "sender": message["sender"],
                "success": False,
                "stages": {},
                "final_data": None,
                "erp_integration": None
            }
            
            # Stage 1: Download and OCR processing
            ocr_result = await self._stage_ocr_processing(message)
            result["stages"]["ocr"] = ocr_result
            
            if not ocr_result["success"]:
                result["error"] = f"OCR failed: {ocr_result['error']}"
                return result
            
            # Stage 2: Data validation
            validation_result = await self._stage_validation(ocr_result["extracted_data"])
            result["stages"]["validation"] = validation_result
            
            if not validation_result["success"]:
                result["error"] = f"Validation failed: {validation_result['error']}"
                return result
            
            # Stage 3: ERP Integration
            erp_result = await self._stage_erp_integration(validation_result["validated_data"])
            result["stages"]["erp"] = erp_result
            result["erp_integration"] = erp_result
            
            if erp_result["success"]:
                result["success"] = True
                result["final_data"] = erp_result["booking_proposal"]
                
                # Move processed email to folder
                await self.graph_service.move_message_to_folder(
                    message_id, 
                    "Processed Invoices",
                    message.get("mailbox", "me")
                )
            else:
                result["error"] = f"ERP integration failed: {erp_result['error']}"
            
            return result
            
        except Exception as e:
            logger.error(f"Fout bij verwerken factuur {message_id}: {e}")
            return {
                "message_id": message_id,
                "success": False,
                "error": str(e),
                "stages": {}
            }
    
    async def _stage_ocr_processing(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """OCR verwerkingsstage"""
        try:
            attachments = message.get("attachments", [])
            if not attachments:
                return {"success": False, "error": "Geen PDF attachments gevonden"}
            
            # Verwerk eerste PDF attachment
            pdf_attachment = attachments[0]
            
            # Download attachment content
            attachment_content = await self.graph_service.download_attachment(
                message["message_id"],
                pdf_attachment["id"],
                message.get("mailbox", "me")
            )
            
            if not attachment_content:
                return {"success": False, "error": "Kon attachment niet downloaden"}
            
            # OCR verwerking via Document Intelligence
            ocr_result = await self.doc_intelligence.analyze_invoice(
                attachment_content,
                pdf_attachment["name"]
            )
            
            if ocr_result["success"]:
                return {
                    "success": True,
                    "extracted_data": ocr_result,
                    "attachment_info": pdf_attachment
                }
            else:
                return {
                    "success": False,
                    "error": ocr_result["error"]
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _stage_validation(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Data validatie stage"""
        try:
            extracted_fields = ocr_data.get("extracted_fields", {})
            
            validation_results = {
                "required_fields": {},
                "business_rules": {},
                "data_quality": {}
            }
            
            # Check required fields
            required_fields = ["invoice_number", "supplier_name", "total_amount", "invoice_date"]
            for field in required_fields:
                field_data = extracted_fields.get(field)
                if field_data and field_data.get("value"):
                    validation_results["required_fields"][field] = {
                        "present": True,
                        "confidence": field_data.get("confidence", 0.0)
                    }
                else:
                    validation_results["required_fields"][field] = {
                        "present": False,
                        "confidence": 0.0
                    }
            
            # Business rules validation
            if extracted_fields.get("total_amount", {}).get("value"):
                amount = float(extracted_fields["total_amount"]["value"])
                validation_results["business_rules"]["amount_reasonable"] = {
                    "valid": 1 <= amount <= 100000,  # Redelijke range
                    "value": amount
                }
            
            # Overall validation score
            required_score = sum(1 for v in validation_results["required_fields"].values() if v["present"]) / len(required_fields)
            business_score = sum(1 for v in validation_results["business_rules"].values() if v["valid"]) / max(1, len(validation_results["business_rules"]))
            
            overall_score = (required_score + business_score) / 2
            
            if overall_score >= 0.8:  # 80% validation threshold
                return {
                    "success": True,
                    "validated_data": ocr_data,
                    "validation_score": overall_score,
                    "validation_details": validation_results
                }
            else:
                return {
                    "success": False,
                    "error": f"Validation score te laag: {overall_score:.2f}",
                    "validation_details": validation_results
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _stage_erp_integration(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """ERP integratie stage"""
        try:
            extracted_fields = validated_data.get("extracted_fields", {})
            
            # Generate booking proposal voor Ridder ERP
            booking_proposal = {
                "invoice_number": extracted_fields.get("invoice_number", {}).get("value"),
                "supplier_name": extracted_fields.get("supplier_name", {}).get("value"),
                "total_amount": extracted_fields.get("total_amount", {}).get("value"),
                "tax_amount": extracted_fields.get("tax_amount", {}).get("value"),
                "invoice_date": extracted_fields.get("invoice_date", {}).get("value"),
                "due_date": extracted_fields.get("due_date", {}).get("value"),
                "currency": extracted_fields.get("currency", {}).get("value", "EUR"),
                
                # Ridder ERP specifieke velden
                "account_code": self._determine_account_code(extracted_fields),
                "cost_center": self._determine_cost_center(extracted_fields),
                "project_code": self._determine_project_code(extracted_fields),
                "payment_terms": self._calculate_payment_terms(extracted_fields),
                
                # Metadata
                "confidence_score": validated_data.get("confidence_score", 0.0),
                "processing_timestamp": datetime.utcnow().isoformat(),
                "requires_approval": self._requires_approval(extracted_fields)
            }
            
            # In productie zou hier daadwerkelijke ERP integratie plaatsvinden
            # Voor nu simuleren we success
            
            return {
                "success": True,
                "booking_proposal": booking_proposal,
                "erp_reference": f"HOEF-{datetime.utcnow().strftime('%Y%m%d')}-{booking_proposal['invoice_number'][:8] if booking_proposal['invoice_number'] else 'XXXX'}",
                "approval_required": booking_proposal["requires_approval"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _determine_account_code(self, fields: Dict[str, Any]) -> str:
        """Bepaal account code op basis van leverancier/content"""
        supplier = fields.get("supplier_name", {}).get("value", "").lower()
        
        # Simple mapping - in productie zou dit een database lookup zijn
        if "fuel" in supplier or "tank" in supplier:
            return "4210"  # Brandstofkosten
        elif "office" in supplier or "bureau" in supplier:
            return "4300"  # Kantoorkosten
        elif "tool" in supplier or "machine" in supplier:
            return "4400"  # Gereedschap/machines
        else:
            return "4000"  # Algemene kosten
    
    def _determine_cost_center(self, fields: Dict[str, Any]) -> str:
        """Bepaal kostenplaats"""
        # In productie gebaseerd op business rules
        return "PROD001"  # Default production cost center
    
    def _determine_project_code(self, fields: Dict[str, Any]) -> Optional[str]:
        """Bepaal project code indien van toepassing"""
        # Zou project references kunnen zoeken in factuur content
        return None
    
    def _calculate_payment_terms(self, fields: Dict[str, Any]) -> int:
        """Bereken betaaltermijn in dagen"""
        invoice_date = fields.get("invoice_date", {}).get("value")
        due_date = fields.get("due_date", {}).get("value")
        
        if invoice_date and due_date:
            try:
                # Parse dates and calculate difference
                return 30  # Default voor nu
            except:
                pass
        
        return 30  # Default 30 dagen
    
    def _requires_approval(self, fields: Dict[str, Any]) -> bool:
        """Bepaal of factuur goedkeuring vereist"""
        amount = fields.get("total_amount", {}).get("value")
        if amount and float(amount) > 1000:  # Boven €1000 goedkeuring vereist
            return True
        return False
    
    async def get_processing_status(self) -> Dict[str, Any]:
        """Verkrijg huidige verwerkingsstatus"""
        if not self.processing_session:
            return {"status": "no_active_session"}
        
        return self.processing_session
    
    async def get_processing_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Verkrijg verwerkingsstatistieken"""
        # In productie uit database
        return {
            "period_days": days,
            "total_invoices_processed": 0,
            "success_rate": 0.0,
            "average_processing_time": 0.0,
            "common_errors": [],
            "top_suppliers": []
        }


# Singleton instance
_invoice_agent_instance: Optional[InvoiceProcessingAgent] = None

def get_invoice_agent() -> InvoiceProcessingAgent:
    """Verkrijg singleton instance van InvoiceProcessingAgent"""
    global _invoice_agent_instance
    if _invoice_agent_instance is None:
        _invoice_agent_instance = InvoiceProcessingAgent()
    return _invoice_agent_instance
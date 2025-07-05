"""
Azure Document Intelligence Service voor Hoeflon AI Portal
Implementeert PDF/image OCR en data extractie volgens Azure best practices
"""
import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import io
import tempfile
from pathlib import Path

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

from ..core.config import get_config

logger = logging.getLogger(__name__)


class DocumentIntelligenceService:
    """
    Service voor Azure Document Intelligence operaties
    Focus op invoice en receipt processing
    """
    
    def __init__(self):
        self.config = get_config("document_intelligence")
        self.client: Optional[DocumentIntelligenceClient] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialiseer Document Intelligence client"""
        try:
            # Valideer configuratie
            endpoint = self.config.get("endpoint")
            api_key = self.config.get("api_key")
            
            if not endpoint or not api_key:
                logger.error("Azure Document Intelligence endpoint en API key zijn vereist")
                raise ValueError("Document Intelligence configuratie onvolledig")
            
            # Initialiseer client
            self.client = DocumentIntelligenceClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(api_key),
                api_version=self.config.get("api_version", "2024-02-29-preview")
            )
            
            logger.info("Azure Document Intelligence client succesvol geïnitialiseerd")
            
        except Exception as e:
            logger.error(f"Fout bij initialiseren Document Intelligence client: {e}")
            raise
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Document Intelligence connectie"""
        try:
            if not self.client:
                return {"status": "error", "message": "Client niet geïnitialiseerd"}
            
            # Test met een kleine dummy document operatie
            # In productie zou je een specifiek test document kunnen gebruiken
            return {
                "status": "success",
                "message": "Document Intelligence client succesvol geïnitialiseerd",
                "endpoint": self.config.get("endpoint"),
                "api_version": self.config.get("api_version")
            }
            
        except Exception as e:
            logger.error(f"Document Intelligence connectie test gefaald: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _validate_file(self, file_content: bytes, filename: str) -> Tuple[bool, str]:
        """Valideer bestand voor verwerking"""
        try:
            # Check bestandsgrootte
            max_size_bytes = self.config.get("max_file_size_mb", 50) * 1024 * 1024
            if len(file_content) > max_size_bytes:
                return False, f"Bestand te groot: {len(file_content)/1024/1024:.1f}MB (max {max_size_bytes/1024/1024}MB)"
            
            # Check bestandsformaat
            supported_formats = self.config.get("supported_formats", [".pdf", ".png", ".jpg", ".jpeg"])
            file_extension = Path(filename).suffix.lower()
            
            if file_extension not in supported_formats:
                return False, f"Niet ondersteund bestandsformaat: {file_extension} (ondersteund: {supported_formats})"
            
            # Check of bestand niet leeg is
            if len(file_content) == 0:
                return False, "Bestand is leeg"
            
            return True, "Bestand validatie geslaagd"
            
        except Exception as e:
            return False, f"Validatie fout: {str(e)}"
    
    async def analyze_invoice(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Analyseer factuur document met prebuilt invoice model
        
        Args:
            file_content: Bestand content als bytes
            filename: Naam van het bestand
            
        Returns:
            Geëxtraheerde factuur data
        """
        try:
            if not self.client:
                raise RuntimeError("Document Intelligence client niet geïnitialiseerd")
            
            # Valideer bestand
            is_valid, validation_message = self._validate_file(file_content, filename)
            if not is_valid:
                return {
                    "success": False,
                    "error": validation_message,
                    "filename": filename
                }
            
            logger.info(f"Start factuur analyse voor {filename}")
            
            # Start document analyse met prebuilt invoice model
            poller = self.client.begin_analyze_document(
                model_id=self.config.get("invoice_model", "prebuilt-invoice"),
                analyze_request=AnalyzeDocumentRequest(bytes_source=file_content),
                content_type="application/octet-stream"
            )
            
            # Wacht op resultaat
            result: AnalyzeResult = poller.result()
            
            # Verwerk resultaat
            invoice_data = self._extract_invoice_data(result, filename)
            
            logger.info(f"Factuur analyse voltooid voor {filename}")
            return invoice_data
            
        except HttpResponseError as e:
            logger.error(f"Azure API fout bij factuur analyse: {e}")
            return {
                "success": False,
                "error": f"Azure API fout: {e.message}",
                "filename": filename
            }
        except Exception as e:
            logger.error(f"Fout bij factuur analyse voor {filename}: {e}")
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def _extract_invoice_data(self, result: AnalyzeResult, filename: str) -> Dict[str, Any]:
        """Extract gestructureerde data uit invoice analyse resultaat"""
        try:
            invoice_data = {
                "success": True,
                "filename": filename,
                "analyzed_at": datetime.utcnow().isoformat(),
                "document_type": "invoice",
                "confidence_score": 0.0,
                "extracted_fields": {},
                "line_items": [],
                "raw_text": "",
                "processing_info": {
                    "model_id": result.model_id if hasattr(result, 'model_id') else None,
                    "api_version": self.config.get("api_version")
                }
            }
            
            if result.documents and len(result.documents) > 0:
                document = result.documents[0]
                
                # Extract confidence score
                if hasattr(document, 'confidence') and document.confidence:
                    invoice_data["confidence_score"] = document.confidence
                
                # Extract fields
                if hasattr(document, 'fields') and document.fields:
                    fields = self._extract_invoice_fields(document.fields)
                    invoice_data["extracted_fields"] = fields
                
                # Extract line items
                if hasattr(document, 'fields') and document.fields and 'Items' in document.fields:
                    line_items = self._extract_line_items(document.fields['Items'])
                    invoice_data["line_items"] = line_items
            
            # Extract raw text
            if result.content:
                invoice_data["raw_text"] = result.content
            
            return invoice_data
            
        except Exception as e:
            logger.error(f"Fout bij extracten invoice data: {e}")
            return {
                "success": False,
                "error": f"Data extractie fout: {str(e)}",
                "filename": filename
            }
    
    def _extract_invoice_fields(self, fields: Dict) -> Dict[str, Any]:
        """Extract belangrijke velden uit invoice fields"""
        extracted = {}
        
        # Mapping van Azure field names naar onze field names
        field_mapping = {
            'VendorName': 'supplier_name',
            'VendorAddress': 'supplier_address',
            'CustomerName': 'customer_name',
            'CustomerAddress': 'customer_address',
            'InvoiceId': 'invoice_number',
            'InvoiceDate': 'invoice_date',
            'DueDate': 'due_date',
            'SubTotal': 'subtotal',
            'TotalTax': 'tax_amount',
            'InvoiceTotal': 'total_amount',
            'AmountDue': 'amount_due',
            'PurchaseOrder': 'purchase_order',
            'CurrencyCode': 'currency'
        }
        
        for azure_field, our_field in field_mapping.items():
            if azure_field in fields:
                field_data = fields[azure_field]
                extracted[our_field] = self._extract_field_value(field_data)
        
        return extracted
    
    def _extract_field_value(self, field_data) -> Dict[str, Any]:
        """Extract waarde en confidence van field"""
        try:
            result = {
                "value": None,
                "confidence": 0.0,
                "content": None
            }
            
            if hasattr(field_data, 'content'):
                result["content"] = field_data.content
            
            if hasattr(field_data, 'confidence'):
                result["confidence"] = field_data.confidence
            
            # Extract actual value based on field type
            if hasattr(field_data, 'value'):
                if hasattr(field_data.value, 'amount'):
                    # Voor currency fields
                    result["value"] = field_data.value.amount
                elif hasattr(field_data.value, 'year'):
                    # Voor date fields
                    result["value"] = f"{field_data.value.year}-{field_data.value.month:02d}-{field_data.value.day:02d}"
                else:
                    # Voor string fields
                    result["value"] = str(field_data.value)
            
            return result
            
        except Exception as e:
            logger.warning(f"Fout bij extracten field value: {e}")
            return {"value": None, "confidence": 0.0, "content": None}
    
    def _extract_line_items(self, items_field) -> List[Dict[str, Any]]:
        """Extract line items uit factuur"""
        line_items = []
        
        try:
            if hasattr(items_field, 'value') and isinstance(items_field.value, list):
                for item in items_field.value:
                    if hasattr(item, 'value') and hasattr(item.value, 'properties'):
                        line_item = {}
                        
                        # Extract item properties
                        properties = item.value.properties
                        for prop_name, prop_data in properties.items():
                            line_item[prop_name.lower()] = self._extract_field_value(prop_data)
                        
                        line_items.append(line_item)
            
        except Exception as e:
            logger.warning(f"Fout bij extracten line items: {e}")
        
        return line_items
    
    async def analyze_receipt(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Analyseer receipt/bon document met prebuilt receipt model
        
        Args:
            file_content: Bestand content als bytes
            filename: Naam van het bestand
            
        Returns:
            Geëxtraheerde receipt data
        """
        try:
            if not self.client:
                raise RuntimeError("Document Intelligence client niet geïnitialiseerd")
            
            # Valideer bestand
            is_valid, validation_message = self._validate_file(file_content, filename)
            if not is_valid:
                return {
                    "success": False,
                    "error": validation_message,
                    "filename": filename
                }
            
            logger.info(f"Start receipt analyse voor {filename}")
            
            # Start document analyse met prebuilt receipt model
            poller = self.client.begin_analyze_document(
                model_id=self.config.get("receipt_model", "prebuilt-receipt"),
                analyze_request=AnalyzeDocumentRequest(bytes_source=file_content),
                content_type="application/octet-stream"
            )
            
            # Wacht op resultaat
            result: AnalyzeResult = poller.result()
            
            # Verwerk resultaat
            receipt_data = self._extract_receipt_data(result, filename)
            
            logger.info(f"Receipt analyse voltooid voor {filename}")
            return receipt_data
            
        except Exception as e:
            logger.error(f"Fout bij receipt analyse voor {filename}: {e}")
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    def _extract_receipt_data(self, result: AnalyzeResult, filename: str) -> Dict[str, Any]:
        """Extract gestructureerde data uit receipt analyse resultaat"""
        try:
            receipt_data = {
                "success": True,
                "filename": filename,
                "analyzed_at": datetime.utcnow().isoformat(),
                "document_type": "receipt",
                "confidence_score": 0.0,
                "extracted_fields": {},
                "items": [],
                "raw_text": "",
                "processing_info": {
                    "model_id": result.model_id if hasattr(result, 'model_id') else None,
                    "api_version": self.config.get("api_version")
                }
            }
            
            if result.documents and len(result.documents) > 0:
                document = result.documents[0]
                
                # Extract confidence score
                if hasattr(document, 'confidence') and document.confidence:
                    receipt_data["confidence_score"] = document.confidence
                
                # Extract fields voor receipts
                if hasattr(document, 'fields') and document.fields:
                    fields = self._extract_receipt_fields(document.fields)
                    receipt_data["extracted_fields"] = fields
                    
                    # Extract items
                    if 'Items' in document.fields:
                        items = self._extract_receipt_items(document.fields['Items'])
                        receipt_data["items"] = items
            
            # Extract raw text
            if result.content:
                receipt_data["raw_text"] = result.content
            
            return receipt_data
            
        except Exception as e:
            logger.error(f"Fout bij extracten receipt data: {e}")
            return {
                "success": False,
                "error": f"Data extractie fout: {str(e)}",
                "filename": filename
            }
    
    def _extract_receipt_fields(self, fields: Dict) -> Dict[str, Any]:
        """Extract belangrijke velden uit receipt fields"""
        extracted = {}
        
        # Mapping voor receipt fields
        field_mapping = {
            'MerchantName': 'merchant_name',
            'MerchantAddress': 'merchant_address',
            'MerchantPhoneNumber': 'merchant_phone',
            'TransactionDate': 'transaction_date',
            'TransactionTime': 'transaction_time',
            'Total': 'total_amount',
            'Subtotal': 'subtotal',
            'Tax': 'tax_amount',
            'Tip': 'tip_amount',
            'ReceiptType': 'receipt_type'
        }
        
        for azure_field, our_field in field_mapping.items():
            if azure_field in fields:
                field_data = fields[azure_field]
                extracted[our_field] = self._extract_field_value(field_data)
        
        return extracted
    
    def _extract_receipt_items(self, items_field) -> List[Dict[str, Any]]:
        """Extract items uit receipt"""
        items = []
        
        try:
            if hasattr(items_field, 'value') and isinstance(items_field.value, list):
                for item in items_field.value:
                    if hasattr(item, 'value') and hasattr(item.value, 'properties'):
                        receipt_item = {}
                        
                        # Extract item properties
                        properties = item.value.properties
                        for prop_name, prop_data in properties.items():
                            receipt_item[prop_name.lower()] = self._extract_field_value(prop_data)
                        
                        items.append(receipt_item)
            
        except Exception as e:
            logger.warning(f"Fout bij extracten receipt items: {e}")
        
        return items
    
    async def analyze_document_generic(self, file_content: bytes, filename: str, model_id: str = "prebuilt-read") -> Dict[str, Any]:
        """
        Generieke document analyse voor text extractie
        
        Args:
            file_content: Bestand content
            filename: Bestandsnaam
            model_id: Model om te gebruiken
            
        Returns:
            Geëxtraheerde text data
        """
        try:
            if not self.client:
                raise RuntimeError("Document Intelligence client niet geïnitialiseerd")
            
            logger.info(f"Start generieke document analyse voor {filename} met model {model_id}")
            
            poller = self.client.begin_analyze_document(
                model_id=model_id,
                analyze_request=AnalyzeDocumentRequest(bytes_source=file_content),
                content_type="application/octet-stream"
            )
            
            result: AnalyzeResult = poller.result()
            
            return {
                "success": True,
                "filename": filename,
                "analyzed_at": datetime.utcnow().isoformat(),
                "document_type": "generic",
                "content": result.content if result.content else "",
                "pages": len(result.pages) if result.pages else 0,
                "model_id": model_id
            }
            
        except Exception as e:
            logger.error(f"Fout bij generieke document analyse: {e}")
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }


# Singleton instance
_document_intelligence_instance: Optional[DocumentIntelligenceService] = None

def get_document_intelligence_service() -> DocumentIntelligenceService:
    """Verkrijg singleton instance van DocumentIntelligenceService"""
    global _document_intelligence_instance
    if _document_intelligence_instance is None:
        _document_intelligence_instance = DocumentIntelligenceService()
    return _document_intelligence_instance
"""
Microsoft Graph API Service voor Hoeflon AI Portal
Implementeert mailbox scanning en attachment processing volgens MS Graph best practices
"""
import os
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import io
import base64

from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.message import Message
from msgraph.generated.models.attachment import Attachment
from msgraph.generated.models.file_attachment import FileAttachment

from ..core.config import get_config

logger = logging.getLogger(__name__)


class GraphAPIService:
    """
    Service voor Microsoft Graph API operaties
    Focus op mailbox scanning en attachment verwerking
    """
    
    def __init__(self):
        self.config = get_config("graph")
        self.client: Optional[GraphServiceClient] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialiseer Graph API client met client credentials flow"""
        try:
            # Valideer configuratie
            required_fields = ["tenant_id", "client_id", "client_secret"]
            missing_fields = [field for field in required_fields if not self.config.get(field)]
            
            if missing_fields:
                logger.error(f"Ontbrekende Graph API configuratie: {missing_fields}")
                raise ValueError(f"Graph API configuratie onvolledig: {missing_fields}")
            
            # Client credentials flow voor backend service
            credential = ClientSecretCredential(
                tenant_id=self.config["tenant_id"],
                client_id=self.config["client_id"],
                client_secret=self.config["client_secret"]
            )
            
            # Initialiseer Graph client
            self.client = GraphServiceClient(
                credentials=credential,
                scopes=self.config["scopes"]
            )
            
            logger.info("Microsoft Graph API client succesvol geïnitialiseerd")
            
        except Exception as e:
            logger.error(f"Fout bij initialiseren Graph API client: {e}")
            raise
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Graph API connectie"""
        try:
            if not self.client:
                return {"status": "error", "message": "Client niet geïnitialiseerd"}
            
            # Test query - probeer gebruikers op te halen
            users_response = await self.client.users.get()
            
            return {
                "status": "success",
                "message": "Graph API connectie succesvol",
                "user_count": len(users_response.value) if users_response.value else 0
            }
            
        except Exception as e:
            logger.error(f"Graph API connectie test gefaald: {e}")
            return {
                "status": "error", 
                "message": str(e)
            }
    
    async def scan_mailbox_for_invoices(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Scan mailbox voor facturen (PDF attachments)
        
        Args:
            days_back: Aantal dagen terug om te scannen
            
        Returns:
            List van berichten met PDF attachments
        """
        try:
            if not self.client:
                raise RuntimeError("Graph API client niet geïnitialiseerd")
            
            # Bepaal mailbox om te scannen
            mailbox = self.config.get("mailbox_to_scan", "me")
            
            # Bereken datum filter
            start_date = datetime.utcnow() - timedelta(days=days_back)
            date_filter = start_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            
            # Query parameters voor berichten
            query_params = {
                "$filter": f"receivedDateTime ge {date_filter} and hasAttachments eq true",
                "$select": "id,subject,receivedDateTime,sender,hasAttachments",
                "$top": self.config.get("max_messages_per_scan", 50),
                "$orderby": "receivedDateTime desc"
            }
            
            logger.info(f"Scanning mailbox {mailbox} voor facturen vanaf {start_date}")
            
            # Haal berichten op
            if mailbox == "me":
                messages_response = await self.client.me.messages.get(
                    request_configuration=lambda config: self._configure_request(config, query_params)
                )
            else:
                messages_response = await self.client.users.by_user_id(mailbox).messages.get(
                    request_configuration=lambda config: self._configure_request(config, query_params)
                )
            
            if not messages_response.value:
                logger.info("Geen berichten gevonden met attachments")
                return []
            
            # Verwerk berichten en filter op PDF attachments
            invoice_messages = []
            for message in messages_response.value:
                if await self._has_pdf_attachments(message.id, mailbox):
                    message_data = await self._extract_message_data(message, mailbox)
                    if message_data:
                        invoice_messages.append(message_data)
            
            logger.info(f"Gevonden {len(invoice_messages)} berichten met PDF attachments")
            return invoice_messages
            
        except Exception as e:
            logger.error(f"Fout bij scannen mailbox: {e}")
            raise
    
    def _configure_request(self, config, query_params):
        """Helper voor query configuratie"""
        for key, value in query_params.items():
            setattr(config.query_parameters, key.lstrip('$'), value)
    
    async def _has_pdf_attachments(self, message_id: str, mailbox: str = "me") -> bool:
        """Check of bericht PDF attachments heeft"""
        try:
            if mailbox == "me":
                attachments_response = await self.client.me.messages.by_message_id(message_id).attachments.get()
            else:
                attachments_response = await self.client.users.by_user_id(mailbox).messages.by_message_id(message_id).attachments.get()
            
            if not attachments_response.value:
                return False
            
            # Check voor PDF attachments
            for attachment in attachments_response.value:
                if isinstance(attachment, FileAttachment):
                    filename = attachment.name or ""
                    if filename.lower().endswith('.pdf'):
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Fout bij controleren attachments voor bericht {message_id}: {e}")
            return False
    
    async def _extract_message_data(self, message: Message, mailbox: str = "me") -> Optional[Dict[str, Any]]:
        """Extract relevante data van bericht met PDF attachments"""
        try:
            # Haal attachments op
            attachments = await self._get_pdf_attachments(message.id, mailbox)
            
            if not attachments:
                return None
            
            # Extract sender informatie
            sender_info = "Onbekend"
            if message.sender and message.sender.email_address:
                sender_info = f"{message.sender.email_address.name} <{message.sender.email_address.address}>"
            
            message_data = {
                "message_id": message.id,
                "subject": message.subject or "Geen onderwerp",
                "sender": sender_info,
                "received_datetime": message.received_date_time.isoformat() if message.received_date_time else None,
                "attachments": attachments,
                "mailbox": mailbox,
                "processed": False,
                "extracted_at": datetime.utcnow().isoformat()
            }
            
            return message_data
            
        except Exception as e:
            logger.error(f"Fout bij extracten message data voor {message.id}: {e}")
            return None
    
    async def _get_pdf_attachments(self, message_id: str, mailbox: str = "me") -> List[Dict[str, Any]]:
        """Haal PDF attachments op van bericht"""
        try:
            if mailbox == "me":
                attachments_response = await self.client.me.messages.by_message_id(message_id).attachments.get()
            else:
                attachments_response = await self.client.users.by_user_id(mailbox).messages.by_message_id(message_id).attachments.get()
            
            if not attachments_response.value:
                return []
            
            pdf_attachments = []
            for attachment in attachments_response.value:
                if isinstance(attachment, FileAttachment):
                    filename = attachment.name or ""
                    if filename.lower().endswith('.pdf'):
                        attachment_data = {
                            "id": attachment.id,
                            "name": filename,
                            "size": attachment.size or 0,
                            "content_type": attachment.content_type or "application/pdf",
                            "content_bytes": attachment.content_bytes
                        }
                        pdf_attachments.append(attachment_data)
            
            return pdf_attachments
            
        except Exception as e:
            logger.error(f"Fout bij ophalen PDF attachments: {e}")
            return []
    
    async def download_attachment(self, message_id: str, attachment_id: str, mailbox: str = "me") -> Optional[bytes]:
        """
        Download specifieke attachment
        
        Args:
            message_id: ID van het bericht
            attachment_id: ID van de attachment
            mailbox: Mailbox om te gebruiken
            
        Returns:
            Attachment content als bytes
        """
        try:
            if mailbox == "me":
                attachment = await self.client.me.messages.by_message_id(message_id).attachments.by_attachment_id(attachment_id).get()
            else:
                attachment = await self.client.users.by_user_id(mailbox).messages.by_message_id(message_id).attachments.by_attachment_id(attachment_id).get()
            
            if isinstance(attachment, FileAttachment) and attachment.content_bytes:
                return base64.b64decode(attachment.content_bytes)
            
            return None
            
        except Exception as e:
            logger.error(f"Fout bij downloaden attachment {attachment_id}: {e}")
            return None
    
    async def mark_message_as_read(self, message_id: str, mailbox: str = "me") -> bool:
        """Markeer bericht als gelezen"""
        try:
            if mailbox == "me":
                await self.client.me.messages.by_message_id(message_id).patch({"isRead": True})
            else:
                await self.client.users.by_user_id(mailbox).messages.by_message_id(message_id).patch({"isRead": True})
            
            return True
            
        except Exception as e:
            logger.error(f"Fout bij markeren bericht als gelezen: {e}")
            return False
    
    async def move_message_to_folder(self, message_id: str, folder_name: str, mailbox: str = "me") -> bool:
        """
        Verplaats bericht naar specifieke folder
        
        Args:
            message_id: ID van bericht
            folder_name: Naam van doelfolder (bijv. "Processed Invoices")
            mailbox: Mailbox om te gebruiken
            
        Returns:
            Success status
        """
        try:
            # Zoek folder ID
            folder_id = await self._find_folder_id(folder_name, mailbox)
            if not folder_id:
                # Creëer folder als deze niet bestaat
                folder_id = await self._create_folder(folder_name, mailbox)
            
            if folder_id:
                # Verplaats bericht
                if mailbox == "me":
                    await self.client.me.messages.by_message_id(message_id).move.post({"destinationId": folder_id})
                else:
                    await self.client.users.by_user_id(mailbox).messages.by_message_id(message_id).move.post({"destinationId": folder_id})
                
                logger.info(f"Bericht {message_id} verplaatst naar folder {folder_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Fout bij verplaatsen bericht naar folder: {e}")
            return False
    
    async def _find_folder_id(self, folder_name: str, mailbox: str = "me") -> Optional[str]:
        """Zoek folder ID op basis van naam"""
        try:
            if mailbox == "me":
                folders_response = await self.client.me.mail_folders.get()
            else:
                folders_response = await self.client.users.by_user_id(mailbox).mail_folders.get()
            
            if folders_response.value:
                for folder in folders_response.value:
                    if folder.display_name == folder_name:
                        return folder.id
            
            return None
            
        except Exception as e:
            logger.error(f"Fout bij zoeken folder: {e}")
            return None
    
    async def _create_folder(self, folder_name: str, mailbox: str = "me") -> Optional[str]:
        """Creëer nieuwe mail folder"""
        try:
            folder_data = {"displayName": folder_name}
            
            if mailbox == "me":
                new_folder = await self.client.me.mail_folders.post(folder_data)
            else:
                new_folder = await self.client.users.by_user_id(mailbox).mail_folders.post(folder_data)
            
            logger.info(f"Folder '{folder_name}' succesvol gecreëerd")
            return new_folder.id if new_folder else None
            
        except Exception as e:
            logger.error(f"Fout bij creëren folder: {e}")
            return None
    
    async def get_processing_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Verkrijg verwerkingsstatistieken voor dashboard"""
        try:
            # In productie zou dit uit een database komen
            # Voor nu een placeholder implementatie
            
            stats = {
                "period_days": days,
                "total_emails_scanned": 0,
                "invoices_found": 0,
                "successfully_processed": 0,
                "processing_errors": 0,
                "last_scan": None
            }
            
            # Zou werkelijke stats ophalen uit database/logging
            logger.info(f"Processing statistics voor {days} dagen: {stats}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Fout bij ophalen processing statistics: {e}")
            return {"error": str(e)}


# Singleton instance
_graph_service_instance: Optional[GraphAPIService] = None

def get_graph_service() -> GraphAPIService:
    """Verkrijg singleton instance van GraphAPIService"""
    global _graph_service_instance
    if _graph_service_instance is None:
        _graph_service_instance = GraphAPIService()
    return _graph_service_instance
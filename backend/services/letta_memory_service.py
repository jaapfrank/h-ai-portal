"""
Letta Memory Service voor Hoeflon AI Portal
Implementeert geheugen- en contextbeheer voor gebruikers volgens Letta best practices
"""
import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import json

from letta_client import Letta
from letta_client.exceptions import LettaError

from ..core.config import get_config

logger = logging.getLogger(__name__)


class LettaMemoryService:
    """
    Service voor het beheren van Letta memory agents per gebruiker
    Volgens Letta best practices voor productieomgevingen
    """
    
    def __init__(self):
        self.config = get_config("letta")
        self.client = None
        self.user_agents: Dict[str, str] = {}  # user_id -> agent_id mapping
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialiseer Letta client met API key"""
        try:
            api_key = self.config.get("api_key")
            if not api_key:
                logger.error("LETTA_API_KEY niet gevonden in environment variables")
                raise ValueError("Letta API key is vereist")
            
            self.client = Letta(
                token=api_key,
                base_url=self.config.get("base_url", "https://api.letta.com")
            )
            logger.info("Letta client succesvol geïnitialiseerd")
            
        except Exception as e:
            logger.error(f"Fout bij initialiseren Letta client: {e}")
            raise
    
    async def get_or_create_user_agent(self, user_id: str, user_profile: Dict[str, Any]) -> str:
        """
        Verkrijg of creëer een Letta agent voor specifieke gebruiker
        
        Args:
            user_id: Unieke gebruikers-ID (bijv. Azure AD Object ID)
            user_profile: Gebruikersprofiel met naam, rol, voorkeuren etc.
            
        Returns:
            agent_id: Letta agent ID voor deze gebruiker
        """
        try:
            # Check of agent al bestaat voor deze gebruiker
            if user_id in self.user_agents:
                agent_id = self.user_agents[user_id]
                # Verificeer dat agent nog bestaat in Letta
                try:
                    agent_state = self.client.agents.get(agent_id)
                    logger.info(f"Bestaande agent gevonden voor gebruiker {user_id}")
                    return agent_id
                except LettaError:
                    # Agent bestaat niet meer, maak nieuwe
                    logger.warning(f"Agent {agent_id} niet meer gevonden, maak nieuwe")
                    del self.user_agents[user_id]
            
            # Maak nieuwe agent voor gebruiker
            agent_id = await self._create_user_agent(user_id, user_profile)
            self.user_agents[user_id] = agent_id
            
            return agent_id
            
        except Exception as e:
            logger.error(f"Fout bij verkrijgen/maken agent voor {user_id}: {e}")
            raise
    
    async def _create_user_agent(self, user_id: str, user_profile: Dict[str, Any]) -> str:
        """Creëer nieuwe Letta agent voor gebruiker"""
        try:
            # Bouw memory blocks gebaseerd op gebruikersprofiel
            memory_blocks = self._build_user_memory_blocks(user_id, user_profile)
            
            # Definieer tools voor Hoeflon ERP context
            tools = [
                "web_search",  # Standaard Letta tool
                # Voeg later custom tools toe voor ERP queries
            ]
            
            # Creëer agent met gebruikersspecifieke configuratie
            agent_state = self.client.agents.create(
                name=f"hoeflon_agent_{user_id}",
                model=self.config.get("model", "openai/gpt-4"),
                embedding=self.config.get("embedding_model", "openai/text-embedding-3-small"),
                memory_blocks=memory_blocks,
                tools=tools,
                metadata={
                    "user_id": user_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "platform": "hoeflon_ai_portal"
                }
            )
            
            logger.info(f"Nieuwe agent {agent_state.id} gemaakt voor gebruiker {user_id}")
            return agent_state.id
            
        except Exception as e:
            logger.error(f"Fout bij maken agent voor {user_id}: {e}")
            raise
    
    def _build_user_memory_blocks(self, user_id: str, user_profile: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Bouw memory blocks voor gebruiker volgens Letta best practices
        
        Returns:
            List van memory blocks met label en value
        """
        memory_blocks = []
        
        # Human memory block - wie is de gebruiker
        human_info = self._format_human_memory(user_profile)
        memory_blocks.append({
            "label": "human",
            "value": human_info
        })
        
        # Persona memory block - wie is de AI assistent
        persona_info = self._format_persona_memory()
        memory_blocks.append({
            "label": "persona", 
            "value": persona_info
        })
        
        # Context memory block - bedrijfscontext
        context_info = self._format_context_memory(user_profile)
        memory_blocks.append({
            "label": "context",
            "value": context_info
        })
        
        # Preferences memory block - gebruikersvoorkeuren
        if "preferences" in user_profile:
            prefs_info = self._format_preferences_memory(user_profile["preferences"])
            memory_blocks.append({
                "label": "preferences",
                "value": prefs_info
            })
        
        return memory_blocks
    
    def _format_human_memory(self, user_profile: Dict[str, Any]) -> str:
        """Format informatie over de gebruiker"""
        name = user_profile.get("name", "Onbekend")
        role = user_profile.get("role", "Medewerker")
        department = user_profile.get("department", "")
        
        human_memory = f"De gebruiker heet {name} en werkt als {role}"
        if department:
            human_memory += f" bij afdeling {department}"
        human_memory += " bij Hoeflon BV, een machinebouwbedrijf in Zwolle."
        
        # Voeg extra context toe indien beschikbaar
        if "manager" in user_profile:
            human_memory += f" Hun manager is {user_profile['manager']}."
        
        return human_memory
    
    def _format_persona_memory(self) -> str:
        """Format AI assistant persona"""
        return """Ik ben de Hoeflon AI Assistant, een intelligente digitale medewerker gespecialiseerd in het beantwoorden van vragen over ons ERP-systeem (Ridder), financiële data (AccountView), en bedrijfsinformatie. 

Ik help bij:
- Het opzoeken van productie-informatie en machine data
- Financiële rapportages en analyses  
- Contactinformatie en organisatiegegevens
- Algemene bedrijfsvragen

Ik ben vriendelijk, professioneel en gebruik Nederlandse taal tenzij anders gevraagd. Ik onthoud eerdere conversaties en leer van gebruikersinteracties."""
    
    def _format_context_memory(self, user_profile: Dict[str, Any]) -> str:
        """Format bedrijfscontext informatie"""
        context = """Hoeflon BV context:
- Machinebouwbedrijf gevestigd in Zwolle
- Gespecialiseerd in industriële machines en automatisering
- Gebruikt Ridder ERP voor productie en voorraad
- AccountView voor financiële administratie
- Multi-database omgeving met historische data"""
        
        # Voeg role-specifieke context toe
        role = user_profile.get("role", "").lower()
        if "productie" in role or "production" in role:
            context += "\n- Toegang tot productiedata en machine-informatie"
        elif "finance" in role or "financieel" in role:
            context += "\n- Toegang tot financiële analyses en rapportages"
        elif "hr" in role or "personeel" in role:
            context += "\n- Toegang tot personeelsinformatie en organisatiedata"
        elif "directie" in role or "management" in role:
            context += "\n- Volledige toegang tot alle bedrijfsdata en analyses"
        
        return context
    
    def _format_preferences_memory(self, preferences: Dict[str, Any]) -> str:
        """Format gebruikersvoorkeuren"""
        prefs = "Gebruikersvoorkeuren: "
        
        pref_items = []
        if preferences.get("language"):
            pref_items.append(f"Taal: {preferences['language']}")
        if preferences.get("notification_frequency"):
            pref_items.append(f"Notificaties: {preferences['notification_frequency']}")
        if preferences.get("dashboard_widgets"):
            pref_items.append(f"Dashboard widgets: {', '.join(preferences['dashboard_widgets'])}")
        
        prefs += ", ".join(pref_items) if pref_items else "Nog geen specifieke voorkeuren ingesteld"
        
        return prefs
    
    async def send_message(self, user_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Stuur bericht naar gebruikers agent en verkrijg response
        
        Args:
            user_id: Gebruikers-ID
            message: Bericht van gebruiker
            context: Optionele extra context (bijv. huidige pagina, recent uitgevoerde query)
            
        Returns:
            Response van agent inclusief memory updates
        """
        try:
            # Verkrijg agent voor gebruiker
            agent_id = self.user_agents.get(user_id)
            if not agent_id:
                raise ValueError(f"Geen agent gevonden voor gebruiker {user_id}")
            
            # Voeg context toe aan bericht indien beschikbaar
            enhanced_message = message
            if context:
                context_str = self._format_context_for_message(context)
                enhanced_message = f"{context_str}\n\nGebruiker vraagt: {message}"
            
            # Stuur bericht naar agent
            response = self.client.agents.messages.create(
                agent_id=agent_id,
                messages=[{
                    "role": "user", 
                    "content": enhanced_message
                }]
            )
            
            # Extract response berichten
            response_messages = []
            for msg in response.messages:
                if hasattr(msg, 'role') and hasattr(msg, 'content'):
                    response_messages.append({
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": datetime.utcnow().isoformat()
                    })
            
            logger.info(f"Bericht verwerkt voor gebruiker {user_id}")
            
            return {
                "messages": response_messages,
                "agent_id": agent_id,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Fout bij verwerken bericht voor {user_id}: {e}")
            raise
    
    def _format_context_for_message(self, context: Dict[str, Any]) -> str:
        """Format extra context voor bericht"""
        context_parts = []
        
        if context.get("current_page"):
            context_parts.append(f"Huidige pagina: {context['current_page']}")
        
        if context.get("recent_query"):
            context_parts.append(f"Recente query: {context['recent_query']}")
        
        if context.get("data_scope"):
            context_parts.append(f"Data scope: {context['data_scope']}")
        
        return "Context informatie: " + " | ".join(context_parts) if context_parts else ""
    
    async def update_user_memory(self, user_id: str, memory_type: str, content: str) -> bool:
        """
        Update specifiek memory block van gebruiker
        
        Args:
            user_id: Gebruikers-ID
            memory_type: Type memory (preferences, context, etc.)
            content: Nieuwe content voor memory block
            
        Returns:
            Success status
        """
        try:
            agent_id = self.user_agents.get(user_id)
            if not agent_id:
                raise ValueError(f"Geen agent gevonden voor gebruiker {user_id}")
            
            # Update memory via Letta memory management
            # Note: Exacte implementatie hangt af van Letta's memory update API
            # Dit is een placeholder voor de memory update functionaliteit
            
            logger.info(f"Memory {memory_type} bijgewerkt voor gebruiker {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Fout bij updaten memory voor {user_id}: {e}")
            return False
    
    async def get_user_memory_summary(self, user_id: str) -> Dict[str, Any]:
        """Verkrijg samenvatting van gebruiker memory"""
        try:
            agent_id = self.user_agents.get(user_id)
            if not agent_id:
                return {"error": "Geen agent gevonden"}
            
            # Verkrijg agent state
            agent_state = self.client.agents.get(agent_id)
            
            # Extract memory information
            memory_summary = {
                "agent_id": agent_id,
                "created_at": agent_state.metadata.get("created_at") if hasattr(agent_state, 'metadata') else None,
                "memory_blocks": []
            }
            
            # Add memory blocks summary (implementation depends on Letta API)
            # This is a placeholder for memory retrieval functionality
            
            return memory_summary
            
        except Exception as e:
            logger.error(f"Fout bij ophalen memory summary voor {user_id}: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_agents(self, retention_days: int = None) -> int:
        """
        Ruim oude, ongebruikte agents op
        
        Args:
            retention_days: Aantal dagen waarna agents worden opgeruimd
            
        Returns:
            Aantal opgeruimde agents
        """
        if retention_days is None:
            retention_days = self.config.get("memory_retention_days", 30)
        
        try:
            cleanup_count = 0
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Implementation depends on Letta's agent management API
            # This would involve:
            # 1. List all agents for this platform
            # 2. Check last activity date
            # 3. Delete agents older than cutoff_date
            
            logger.info(f"Cleanup voltooid: {cleanup_count} agents verwijderd")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"Fout bij cleanup van oude agents: {e}")
            return 0


# Singleton instance
_letta_service_instance = None

def get_letta_service() -> LettaMemoryService:
    """Verkrijg singleton instance van LettaMemoryService"""
    global _letta_service_instance
    if _letta_service_instance is None:
        _letta_service_instance = LettaMemoryService()
    return _letta_service_instance
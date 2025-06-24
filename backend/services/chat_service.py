"""
Main chat orchestration service
"""
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.exceptions import RoutingError, QueryExecutionError
from routing.intelligent_router import get_intelligent_router
from services.company_service import get_company_info, get_company_search
from database.connections import MultiDatabaseManager

class ChatService:
    """Main chat service that orchestrates query routing and processing"""
    
    def __init__(self):
        # Get config path relative to backend directory
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(backend_dir, "..", "config.json")
        self.db_manager = MultiDatabaseManager(config_path)
        self.intelligent_router = get_intelligent_router()
        
    async def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process a chat message and return appropriate response
        """
        try:
            # Use intelligent routing to determine how to handle the question
            routing_result = await self.intelligent_router.route_question_intelligently(message, session_id)
            
            primary_db = routing_result['routing']['primary_database']
            query_method = routing_result['method']['type']
            
            # Route based on intelligent router decision
            if primary_db == 'COMPANY_KNOWLEDGE':
                return await self._handle_company_query(message, session_id)
            elif primary_db in ['ERP', 'ACCOUNTVIEW']:
                return await self._handle_business_query(message, session_id, routing_result)
            else:
                return {
                    "response": "Ik begrijp je vraag niet helemaal. Kun je hem anders formuleren?",
                    "type": "clarification",
                    "routing_info": routing_result
                }
                
        except Exception as e:
            return {
                "response": f"Er is een fout opgetreden: {str(e)}",
                "type": "error"
            }
    
    async def _handle_company_query(self, message: str, session_id: str) -> Dict[str, Any]:
        """Handle company information queries"""
        try:
            company_info = get_company_search(message)
            return {
                "response": company_info,
                "type": "company_info"
            }
        except Exception as e:
            raise QueryExecutionError(f"Company query failed: {str(e)}")
    
    async def _handle_business_query(self, message: str, session_id: str, routing_result: Dict) -> Dict[str, Any]:
        """Handle business/ERP queries using intelligent routing"""
        try:
            primary_db = routing_result['routing']['primary_database']
            query_method = routing_result['method']['type']
            
            if query_method == 'AI_SQL_GENERATION':
                # Generate SQL query using AI
                response = f"AI SQL Query voor {primary_db}: '{message}' - Implementation needed"
            elif query_method == 'INTELLIGENT_TABLE_ANALYSIS':
                # Use intelligent table analysis
                response = f"Intelligent Analysis voor {primary_db}: '{message}' - Implementation needed"
            else:
                response = f"Query method '{query_method}' voor database '{primary_db}' - Implementation needed"
            
            return {
                "response": response,
                "type": "business_data",
                "routing_info": routing_result,
                "database": primary_db,
                "method": query_method
            }
        except Exception as e:
            raise QueryExecutionError(f"Business query failed: {str(e)}")
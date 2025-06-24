"""
Company Chat Endpoint - Database First Approach
===============================================

This creates a new chat endpoint that prioritizes company database
before falling back to AI systems.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import os
import sys

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.company_service import quick_company_search, is_company_info_question
    DATABASE_AVAILABLE = True
    print("✅ Company database imported successfully in company_chat_endpoint")
except ImportError as e:
    print(f"❌ Failed to import company database: {e}")
    DATABASE_AVAILABLE = False
    def quick_company_search(question): return None
    def is_company_info_question(question): return False

class CompanyChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class CompanyChatResponse(BaseModel):
    antwoord: str
    sql_query: Optional[str] = None
    resultaten: Optional[list] = None
    chart_data: Optional[str] = None
    drill_down_suggestions: Optional[list] = None
    session_id: Optional[str] = None
    csv_enhancement: Optional[dict] = None
    enterprise_analysis: Optional[dict] = None
    suggestions: Optional[list] = None
    suggestion_type: Optional[str] = None

router = APIRouter()

@router.post("/company_chat", response_model=CompanyChatResponse)
async def company_chat_endpoint(request: CompanyChatRequest):
    """
    🏢 COMPANY-FIRST CHAT ENDPOINT
    
    Priority order:
    1. Company Database (instant answers)
    2. AI Fallback (if no database match)
    """
    user_question = request.message.strip()
    session_id = request.session_id or "default"
    
    if not user_question:
        return CompanyChatResponse(
            antwoord="Geen vraag ontvangen.",
            session_id=session_id
        )
    
    print(f"🏢 COMPANY CHAT: '{user_question}' (session: {session_id})")
    
    # PRIORITY 1: Company Database Search
    if DATABASE_AVAILABLE and is_company_info_question(user_question):
        print(f"🔍 Company database check for: '{user_question}'")
        company_answer = quick_company_search(user_question)
        
        if company_answer:
            print(f"✅ COMPANY DATABASE HIT: {company_answer[:50]}...")
            return CompanyChatResponse(
                antwoord=company_answer,
                sql_query="[Company Database]",
                resultaten=[],
                session_id=session_id,
                enterprise_analysis={
                    "status": "company_database",
                    "source": "structured_data",
                    "confidence": 0.95
                }
            )
        else:
            print(f"📋 No database match for: '{user_question}'")
    
    # FALLBACK: Simple response for non-company questions
    return CompanyChatResponse(
        antwoord=f"Voor '{user_question}' gebruik ik de company database, maar geen directe match gevonden. Probeer specifiekere vragen zoals 'telefoonnummer van [naam]' of 'wie is de directeur'.",
        sql_query="[No Match]",
        resultaten=[],
        session_id=session_id,
        enterprise_analysis={
            "status": "no_database_match",
            "fallback": "available"
        }
    )

def setup_company_chat_routes(app):
    """Setup company chat routes on the main app"""
    app.include_router(router)
    print("✅ Company chat endpoint registered")

# Test function
def test_company_chat():
    """Test the company chat functionality"""
    import asyncio
    
    async def run_test():
        test_questions = [
            "wat is het telefoonnummer van jaap frank",
            "wie is de directeur", 
            "hoe vraag ik verlof aan",
            "hoeveel machines hebben we"  # Non-company question
        ]
        
        for question in test_questions:
            request = CompanyChatRequest(message=question)
            response = await company_chat_endpoint(request)
            print(f"\nQ: {question}")
            print(f"A: {response.antwoord}")
            print(f"Source: {response.enterprise_analysis}")
    
    asyncio.run(run_test())

if __name__ == "__main__":
    test_company_chat()
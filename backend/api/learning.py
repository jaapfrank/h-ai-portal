"""
Learning API endpoints for user feedback and corrections
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines.intelligence.memory import conversational_memory

router = APIRouter()

class LearningFeedback(BaseModel):
    session_id: str
    original_question: str
    original_answer: str
    corrected_answer: str
    correction_type: str = "general"  # general, query_result, explanation
    metadata: Optional[Dict[str, Any]] = None

class QueryCorrection(BaseModel):
    session_id: str
    question: str
    expected_result: Any
    actual_result: Any
    correct_sql: Optional[str] = None
    explanation: Optional[str] = None

@router.post("/feedback/correction")
async def submit_correction(feedback: LearningFeedback):
    """Submit a correction to improve future responses"""
    try:
        # Store the correction in conversational memory
        correction_message = f"Correctie: '{feedback.original_question}' - Het juiste antwoord is: {feedback.corrected_answer}"
        
        conversational_memory.add_interaction(
            session_id=feedback.session_id,
            user_question=f"[CORRECTIE] {feedback.original_question}",
            ai_response=correction_message,
            sql_query=None,
            results=[{
                "type": "user_correction",
                "original_answer": feedback.original_answer,
                "corrected_answer": feedback.corrected_answer,
                "correction_type": feedback.correction_type,
                "metadata": feedback.metadata
            }],
            confidence=1.0
        )
        
        return {
            "status": "success",
            "message": "Correctie opgeslagen! Dit wordt gebruikt om toekomstige antwoorden te verbeteren.",
            "learned_data": {
                "question": feedback.original_question,
                "correction": feedback.corrected_answer,
                "type": feedback.correction_type
            }
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Fout bij opslaan correctie: {str(e)}"
        }

@router.post("/feedback/query")
async def submit_query_correction(correction: QueryCorrection):
    """Submit a query correction with expected vs actual results"""
    try:
        correction_message = f"Query correctie voor: '{correction.question}'"
        if correction.explanation:
            correction_message += f" - {correction.explanation}"
        
        conversational_memory.add_interaction(
            session_id=correction.session_id,
            user_question=f"[QUERY CORRECTIE] {correction.question}",
            ai_response=correction_message,
            sql_query=correction.correct_sql,
            results=[{
                "type": "query_correction",
                "expected_result": correction.expected_result,
                "actual_result": correction.actual_result,
                "correct_sql": correction.correct_sql,
                "explanation": correction.explanation
            }],
            confidence=1.0
        )
        
        return {
            "status": "success",
            "message": "Query correctie opgeslagen!",
            "learned_data": {
                "question": correction.question,
                "expected_result": correction.expected_result,
                "correct_sql": correction.correct_sql
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Fout bij opslaan query correctie: {str(e)}"
        }

@router.get("/memory/session/{session_id}")
async def get_session_memory(session_id: str, limit: int = 10):
    """Get conversation memory for a session"""
    try:
        history = conversational_memory.get_session_history(session_id, limit)
        suggestions = conversational_memory.get_followup_suggestions(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "conversation_history": history,
            "followup_suggestions": suggestions,
            "total_interactions": len(history)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Fout bij ophalen sessie geheugen: {str(e)}"
        }

@router.post("/memory/session/{session_id}/search")
async def search_session_memory(session_id: str, search_term: str):
    """Search through session memory"""
    try:
        matches = conversational_memory.search_conversation_history(session_id, search_term)
        
        return {
            "status": "success",
            "search_term": search_term,
            "matches": matches,
            "total_matches": len(matches)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Fout bij zoeken in geheugen: {str(e)}"
        }

@router.get("/memory/suggestions/{session_id}")
async def get_followup_suggestions(session_id: str):
    """Get AI-generated follow-up suggestions"""
    try:
        suggestions = conversational_memory.get_followup_suggestions(session_id)
        
        return {
            "status": "success",
            "session_id": session_id,
            "suggestions": suggestions
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Fout bij genereren suggesties: {str(e)}"
        }
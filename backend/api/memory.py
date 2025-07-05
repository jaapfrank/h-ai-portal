"""
FastAPI endpoints voor Letta memory management
Ondersteunt user context, memory operaties en agent management
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..services.letta_memory_service import get_letta_service, LettaMemoryService
from ..database.memory_db import get_db_context, get_memory_db
from ..models.user_context import (
    UserContext, UserSession, UserPreferences,
    get_or_create_user_by_azure_id, update_user_letta_agent
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory", tags=["Memory Management"])


# Pydantic models voor API requests/responses
class MemoryMessageRequest(BaseModel):
    """Request model voor memory message"""
    message: str = Field(..., description="Gebruikerbericht")
    context: Optional[Dict[str, Any]] = Field(None, description="Extra context informatie")


class MemoryMessageResponse(BaseModel):
    """Response model voor memory message"""
    messages: List[Dict[str, Any]] = Field(..., description="Agent response berichten")
    agent_id: str = Field(..., description="Letta agent ID")
    processed_at: str = Field(..., description="Verwerkingstijd")
    user_context: Dict[str, Any] = Field(..., description="User context informatie")


class UserProfileRequest(BaseModel):
    """Request model voor user profile update"""
    azure_claims: Dict[str, Any] = Field(..., description="Azure AD claims")
    custom_attributes: Optional[Dict[str, Any]] = Field(None, description="Custom attributen")


class UserPreferencesRequest(BaseModel):
    """Request model voor user preferences update"""
    language: Optional[str] = Field(None, description="Taalvoorkeur")
    theme: Optional[str] = Field(None, description="Theme voorkeur")
    dashboard_layout: Optional[str] = Field(None, description="Dashboard layout")
    notification_frequency: Optional[str] = Field(None, description="Notificatie frequentie")
    enable_memory: Optional[bool] = Field(None, description="Memory aan/uit")
    ai_response_style: Optional[str] = Field(None, description="AI response stijl")
    custom_preferences: Optional[Dict[str, Any]] = Field(None, description="Custom voorkeuren")


class MemoryUpdateRequest(BaseModel):
    """Request model voor memory update"""
    memory_type: str = Field(..., description="Type memory block")
    content: str = Field(..., description="Memory content")


# Helper functions
def get_user_from_request(request: Request, session: Session) -> UserContext:
    """
    Extract user van request headers (Azure AD token)
    Voor demo doeleinden - in productie via JWT token parsing
    """
    # Demo implementation - haal user ID van header
    azure_object_id = request.headers.get("X-User-ID")
    if not azure_object_id:
        raise HTTPException(status_code=401, detail="User ID header vereist")
    
    # Haal of creëer user
    try:
        # Demo claims - in productie van JWT token
        demo_claims = {
            "oid": azure_object_id,
            "upn": f"user_{azure_object_id}@hoeflon.nl",
            "name": f"Demo User {azure_object_id}",
            "email": f"user_{azure_object_id}@hoeflon.nl",
            "jobTitle": "Medewerker",
            "department": "IT"
        }
        
        user = get_or_create_user_by_azure_id(azure_object_id, session, demo_claims)
        return user
        
    except Exception as e:
        logger.error(f"Fout bij verkrijgen user: {e}")
        raise HTTPException(status_code=500, detail="Fout bij gebruiker authenticatie")


# API Endpoints
@router.post("/chat", response_model=MemoryMessageResponse)
async def send_memory_message(
    request: MemoryMessageRequest,
    http_request: Request,
    letta_service: LettaMemoryService = Depends(get_letta_service)
):
    """
    Stuur bericht naar user's memory agent
    """
    try:
        with get_db_context() as session:
            # Verkrijg user van request
            user = get_user_from_request(http_request, session)
            
            # Zorg dat user een Letta agent heeft
            user_profile = user.get_user_profile_for_letta()
            agent_id = await letta_service.get_or_create_user_agent(
                user.azure_object_id, 
                user_profile
            )
            
            # Update agent ID in database indien nieuw
            if user.letta_agent_id != agent_id:
                update_user_letta_agent(user.id, agent_id, session)
            
            # Stuur bericht naar agent
            response = await letta_service.send_message(
                user.azure_object_id,
                request.message,
                request.context
            )
            
            # Update last interaction
            user.agent_last_interaction = datetime.utcnow()
            session.commit()
            
            return MemoryMessageResponse(
                messages=response["messages"],
                agent_id=response["agent_id"],
                processed_at=response["processed_at"],
                user_context=user.to_dict()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij memory chat: {e}")
        raise HTTPException(status_code=500, detail=f"Memory service fout: {str(e)}")


@router.get("/profile")
async def get_user_profile(
    http_request: Request
):
    """
    Verkrijg user profile en memory status
    """
    try:
        with get_db_context() as session:
            user = get_user_from_request(http_request, session)
            
            # Verkrijg memory summary van Letta
            letta_service = get_letta_service()
            memory_summary = await letta_service.get_user_memory_summary(user.azure_object_id)
            
            return {
                "user_profile": user.to_dict(),
                "preferences": user.preferences.to_dict() if user.preferences else None,
                "memory_summary": memory_summary,
                "agent_status": {
                    "has_agent": bool(user.letta_agent_id),
                    "agent_id": user.letta_agent_id,
                    "last_interaction": user.agent_last_interaction.isoformat() if user.agent_last_interaction else None
                }
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij ophalen user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Profile service fout: {str(e)}")


@router.put("/profile")
async def update_user_profile(
    request: UserProfileRequest,
    http_request: Request
):
    """
    Update user profile informatie
    """
    try:
        with get_db_context() as session:
            user = get_user_from_request(http_request, session)
            
            # Update user met nieuwe claims
            claims = request.azure_claims
            user.azure_claims = claims
            user.display_name = claims.get("name", user.display_name)
            user.email = claims.get("email", user.email)
            user.department = claims.get("department", user.department)
            user.job_title = claims.get("jobTitle", user.job_title)
            
            if request.custom_attributes:
                user.custom_attributes = request.custom_attributes
            
            session.commit()
            
            return {"status": "success", "user_profile": user.to_dict()}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij updaten user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Profile update fout: {str(e)}")


@router.put("/preferences")
async def update_user_preferences(
    request: UserPreferencesRequest,
    http_request: Request
):
    """
    Update gebruikersvoorkeuren
    """
    try:
        with get_db_context() as session:
            user = get_user_from_request(http_request, session)
            
            # Verkrijg of creëer preferences
            if not user.preferences:
                user.preferences = UserPreferences(user=user)
                session.add(user.preferences)
            
            preferences = user.preferences
            
            # Update alleen ingestelde velden
            if request.language is not None:
                preferences.language = request.language
            if request.theme is not None:
                preferences.theme = request.theme
            if request.dashboard_layout is not None:
                preferences.dashboard_layout = request.dashboard_layout
            if request.notification_frequency is not None:
                preferences.notification_frequency = request.notification_frequency
            if request.enable_memory is not None:
                preferences.enable_memory = request.enable_memory
            if request.ai_response_style is not None:
                preferences.ai_response_style = request.ai_response_style
            if request.custom_preferences is not None:
                preferences.custom_preferences = request.custom_preferences
            
            session.commit()
            
            return {"status": "success", "preferences": preferences.to_dict()}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij updaten preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Preferences update fout: {str(e)}")


@router.put("/memory/{memory_type}")
async def update_memory_block(
    memory_type: str,
    request: MemoryUpdateRequest,
    http_request: Request,
    letta_service: LettaMemoryService = Depends(get_letta_service)
):
    """
    Update specifiek memory block van user agent
    """
    try:
        with get_db_context() as session:
            user = get_user_from_request(http_request, session)
            
            if not user.letta_agent_id:
                raise HTTPException(status_code=404, detail="Geen memory agent gevonden voor gebruiker")
            
            # Update memory via Letta service
            success = await letta_service.update_user_memory(
                user.azure_object_id,
                memory_type,
                request.content
            )
            
            if success:
                user.agent_last_interaction = datetime.utcnow()
                session.commit()
                return {"status": "success", "memory_type": memory_type}
            else:
                raise HTTPException(status_code=500, detail="Memory update gefaald")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij memory update: {e}")
        raise HTTPException(status_code=500, detail=f"Memory update fout: {str(e)}")


@router.get("/sessions")
async def get_user_sessions(
    http_request: Request,
    limit: int = 10,
    offset: int = 0
):
    """
    Verkrijg user sessie geschiedenis
    """
    try:
        with get_db_context() as session:
            user = get_user_from_request(http_request, session)
            
            # Haal sessies op
            sessions = (session.query(UserSession)
                       .filter_by(user_id=user.id)
                       .order_by(UserSession.started_at.desc())
                       .offset(offset)
                       .limit(limit)
                       .all())
            
            return {
                "sessions": [s.to_dict() for s in sessions],
                "total_count": len(user.sessions),
                "limit": limit,
                "offset": offset
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij ophalen sessies: {e}")
        raise HTTPException(status_code=500, detail=f"Sessions service fout: {str(e)}")


@router.get("/health")
async def memory_health_check():
    """
    Health check voor memory services
    """
    try:
        # Database health check
        db_health = get_memory_db().health_check()
        
        # Letta service health check
        letta_service = get_letta_service()
        letta_health = {
            "status": "healthy" if letta_service.client else "unhealthy",
            "client_initialized": bool(letta_service.client)
        }
        
        overall_status = "healthy" if (
            db_health["status"] == "healthy" and 
            letta_health["status"] == "healthy"
        ) else "unhealthy"
        
        return {
            "status": overall_status,
            "database": db_health,
            "letta_service": letta_health,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check gefaald: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.delete("/agent")
async def reset_user_agent(
    http_request: Request,
    letta_service: LettaMemoryService = Depends(get_letta_service)
):
    """
    Reset user's memory agent (delete and recreate)
    """
    try:
        with get_db_context() as session:
            user = get_user_from_request(http_request, session)
            
            # Verwijder agent referentie uit database
            user.letta_agent_id = None
            user.agent_created_at = None
            user.agent_last_interaction = None
            
            # Verwijder uit service cache
            if user.azure_object_id in letta_service.user_agents:
                del letta_service.user_agents[user.azure_object_id]
            
            session.commit()
            
            return {"status": "success", "message": "Memory agent gereset"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fout bij agent reset: {e}")
        raise HTTPException(status_code=500, detail=f"Agent reset fout: {str(e)}")


# Router toevoegen aan main app
def include_memory_router(app):
    """Helper functie om memory router toe te voegen aan FastAPI app"""
    app.include_router(router)
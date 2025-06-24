"""
Health check API endpoints
"""
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import get_config

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    database_status: str

@router.get("/status", response_model=HealthResponse)
async def health_check():
    """System health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="2.0.0",
        database_status="connected"
    )

@router.get("/config")
async def get_system_config():
    """Get system configuration (non-sensitive parts)"""
    return {
        "api": get_config("api"),
        "session": get_config("session"),
        "version": "2.0.0"
    }
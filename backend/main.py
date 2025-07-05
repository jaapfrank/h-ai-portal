"""
Hoeflon Ridder ERP AI Chatbot - Main FastAPI Application
========================================================

A modular AI-powered chatbot that answers business questions by generating 
and executing SQL queries against the Ridder ERP database system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.config import get_config
from api.chat import router as chat_router
from api.company import router as company_router  
from api.health import router as health_router
from api.learning import router as learning_router
from api.memory import router as memory_router
from api.documents import router as documents_router

# Create FastAPI application
app = FastAPI(
    title="Hoeflon Ridder ERP AI Chatbot",
    description="AI-powered chatbot for business intelligence queries",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health_router, tags=["health"])
app.include_router(chat_router, tags=["chat"])
app.include_router(company_router, tags=["company"])
app.include_router(learning_router, prefix="/learning", tags=["learning"])
app.include_router(memory_router, prefix="/memory", tags=["memory"])
app.include_router(documents_router, prefix="/documents", tags=["documents"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Hoeflon Ridder ERP AI Chatbot API",
        "version": "2.0.0",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    config = get_config("api")
    uvicorn.run(
        "main:app",
        host=config["host"],
        port=config["port"],
        reload=config["reload"]
    )
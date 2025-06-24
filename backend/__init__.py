"""
Hoeflon Ridder ERP AI Chatbot Backend
=====================================

A modular AI-powered chatbot that answers business questions by generating 
and executing SQL queries against the Ridder ERP database system.

Module Structure:
- core/: Core system components (config, exceptions)  
- database/: Database connections and knowledge stores
- routing/: Intelligent query routing and preprocessing
- engines/: Processing engines (query, analysis, intelligence)
- services/: Business logic services
- api/: FastAPI endpoints
"""

__version__ = "2.0.0"
__author__ = "Claude & Team Hoeflon"
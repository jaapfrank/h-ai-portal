"""
Configuration management for the Hoeflon ERP AI system
"""
import os
from typing import Dict, Any

# Database Configuration
DATABASE_CONFIG = {
    "ridder_erp": {
        "server": "sql1.hoeflon.local",
        "database": "Hoeflon", 
        "driver": "ODBC Driver 18 for SQL Server",
        "username": "AI",
        "password": "Hoofdstraat159!",
        "trusted_connection": "no"
    },
    "hoeflon_bv": {
        "server": "sql1.hoeflon.local",
        "database": "HOEFLON25",
        "driver": "ODBC Driver 18 for SQL Server", 
        "username": "AI",
        "password": "Hoofdstraat159!",
        "trusted_connection": "no"
    },
    "hoeflon_int": {
        "server": "sql1.hoeflon.local",
        "database": "HOEFINT25",
        "driver": "ODBC Driver 18 for SQL Server",
        "username": "AI",
        "password": "Hoofdstraat159!",
        "trusted_connection": "no"
    }
}

# Knowledge Database Paths
KNOWLEDGE_DB_PATHS = {
    "csv_knowledge": os.path.join(os.path.dirname(__file__), "..", "database", "knowledge", "csv_database_knowledge.db"),
    "company_db": os.path.join(os.path.dirname(__file__), "..", "database", "knowledge", "hoeflon_company.db"), 
    "ml_learning": os.path.join(os.path.dirname(__file__), "..", "database", "knowledge", "ml_learning.db")
}

# API Configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8504,
    "reload": True
}

# Security Settings
FORBIDDEN_SQL_OPERATIONS = [
    "DROP", "DELETE", "INSERT", "UPDATE", "CREATE", "ALTER", 
    "TRUNCATE", "EXEC", "EXECUTE", "SP_", "XP_"
]

# Query Timeout (seconds)
QUERY_TIMEOUT = 30

# Session Configuration
SESSION_CONFIG = {
    "timeout_minutes": 60,
    "max_sessions": 1000
}

# Letta Memory Configuration
LETTA_CONFIG = {
    "api_key": os.getenv("LETTA_API_KEY", ""),
    "base_url": os.getenv("LETTA_BASE_URL", "https://api.letta.com"),
    "model": "openai/gpt-4",
    "embedding_model": "openai/text-embedding-3-small",
    "max_memory_blocks": 10,
    "memory_retention_days": 30
}

# Microsoft Graph API Configuration
GRAPH_CONFIG = {
    "tenant_id": os.getenv("AZURE_TENANT_ID", ""),
    "client_id": os.getenv("AZURE_CLIENT_ID", ""),
    "client_secret": os.getenv("AZURE_CLIENT_SECRET", ""),
    "scopes": ["https://graph.microsoft.com/.default"],
    "mailbox_to_scan": os.getenv("GRAPH_MAILBOX", "facturen@hoeflon.nl"),
    "scan_interval_hours": int(os.getenv("GRAPH_SCAN_INTERVAL", "1")),
    "max_messages_per_scan": int(os.getenv("GRAPH_MAX_MESSAGES", "50"))
}

# Azure Document Intelligence Configuration
DOCUMENT_INTELLIGENCE_CONFIG = {
    "endpoint": os.getenv("AZURE_DOC_INTEL_ENDPOINT", ""),
    "api_key": os.getenv("AZURE_DOC_INTEL_KEY", ""),
    "api_version": "2024-02-29-preview",
    "invoice_model": "prebuilt-invoice",
    "receipt_model": "prebuilt-receipt",
    "max_file_size_mb": 50,
    "supported_formats": [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]
}

def get_config(section: str) -> Dict[str, Any]:
    """Get configuration for a specific section"""
    configs = {
        "database": DATABASE_CONFIG,
        "knowledge": KNOWLEDGE_DB_PATHS,
        "api": API_CONFIG,
        "session": SESSION_CONFIG,
        "letta": LETTA_CONFIG,
        "graph": GRAPH_CONFIG,
        "document_intelligence": DOCUMENT_INTELLIGENCE_CONFIG
    }
    return configs.get(section, {})
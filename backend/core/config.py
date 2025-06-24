"""
Configuration management for the Hoeflon ERP AI system
"""
import os
from typing import Dict, Any

# Database Configuration
DATABASE_CONFIG = {
    "ridder_erp": {
        "server": "srv-dc-sql2019\\SQLEXPRESS",
        "database": "Ridder", 
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted_connection": "yes"
    },
    "hoeflon_bv": {
        "server": "srv-dc-sql2019\\SQLEXPRESS",
        "database": "HOEFLON25",
        "driver": "ODBC Driver 17 for SQL Server", 
        "trusted_connection": "yes"
    },
    "hoeflon_int": {
        "server": "srv-dc-sql2019\\SQLEXPRESS",
        "database": "HOEFINT25",
        "driver": "ODBC Driver 17 for SQL Server",
        "trusted_connection": "yes"
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

def get_config(section: str) -> Dict[str, Any]:
    """Get configuration for a specific section"""
    configs = {
        "database": DATABASE_CONFIG,
        "knowledge": KNOWLEDGE_DB_PATHS,
        "api": API_CONFIG,
        "session": SESSION_CONFIG
    }
    return configs.get(section, {})
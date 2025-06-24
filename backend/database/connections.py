#!/usr/bin/env python3
"""
Multi-Database Manager for Hoeflon AI
Handles connections to multiple database sources:
- Ridder ERP (SQL Server)
- AccountView Hoeflon B.V. (DBF files)
- AccountView Hoeflon International (DBF files)
"""

import pyodbc
import pandas as pd
import os
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
from dbfread import DBF
import datetime

class MultiDatabaseManager:
    """Manages connections to multiple database sources"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self.load_config()
        self.connections = {}
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_erp_connection(self):
        """Get connection to Ridder ERP SQL Server database"""
        if 'erp' not in self.connections:
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.config['sql_host']};"
                f"DATABASE={self.config['sql_db']};"
                f"UID={self.config['sql_user']};"
                f"PWD={self.config['sql_pass']};"
                f"TrustServerCertificate=yes;"
                f"Encrypt=optional"
            )
            self.connections['erp'] = pyodbc.connect(connection_string, timeout=30)
        return self.connections['erp']
    
    def query_erp(self, sql: str) -> List[Dict[str, Any]]:
        """Execute query on Ridder ERP database"""
        conn = self.get_erp_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                result_dict = {}
                for i, value in enumerate(row):
                    if isinstance(value, (bytes,)):
                        result_dict[columns[i]] = f"<binary:{len(value)} bytes>"
                    elif hasattr(value, 'isoformat'):  # datetime objects
                        result_dict[columns[i]] = value.isoformat()
                    else:
                        result_dict[columns[i]] = value
                results.append(result_dict)
            
            return results
        finally:
            cursor.close()
    
    def get_dbf_tables(self, database_name: str) -> List[str]:
        """Get list of DBF tables in AccountView database"""
        if database_name == "hoeflon_bv":
            dbf_path = os.path.join(self.base_dir, "HOEFLON25", "HOEFLON25")
        elif database_name == "hoeflon_international":
            dbf_path = os.path.join(self.base_dir, "HOEFLON25", "HOEFINT25")
        else:
            raise ValueError(f"Unknown AccountView database: {database_name}")
        
        if not os.path.exists(dbf_path):
            return []
        
        # Find all .DBF files
        dbf_files = []
        for file in os.listdir(dbf_path):
            if file.upper().endswith('.DBF'):
                table_name = file[:-4]  # Remove .DBF extension
                dbf_files.append(table_name)
        
        return sorted(dbf_files)
    
    def query_dbf(self, database_name: str, table_name: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Query DBF table using dbfread library"""
        if database_name == "hoeflon_bv":
            dbf_path = os.path.join(self.base_dir, "HOEFLON25", "HOEFLON25")
        elif database_name == "hoeflon_international":
            dbf_path = os.path.join(self.base_dir, "HOEFLON25", "HOEFINT25")
        else:
            raise ValueError(f"Unknown AccountView database: {database_name}")
        
        dbf_file = os.path.join(dbf_path, f"{table_name}.DBF")
        
        if not os.path.exists(dbf_file):
            raise FileNotFoundError(f"DBF file not found: {dbf_file}")
        
        try:
            # Read DBF file using dbfread
            table = DBF(dbf_file, encoding='latin1')
            results = []
            
            for i, record in enumerate(table):
                if i >= limit:  # Limit records for performance
                    break
                    
                # Convert record to dictionary with proper data types
                result_dict = {}
                for key, value in record.items():
                    if isinstance(value, datetime.date):
                        result_dict[key] = value.isoformat()
                    elif isinstance(value, datetime.datetime):
                        result_dict[key] = value.isoformat()
                    elif isinstance(value, (bytes,)):
                        result_dict[key] = f"<binary:{len(value)} bytes>"
                    elif value is None:
                        result_dict[key] = None
                    else:
                        result_dict[key] = str(value).strip() if isinstance(value, str) else value
                
                results.append(result_dict)
            
            return results
            
        except Exception as e:
            raise Exception(f"Could not read DBF table {table_name}: {str(e)}")
    
    def get_financial_summary(self, year: int = 2025) -> Dict[str, Any]:
        """Get financial summary from both AccountView databases"""
        summary = {
            "year": year,
            "hoeflon_bv": {},
            "hoeflon_international": {},
            "combined": {}
        }
        
        # Get available tables for both databases
        try:
            bv_tables = self.get_dbf_tables("hoeflon_bv")
            int_tables = self.get_dbf_tables("hoeflon_international")
            
            summary["hoeflon_bv"]["available_tables"] = bv_tables
            summary["hoeflon_international"]["available_tables"] = int_tables
            
            # Key financial tables to look for
            financial_tables = ["LEDGER", "OPENITEM", "DAILY", "PJT_HDR", "PJT_LINE"]
            
            for db_name in ["hoeflon_bv", "hoeflon_international"]:
                tables = bv_tables if db_name == "hoeflon_bv" else int_tables
                summary[db_name]["financial_data"] = {}
                
                for table in financial_tables:
                    if table in tables:
                        try:
                            # Get sample data from each financial table
                            data = self.query_dbf(db_name, table)
                            summary[db_name]["financial_data"][table] = {
                                "record_count": len(data),
                                "sample_records": data[:3] if data else [],
                                "columns": list(data[0].keys()) if data else []
                            }
                        except Exception as e:
                            summary[db_name]["financial_data"][table] = {
                                "error": str(e)
                            }
            
        except Exception as e:
            summary["error"] = str(e)
        
        return summary
    
    def execute_multi_database_query(self, query_instruction: str) -> Dict[str, Any]:
        """Execute queries across multiple databases based on instruction"""
        result = {
            "instruction": query_instruction,
            "databases_queried": [],
            "results": {}
        }
        
        # Determine which databases to query based on instruction
        instruction_lower = query_instruction.lower()
        
        # ERP queries
        if any(word in instruction_lower for word in ["machines", "productie", "voorraad", "erp"]):
            result["databases_queried"].append("erp")
            # Execute ERP query (simplified example)
            try:
                erp_results = self.query_erp("SELECT COUNT(*) as machine_count FROM U_SERIENUMMERSHOEFLON")
                result["results"]["erp"] = erp_results
            except Exception as e:
                result["results"]["erp"] = {"error": str(e)}
        
        # Financial queries for both AccountView databases
        if any(word in instruction_lower for word in ["omzet", "financieel", "ledger", "accounting"]):
            for db_name in ["hoeflon_bv", "hoeflon_international"]:
                result["databases_queried"].append(db_name)
                try:
                    # Try to get financial data from LEDGER table
                    financial_data = self.query_dbf(db_name, "LEDGER")
                    result["results"][db_name] = {
                        "record_count": len(financial_data),
                        "sample": financial_data[:5]
                    }
                except Exception as e:
                    result["results"][db_name] = {"error": str(e)}
        
        return result
    
    def get_database_schemas(self) -> Dict[str, Any]:
        """Get schemas for all connected databases"""
        schemas = {}
        
        # ERP Schema (already generated)
        erp_schema_path = os.path.join(self.base_dir, "schema_full.json")
        if os.path.exists(erp_schema_path):
            with open(erp_schema_path, 'r', encoding='utf-8') as f:
                schemas["erp"] = json.load(f)
        
        # AccountView schemas
        for db_name in ["hoeflon_bv", "hoeflon_international"]:
            try:
                tables = self.get_dbf_tables(db_name)
                schemas[db_name] = {
                    "database_type": "AccountView_DBF",
                    "table_count": len(tables),
                    "tables": {}
                }
                
                # Get structure for each table (limited to first few for performance)
                for table in tables[:10]:  # Limit to first 10 tables
                    try:
                        sample_data = self.query_dbf(db_name, table)
                        if sample_data:
                            schemas[db_name]["tables"][table] = {
                                "record_count": len(sample_data),
                                "columns": list(sample_data[0].keys()),
                                "sample_data": sample_data[:2]
                            }
                    except Exception as e:
                        schemas[db_name]["tables"][table] = {"error": str(e)}
                        
            except Exception as e:
                schemas[db_name] = {"error": str(e)}
        
        return schemas
    
    def close_connections(self):
        """Close all database connections"""
        for conn_name, conn in self.connections.items():
            try:
                conn.close()
            except:
                pass
        self.connections.clear()
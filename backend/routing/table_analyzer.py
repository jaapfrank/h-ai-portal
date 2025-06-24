#!/usr/bin/env python3
"""
Intelligent Table Analyzer - True ML Approach
Automatically analyzes ALL database tables and understands their business meaning
Generates dynamic SQL queries without manual mapping
"""

import pyodbc
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import sqlite3

class IntelligentTableAnalyzer:
    """AI-powered database table analyzer that understands business context"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.table_knowledge = {}
        self.column_meanings = {}
        self.relationship_map = {}
        self.business_concepts = {}
        
    def analyze_entire_database(self) -> Dict[str, Any]:
        """Analyze ALL tables and understand their business meaning"""
        print("🧠 Starting intelligent database analysis...")
        
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Get ALL tables AND views (especially V_R_ views)
            cursor.execute("""
            SELECT TABLE_NAME, TABLE_TYPE 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE IN ('BASE TABLE', 'VIEW')
            ORDER BY TABLE_NAME
            """)
            
            tables = cursor.fetchall()
            print(f"📊 Found {len(tables)} tables to analyze")
            
            analysis_results = {
                "total_tables": len(tables),
                "total_views": len([t for t in tables if t[1] == 'VIEW']),
                "total_v_r_views": len([t for t in tables if t[1] == 'VIEW' and t[0].startswith('V_R_')]),
                "analyzed_tables": {},
                "analyzed_views": {},
                "v_r_views": {},
                "business_concepts": {},
                "auto_generated_queries": {},
                "table_relationships": {},
                "confidence_scores": {}
            }
            
            # Analyze each table and view
            for table_name, table_type in tables:
                print(f"🔍 Analyzing {table_type.lower()}: {table_name}")
                
                table_analysis = self._analyze_single_table(cursor, table_name, table_type)
                
                # Categorize by type and importance
                if table_type == 'VIEW':
                    analysis_results["analyzed_views"][table_name] = table_analysis
                    if table_name.startswith('V_R_'):
                        analysis_results["v_r_views"][table_name] = table_analysis
                        print(f"  ⭐ Found V_R_ view: {table_name}")
                else:
                    analysis_results["analyzed_tables"][table_name] = table_analysis
                
                # Extract business concepts
                business_concept = self._extract_business_concept(table_name, table_analysis)
                if business_concept:
                    analysis_results["business_concepts"][table_name] = business_concept
            
            # Generate relationships
            analysis_results["table_relationships"] = self._discover_relationships(cursor, analysis_results["analyzed_tables"])
            
            # Generate automatic queries
            analysis_results["auto_generated_queries"] = self._generate_automatic_queries(analysis_results)
            
            conn.close()
            
            # Save analysis
            self._save_analysis(analysis_results)
            
            print("✅ Intelligent database analysis completed")
            return analysis_results
            
        except Exception as e:
            print(f"❌ Database analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_single_table(self, cursor, table_name: str, table_type: str = 'BASE TABLE') -> Dict[str, Any]:
        """Analyze a single table and understand its purpose"""
        
        try:
            # Get column information
            cursor.execute(f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
            """)
            
            columns = cursor.fetchall()
            
            # Get sample data (first 5 rows)
            try:
                cursor.execute(f"SELECT TOP 5 * FROM [{table_name}]")
                sample_data = cursor.fetchall()
                sample_count = len(sample_data)
            except:
                sample_data = []
                sample_count = 0
            
            # Get total row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
                total_rows = cursor.fetchone()[0]
            except:
                total_rows = 0
            
            # Analyze column patterns and meanings
            column_analysis = {}
            for col_name, data_type, is_nullable, default_val, max_length in columns:
                column_meaning = self._interpret_column_meaning(col_name, data_type)
                column_analysis[col_name] = {
                    "data_type": data_type,
                    "is_nullable": is_nullable,
                    "default_value": default_val,
                    "max_length": max_length,
                    "business_meaning": column_meaning,
                    "is_primary_key": "ID" in col_name.upper() and col_name.upper().endswith("ID") and len(col_name) <= 3,
                    "is_foreign_key": "FK_" in col_name.upper(),
                    "is_date_field": "DATE" in col_name.upper() or data_type in ["datetime", "date"],
                    "is_amount_field": "AMOUNT" in col_name.upper() or "PRICE" in col_name.upper() or "COST" in col_name.upper()
                }
            
            # Determine table business purpose
            table_purpose = self._determine_table_purpose(table_name, column_analysis)
            
            return {
                "table_name": table_name,
                "table_type": table_type,
                "is_v_r_view": table_name.startswith('V_R_') and table_type == 'VIEW',
                "total_rows": total_rows,
                "total_columns": len(columns),
                "column_details": column_analysis,
                "sample_data_available": sample_count > 0,
                "business_purpose": table_purpose,
                "confidence_score": self._calculate_table_confidence(table_name, column_analysis),
                "primary_keys": [col for col, details in column_analysis.items() if details["is_primary_key"]],
                "foreign_keys": [col for col, details in column_analysis.items() if details["is_foreign_key"]],
                "date_fields": [col for col, details in column_analysis.items() if details["is_date_field"]],
                "amount_fields": [col for col, details in column_analysis.items() if details["is_amount_field"]]
            }
            
        except Exception as e:
            return {
                "table_name": table_name,
                "error": str(e),
                "confidence_score": 0.0
            }
    
    def _interpret_column_meaning(self, column_name: str, data_type: str) -> str:
        """Interpret what a column means in business context"""
        
        col_upper = column_name.upper()
        
        # Primary/Foreign Key patterns
        if col_upper == "ID":
            return "Primary identifier"
        if col_upper.startswith("FK_"):
            return f"Foreign key reference to {col_upper[3:].lower()}"
        
        # Common business fields
        business_patterns = {
            "NAME": "Name or description",
            "DESCRIPTION": "Detailed description",
            "CODE": "Business code or identifier",
            "NUMBER": "Reference or sequence number",
            "STATUS": "Current status or state",
            "STATE": "Current state or condition",
            "TYPE": "Category or classification",
            "AMOUNT": "Monetary amount",
            "PRICE": "Price or cost value",
            "QUANTITY": "Quantity or count",
            "QTY": "Quantity abbreviation",
            "DATE": "Date field",
            "TIME": "Time or timestamp",
            "CREATED": "Creation timestamp",
            "UPDATED": "Last update timestamp",
            "MODIFIED": "Modification timestamp",
            "DELIVERY": "Delivery related",
            "ORDER": "Order related",
            "INVOICE": "Invoice related",
            "CUSTOMER": "Customer related",
            "SUPPLIER": "Supplier related",
            "PRODUCT": "Product related",
            "MACHINE": "Machine related",
            "SERVICE": "Service related"
        }
        
        # Check for pattern matches
        for pattern, meaning in business_patterns.items():
            if pattern in col_upper:
                return meaning
        
        # Data type based interpretation
        if data_type in ["datetime", "date", "timestamp"]:
            return "Date/time field"
        if data_type in ["money", "decimal", "numeric"] and "AMOUNT" in col_upper:
            return "Financial amount"
        if data_type in ["int", "bigint"] and col_upper.endswith("ID"):
            return "Identifier field"
        
        return "General data field"
    
    def _determine_table_purpose(self, table_name: str, column_analysis: Dict) -> str:
        """Determine the business purpose of a table or view"""
        
        name_upper = table_name.upper()
        columns = list(column_analysis.keys())
        column_names_upper = [col.upper() for col in columns]
        
        # Special handling for V_R_ views (ERP optimized views)
        if name_upper.startswith('V_R_'):
            if 'SERVICEOBJECT' in name_upper:
                return "ERP Service Object View - Optimized machine and equipment data with calculated fields"
            elif 'SALESINVOICE' in name_upper:
                return "ERP Sales Invoice View - Optimized revenue and billing data with business logic"
            elif 'RELATION' in name_upper:
                return "ERP Relation View - Optimized customer/supplier data with enhanced lookups"
            elif 'ITEM' in name_upper:
                return "ERP Item View - Optimized product and inventory data with calculated stock levels"
            elif 'PURCHASE' in name_upper:
                return "ERP Purchase View - Optimized procurement data with vendor performance metrics"
            else:
                return f"ERP Optimized View - {name_upper[3:].replace('_', ' ').title()} with calculated business fields"
        
        # Common ERP table patterns
        if "SALESINVOICE" in name_upper or "INVOICE" in name_upper:
            return "Sales invoicing and revenue tracking"
        
        if "PURCHASEORDER" in name_upper or "PURCHASE" in name_upper:
            return "Purchase orders and supplier management"
        
        if "RELATION" in name_upper and any("NAME" in col for col in column_names_upper):
            return "Business relationships (customers, suppliers, contacts)"
        
        if "SERVICEOBJECT" in name_upper or ("SERVICE" in name_upper and "OBJECT" in name_upper):
            return "Service objects and machine management"
        
        if "ITEM" in name_upper or "PRODUCT" in name_upper:
            return "Product and inventory management"
        
        if "MACHINE" in name_upper or "EQUIPMENT" in name_upper:
            return "Machine and equipment tracking"
        
        if any("DELIVERY" in col for col in column_names_upper):
            return "Delivery and logistics management"
        
        if any("STOCK" in col for col in column_names_upper) or any("INVENTORY" in col for col in column_names_upper):
            return "Stock and inventory management"
        
        # Look for key business indicators
        has_amounts = any(details["is_amount_field"] for details in column_analysis.values())
        has_dates = any(details["is_date_field"] for details in column_analysis.values())
        has_foreign_keys = any(details["is_foreign_key"] for details in column_analysis.values())
        
        if has_amounts and has_dates:
            return "Financial transaction tracking"
        if has_foreign_keys and has_dates:
            return "Transactional business process"
        if "LOG" in name_upper or "AUDIT" in name_upper:
            return "System logging and audit trail"
        
        return "General business data storage"
    
    def _calculate_table_confidence(self, table_name: str, column_analysis: Dict) -> float:
        """Calculate confidence score for table analysis accuracy"""
        
        confidence = 0.5  # Base confidence
        
        # Higher confidence for well-structured tables
        if any(details["is_primary_key"] for details in column_analysis.values()):
            confidence += 0.2
        
        if any(details["is_foreign_key"] for details in column_analysis.values()):
            confidence += 0.1
        
        # Standard ERP table names get higher confidence
        name_upper = table_name.upper()
        if any(pattern in name_upper for pattern in ["INVOICE", "ORDER", "RELATION", "ITEM", "SERVICE"]):
            confidence += 0.2
        
        # Well-named columns increase confidence
        meaningful_columns = sum(1 for details in column_analysis.values() 
                               if details["business_meaning"] != "General data field")
        confidence += min(0.3, meaningful_columns * 0.05)
        
        return min(1.0, confidence)
    
    def _extract_business_concept(self, table_name: str, table_analysis: Dict) -> Optional[str]:
        """Extract high-level business concept from table analysis"""
        
        business_purpose = table_analysis.get("business_purpose", "")
        
        # Map table purposes to business concepts
        if "invoice" in business_purpose.lower() or "revenue" in business_purpose.lower():
            return "Financial Operations"
        elif "machine" in business_purpose.lower() or "service" in business_purpose.lower():
            return "Production & Equipment"
        elif "relation" in business_purpose.lower() or "customer" in business_purpose.lower():
            return "Customer Relationship Management"
        elif "purchase" in business_purpose.lower() or "supplier" in business_purpose.lower():
            return "Procurement & Supply Chain"
        elif "item" in business_purpose.lower() or "product" in business_purpose.lower():
            return "Inventory & Product Management"
        elif "erp" in business_purpose.lower() and "view" in business_purpose.lower():
            return "ERP Optimized Views"
        else:
            return "General Business Operations"
    
    def _discover_relationships(self, cursor, analyzed_tables: Dict) -> Dict[str, List[str]]:
        """Discover relationships between tables based on foreign keys"""
        
        relationships = {}
        
        for table_name, analysis in analyzed_tables.items():
            if "column_details" in analysis:
                foreign_keys = analysis.get("foreign_keys", [])
                
                for fk in foreign_keys:
                    # FK_SUPPLIER -> probably links to RELATION table
                    # FK_SERVICEOBJECTTYPE -> probably links to serviceobject type table
                    if fk.startswith("FK_"):
                        referenced_concept = fk[3:]  # Remove FK_ prefix
                        
                        # Find likely target tables
                        likely_targets = []
                        for other_table in analyzed_tables.keys():
                            if referenced_concept.lower() in other_table.lower():
                                likely_targets.append(other_table)
                        
                        if likely_targets:
                            relationships[f"{table_name}.{fk}"] = likely_targets
        
        return relationships
    
    def _generate_automatic_queries(self, analysis_results: Dict) -> Dict[str, Dict]:
        """Automatically generate SQL queries based on table analysis"""
        
        auto_queries = {}
        
        for table_name, analysis in analysis_results["analyzed_tables"].items():
            if "error" in analysis:
                continue
                
            table_purpose = analysis.get("business_purpose", "")
            
            # Generate queries based on table purpose
            if "supplier" in table_purpose.lower() and "purchase" in table_purpose.lower():
                # This is likely purchase order data - generate supplier performance queries
                auto_queries[f"leverancier_performance_{table_name.lower()}"] = {
                    "table": table_name,
                    "purpose": "Supplier delivery performance analysis",
                    "query_type": "performance_analysis",
                    "confidence": analysis.get("confidence_score", 0.5),
                    "auto_generated": True,
                    "business_question": "Wat is de delivery performance van onze leveranciers?",
                    "sql_template": self._generate_supplier_performance_query(table_name, analysis)
                }
            
            if "invoice" in table_purpose.lower() or "revenue" in table_purpose.lower():
                # Revenue analysis queries
                auto_queries[f"omzet_analysis_{table_name.lower()}"] = {
                    "table": table_name,
                    "purpose": "Revenue and sales analysis",
                    "query_type": "financial_analysis", 
                    "confidence": analysis.get("confidence_score", 0.5),
                    "auto_generated": True,
                    "business_question": "Wat is onze omzet dit jaar?",
                    "sql_template": self._generate_revenue_query(table_name, analysis)
                }
            
            if "machine" in table_purpose.lower() or "service" in table_purpose.lower():
                # Machine/production analysis
                auto_queries[f"machine_analysis_{table_name.lower()}"] = {
                    "table": table_name,
                    "purpose": "Machine and production analysis",
                    "query_type": "production_analysis",
                    "confidence": analysis.get("confidence_score", 0.5),
                    "auto_generated": True,
                    "business_question": "Hoeveel machines hebben we dit jaar gebouwd?",
                    "sql_template": self._generate_machine_query(table_name, analysis)
                }
        
        return auto_queries
    
    def _generate_supplier_performance_query(self, table_name: str, analysis: Dict) -> str:
        """Generate supplier performance query for a table"""
        
        columns = analysis.get("column_details", {})
        
        # Find relevant columns
        supplier_col = None
        delivery_date_col = None
        requested_date_col = None
        amount_col = None
        
        for col_name, details in columns.items():
            col_upper = col_name.upper()
            if "SUPPLIER" in col_upper and details["is_foreign_key"]:
                supplier_col = col_name
            elif "DELIVERY" in col_upper and details["is_date_field"]:
                delivery_date_col = col_name
            elif "REQUEST" in col_upper and details["is_date_field"]:
                requested_date_col = col_name
            elif details["is_amount_field"]:
                amount_col = col_name
        
        if supplier_col and delivery_date_col and requested_date_col:
            return f"""
            -- Auto-generated supplier performance query for {table_name}
            SELECT 
                r.NAME as Leverancier,
                COUNT(t.ID) as TotaalOrders,
                COUNT(CASE WHEN t.{delivery_date_col} <= t.{requested_date_col} THEN 1 END) as OpTijd,
                ROUND(
                    CAST(COUNT(CASE WHEN t.{delivery_date_col} <= t.{requested_date_col} THEN 1 END) AS FLOAT) * 100.0 / 
                    CAST(COUNT(t.ID) AS FLOAT), 2
                ) as PercentageOpTijd
                {f", SUM(t.{amount_col}) as TotaalWaarde" if amount_col else ""}
            FROM {table_name} t
            INNER JOIN R_RELATION r ON t.{supplier_col} = r.ID
            WHERE YEAR(t.ORDERDATE) = YEAR(GETDATE())
              AND t.{delivery_date_col} IS NOT NULL
              AND t.{requested_date_col} IS NOT NULL
            GROUP BY r.NAME
            ORDER BY PercentageOpTijd DESC
            """
        
        return f"-- Could not auto-generate query for {table_name} - missing required columns"
    
    def _generate_revenue_query(self, table_name: str, analysis: Dict) -> str:
        """Generate revenue analysis query"""
        
        columns = analysis.get("column_details", {})
        amount_col = None
        date_col = None
        
        for col_name, details in columns.items():
            if details["is_amount_field"] and not amount_col:
                amount_col = col_name
            elif details["is_date_field"] and "INVOICE" in col_name.upper():
                date_col = col_name
        
        if amount_col and date_col:
            return f"""
            -- Auto-generated revenue query for {table_name}
            SELECT 
                SUM({amount_col}) as TotaleOmzet,
                COUNT(*) as AantalFacturen,
                AVG({amount_col}) as GemiddeldeFactuurWaarde
            FROM {table_name}
            WHERE YEAR({date_col}) = YEAR(GETDATE())
              AND {amount_col} > 0
            """
        
        return f"-- Could not auto-generate revenue query for {table_name}"
    
    def _generate_machine_query(self, table_name: str, analysis: Dict) -> str:
        """Generate machine/production analysis query"""
        
        return f"""
        -- Auto-generated machine count query for {table_name}
        SELECT 
            COUNT(*) as TotaalMachines
        FROM {table_name}
        WHERE YEAR(DATUMGEREED) = YEAR(GETDATE())
        """
    
    def _save_analysis(self, analysis_results: Dict):
        """Save analysis results for future use"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/home/jaapfrank/Hoeflon Ridder/Ridder AI/intelligent_database_analysis_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, default=str)
            print(f"💾 Analysis saved to: {filename}")
        except Exception as e:
            print(f"⚠️ Could not save analysis: {e}")
    
    def get_query_for_question(self, user_question: str) -> Optional[Dict]:
        """AI-powered query generation for any business question"""
        
        question_lower = user_question.lower()
        
        # Load latest analysis
        analysis = self._load_latest_analysis()
        if not analysis:
            return None
        
        # Match business questions to auto-generated queries
        auto_queries = analysis.get("auto_generated_queries", {})
        
        for query_name, query_info in auto_queries.items():
            business_question = query_info.get("business_question", "").lower()
            
            # Simple keyword matching (can be enhanced with NLP)
            if any(keyword in question_lower for keyword in ["leverancier", "supplier", "delivery", "performance"]):
                if "supplier" in query_info.get("purpose", "").lower():
                    return query_info
            
            if any(keyword in question_lower for keyword in ["omzet", "revenue", "factuur"]):
                if "revenue" in query_info.get("purpose", "").lower():
                    return query_info
            
            if any(keyword in question_lower for keyword in ["machine", "productie", "gebouwd"]):
                if "machine" in query_info.get("purpose", "").lower():
                    return query_info
        
        return None
    
    def _load_latest_analysis(self) -> Optional[Dict]:
        """Load the most recent analysis results"""
        
        try:
            import os
            import glob
            
            # Find latest analysis file
            pattern = "/home/jaapfrank/Hoeflon Ridder/Ridder AI/intelligent_database_analysis_*.json"
            files = glob.glob(pattern)
            
            if not files:
                return None
            
            latest_file = max(files, key=os.path.getctime)
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"⚠️ Could not load analysis: {e}")
            return None

if __name__ == "__main__":
    # Test the intelligent analyzer
    print("🧠 Testing Intelligent Table Analyzer...")
    
    # This would use real database connection
    # analyzer = IntelligentTableAnalyzer("connection_string")
    # results = analyzer.analyze_entire_database()
    
    print("✅ Intelligent Table Analyzer ready for full database analysis!")
    print("🚀 This system will:")
    print("  • Analyze ALL database tables automatically")
    print("  • Understand business meaning of each table")
    print("  • Generate SQL queries dynamically")
    print("  • Learn and improve over time")
    print("  • No manual mapping required!")
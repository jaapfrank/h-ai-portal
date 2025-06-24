#!/usr/bin/env python3
"""
Dynamic Table Selector - Automatically selects V_R_ views when available
Deze module zorgt ervoor dat het systeem automatisch V_R_ views gebruikt 
die meer complete data bevatten dan standaard R_ tabellen.
"""

import re
from typing import Dict, List, Optional, Tuple
import pyodbc

class DynamicTableSelector:
    """Dynamisch selecteren van de beste tabellen/views voor queries"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.table_hierarchy = {}
        self.available_tables = set()
        self.view_mappings = {}
        self._discover_tables()
    
    def _discover_tables(self):
        """Ontdek alle beschikbare tabellen en views"""
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Krijg alle tabellen en views
            cursor.execute("""
                SELECT TABLE_NAME, TABLE_TYPE 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME LIKE 'R_%' 
                   OR TABLE_NAME LIKE 'V_R_%' 
                   OR TABLE_NAME LIKE 'X_R_%'
                ORDER BY TABLE_NAME
            """)
            
            for row in cursor.fetchall():
                table_name = row.TABLE_NAME
                table_type = row.TABLE_TYPE
                self.available_tables.add(table_name)
                
                # Map V_R_ views to their base R_ tables
                if table_name.startswith('V_R_'):
                    base_table = table_name[2:]  # Remove 'V_'
                    self.view_mappings[base_table] = table_name
                    print(f"📋 Mapped {base_table} -> {table_name}")
            
            conn.close()
            print(f"🔍 Discovered {len(self.available_tables)} tables/views")
            
        except Exception as e:
            print(f"❌ Error discovering tables: {e}")
    
    def get_best_table(self, base_table: str) -> str:
        """Krijg de beste tabel voor de gegeven base table"""
        # Eerst zoeken naar V_R_ view (heeft meeste data)
        if base_table in self.view_mappings:
            best_table = self.view_mappings[base_table]
            print(f"🚀 Using enhanced view: {best_table} (instead of {base_table})")
            return best_table
        
        # Dan X_R_ extension tabel
        x_table = f"X_{base_table}"
        if x_table in self.available_tables:
            print(f"🔧 Using extension table: {x_table} (instead of {base_table})")
            return x_table
        
        # Als fallback de originele tabel
        if base_table in self.available_tables:
            print(f"📊 Using base table: {base_table}")
            return base_table
        
        print(f"⚠️ Table not found: {base_table}")
        return base_table
    
    def get_enhanced_columns(self, table: str) -> Dict[str, str]:
        """Krijg enhanced kolommen voor een tabel"""
        enhanced_columns = {}
        
        try:
            conn = pyodbc.connect(self.connection_string)
            cursor = conn.cursor()
            
            # Krijg alle kolommen van de tabel
            cursor.execute(f"""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = '{table}'
                ORDER BY ORDINAL_POSITION
            """)
            
            for row in cursor.fetchall():
                col_name = row.COLUMN_NAME
                data_type = row.DATA_TYPE
                
                # Map enhanced kolommen
                if 'DATUM' in col_name and 'GEREED' in col_name:
                    enhanced_columns['production_date'] = col_name
                elif 'PRODUCTIE' in col_name and 'STATUS' in col_name:
                    enhanced_columns['production_status'] = col_name
                elif col_name == 'DELIVERYDATE':
                    enhanced_columns['delivery_date'] = col_name
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error getting columns for {table}: {e}")
        
        return enhanced_columns
    
    def optimize_query(self, original_query: str) -> str:
        """Optimaliseer query door beste tabellen te gebruiken"""
        optimized_query = original_query
        
        # Vind alle R_ tabellen in de query
        r_table_pattern = r'\bR_[A-Z_]+\b'
        r_tables = re.findall(r_table_pattern, original_query)
        
        for r_table in set(r_tables):
            best_table = self.get_best_table(r_table)
            if best_table != r_table:
                optimized_query = optimized_query.replace(r_table, best_table)
                print(f"🔄 Optimized: {r_table} -> {best_table}")
        
        # Optimaliseer kolommen gebaseerd op beschikbare enhanced kolommen
        for r_table in set(r_tables):
            best_table = self.get_best_table(r_table)
            enhanced_cols = self.get_enhanced_columns(best_table)
            
            # Vervang DELIVERYDATE met DATUMGEREED als beschikbaar
            if 'production_date' in enhanced_cols and 'DELIVERYDATE' in optimized_query:
                optimized_query = optimized_query.replace('DELIVERYDATE', enhanced_cols['production_date'])
                print(f"📅 Enhanced date column: DELIVERYDATE -> {enhanced_cols['production_date']}")
            
            # Voeg PRODUCTIESTATUS filter toe als beschikbaar
            if 'production_status' in enhanced_cols and best_table.startswith('V_R_'):
                # Voeg PRODUCTIESTATUS = 6 toe aan WHERE clause
                if 'WHERE ' in optimized_query and 'PRODUCTIESTATUS' not in optimized_query:
                    where_pos = optimized_query.find('WHERE ')
                    insert_pos = optimized_query.find('AND', where_pos)
                    if insert_pos == -1:
                        insert_pos = len(optimized_query.rstrip())
                        if optimized_query.rstrip().endswith('"'):
                            insert_pos -= 1
                    
                    status_filter = f"\n                    AND so.{enhanced_cols['production_status']} = 6"
                    optimized_query = optimized_query[:insert_pos] + status_filter + optimized_query[insert_pos:]
                    print(f"✅ Added production status filter: {enhanced_cols['production_status']} = 6")
        
        return optimized_query
    
    def explain_optimization(self, original_query: str, optimized_query: str) -> str:
        """Leg optimalisaties uit"""
        if original_query == optimized_query:
            return "Geen optimalisaties nodig."
        
        explanation = "🚀 **Query Optimalisaties:**\n"
        
        # Tabel wijzigingen
        orig_tables = set(re.findall(r'\bR_[A-Z_]+\b', original_query))
        opt_tables = set(re.findall(r'\b[VX]?_?R_[A-Z_]+\b', optimized_query))
        
        for orig_table in orig_tables:
            best_table = self.get_best_table(orig_table)
            if best_table != orig_table:
                explanation += f"• **{orig_table}** → **{best_table}** (enhanced view met meer data)\n"
        
        # Kolom wijzigingen
        if 'DATUMGEREED' in optimized_query and 'DATUMGEREED' not in original_query:
            explanation += "• **DELIVERYDATE** → **DATUMGEREED** (preciezere productiedatum)\n"
        
        if 'PRODUCTIESTATUS = 6' in optimized_query:
            explanation += "• **Toegevoegd: PRODUCTIESTATUS = 6** (alleen gereed geproduceerde machines)\n"
        
        return explanation
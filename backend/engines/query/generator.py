#!/usr/bin/env python3
"""
INTELLIGENT QUERY GENERATOR - DAY 1-2
Dynamic SQL generation without hardcoded patterns
Team: BROER (Lead), ERIK, OOM
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from adaptive_core_architecture import DatabaseSchema, QuestionIntent

@dataclass
class GeneratedQuery:
    """Intelligent query result"""
    sql: str
    parameters: Dict[str, Any]
    explanation: str
    confidence: float
    estimated_rows: int

class IntelligentQueryGenerator:
    """BROER's Dynamic Query Generation - No hardcoded SQL"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    async def generate_query(self, intent: QuestionIntent, schema: DatabaseSchema) -> GeneratedQuery:
        """Generate optimal SQL based on intent and schema understanding"""
        self.logger.info(f"🔧 BROER: Generating query for {intent.intent_type} intent")
        
        # 1. Find relevant tables based on entities
        relevant_tables = await self._find_relevant_tables(intent, schema)
        
        # 2. Build SELECT clause based on intent
        select_clause = await self._build_select_clause(intent, relevant_tables, schema)
        
        # 3. Build FROM clause with intelligent joins
        from_clause = await self._build_from_clause(relevant_tables, schema)
        
        # 4. Build WHERE clause with filters and time constraints
        where_clause = await self._build_where_clause(intent, relevant_tables, schema)
        
        # 5. Build GROUP BY and ORDER BY clauses
        group_clause = await self._build_group_clause(intent, relevant_tables)
        order_clause = await self._build_order_clause(intent)
        
        # 6. Combine into final query
        sql_parts = [select_clause, from_clause]
        if where_clause:
            sql_parts.append(where_clause)
        if group_clause:
            sql_parts.append(group_clause)
        if order_clause:
            sql_parts.append(order_clause)
            
        sql = " ".join(sql_parts)
        
        # 7. Generate explanation
        explanation = await self._generate_explanation(intent, relevant_tables)
        
        # 8. Estimate result size
        estimated_rows = await self._estimate_result_size(relevant_tables, intent)
        
        query = GeneratedQuery(
            sql=sql,
            parameters={},
            explanation=explanation,
            confidence=intent.confidence,
            estimated_rows=estimated_rows
        )
        
        self.logger.info(f"✅ BROER: Query generated - {len(sql)} chars, {estimated_rows} estimated rows")
        
        return query
    
    async def _find_relevant_tables(self, intent: QuestionIntent, schema: DatabaseSchema) -> List[str]:
        """Intelligently find tables relevant to the question"""
        relevant_tables = []
        
        # Match entities to tables
        for entity in intent.entities:
            if entity in schema.business_entities.values():
                # Find tables that map to this business entity
                for table_name, business_type in schema.business_entities.items():
                    if business_type == entity:
                        relevant_tables.append(table_name)
            elif '.' in entity:
                # Direct table.column reference
                table_name = entity.split('.')[0]
                if table_name in schema.tables:
                    relevant_tables.append(table_name)
        
        # If no specific entities found, use heuristics based on intent
        if not relevant_tables:
            relevant_tables = await self._heuristic_table_selection(intent, schema)
            
        return list(set(relevant_tables))  # Remove duplicates
    
    async def _heuristic_table_selection(self, intent: QuestionIntent, schema: DatabaseSchema) -> List[str]:
        """Fallback table selection using intelligent heuristics"""
        tables = []
        
        if intent.intent_type in ['count', 'sum']:
            # Look for tables with numeric columns
            for table_name, table_info in schema.tables.items():
                if table_info['row_count'] > 0:  # Has data
                    tables.append(table_name)
                    
        elif intent.intent_type == 'top':
            # Look for tables with ranking-worthy columns
            for metric in schema.key_metrics:
                table_name = metric.split('.')[0]
                tables.append(table_name)
        
        return tables[:3]  # Limit to top 3 candidates
    
    async def _build_select_clause(self, intent: QuestionIntent, tables: List[str], schema: DatabaseSchema) -> str:
        """Build intelligent SELECT clause"""
        
        if intent.intent_type == 'count':
            if intent.aggregation:
                # Count with grouping
                group_col = await self._find_grouping_column(intent.aggregation, tables, schema)
                return f"SELECT {group_col}, COUNT(*) as Total"
            else:
                # Simple count
                return "SELECT COUNT(*) as Total"
                
        elif intent.intent_type == 'sum':
            # Find numeric column to sum
            sum_col = await self._find_sum_column(tables, schema)
            if intent.aggregation:
                group_col = await self._find_grouping_column(intent.aggregation, tables, schema)
                return f"SELECT {group_col}, SUM({sum_col}) as Total"
            else:
                return f"SELECT SUM({sum_col}) as Total"
                
        elif intent.intent_type == 'top':
            # Top records with ranking
            rank_col = await self._find_ranking_column(tables, schema)
            group_col = await self._find_grouping_column('customer', tables, schema)  # Default to customer
            return f"SELECT TOP 10 {group_col}, {rank_col}"
            
        else:
            # General select
            key_cols = await self._find_key_columns(tables, schema)
            return f"SELECT {', '.join(key_cols[:5])}"  # Top 5 columns
    
    async def _build_from_clause(self, tables: List[str], schema: DatabaseSchema) -> str:
        """Build FROM clause with intelligent joins"""
        if len(tables) == 1:
            return f"FROM {tables[0]}"
        
        # Multi-table query - find optimal join path
        joins = await self._find_join_path(tables, schema)
        
        from_clause = f"FROM {tables[0]}"
        for join in joins:
            from_clause += f" {join}"
            
        return from_clause
    
    async def _find_join_path(self, tables: List[str], schema: DatabaseSchema) -> List[str]:
        """Find optimal join path between tables"""
        joins = []
        
        for i in range(1, len(tables)):
            # Find relationship between tables[0] and tables[i]
            join_condition = None
            
            for rel in schema.relationships:
                if (rel['from_table'] == tables[0] and rel['to_table'] == tables[i]) or \
                   (rel['from_table'] == tables[i] and rel['to_table'] == tables[0]):
                    join_condition = f"{rel['from_table']}.{rel['from_column']} = {rel['to_table']}.{rel['to_column']}"
                    break
            
            if join_condition:
                joins.append(f"INNER JOIN {tables[i]} ON {join_condition}")
            else:
                # Fallback - look for common column names
                common_col = await self._find_common_column(tables[0], tables[i], schema)
                if common_col:
                    joins.append(f"INNER JOIN {tables[i]} ON {tables[0]}.{common_col} = {tables[i]}.{common_col}")
                    
        return joins
    
    async def _build_where_clause(self, intent: QuestionIntent, tables: List[str], schema: DatabaseSchema) -> Optional[str]:
        """Build WHERE clause with time filters and conditions"""
        conditions = []
        
        # Time frame conditions
        if intent.time_frame:
            time_condition = await self._build_time_condition(intent.time_frame, tables, schema)
            if time_condition:
                conditions.append(time_condition)
        
        # Entity filters
        for filter_key, filter_value in intent.filters.items():
            if filter_value != "EXTRACTED_VALUE":  # Skip placeholder values
                conditions.append(f"{filter_key} = '{filter_value}'")
        
        # Business logic filters (exclude internal sales, etc.)
        business_filters = await self._add_business_filters(tables, schema)
        conditions.extend(business_filters)
        
        if conditions:
            return f"WHERE {' AND '.join(conditions)}"
        
        return None
    
    async def _build_time_condition(self, time_frame: str, tables: List[str], schema: DatabaseSchema) -> Optional[str]:
        """Build time-based WHERE condition"""
        # Find date column in the tables
        date_column = None
        
        for table in tables:
            for time_col in schema.time_columns:
                if time_col.startswith(f"{table}."):
                    date_column = time_col
                    break
            if date_column:
                break
        
        if not date_column:
            return None
            
        if time_frame == 'this_year':
            return f"YEAR({date_column}) = YEAR(GETDATE())"
        elif time_frame == 'last_year':
            return f"YEAR({date_column}) = YEAR(GETDATE()) - 1"
        elif time_frame == 'this_month':
            return f"YEAR({date_column}) = YEAR(GETDATE()) AND MONTH({date_column}) = MONTH(GETDATE())"
        elif time_frame == 'last_month':
            return f"YEAR({date_column}) = YEAR(GETDATE()) AND MONTH({date_column}) = MONTH(GETDATE()) - 1"
            
        return None
    
    async def _add_business_filters(self, tables: List[str], schema: DatabaseSchema) -> List[str]:
        """Add business logic filters (exclude internal sales, etc.)"""
        filters = []
        
        # Hoeflon-specific: exclude internal sales
        for table in tables:
            if 'relation' in table.lower() or 'customer' in table.lower():
                filters.append(f"{table}.ID NOT IN (7,6736,5910,5219,1114,6109,3366,8165)")
        
        return filters
    
    async def _build_group_clause(self, intent: QuestionIntent, tables: List[str]) -> Optional[str]:
        """Build GROUP BY clause"""
        if intent.aggregation and intent.intent_type in ['count', 'sum', 'top']:
            group_col = await self._find_grouping_column(intent.aggregation, tables, None)
            if group_col:
                return f"GROUP BY {group_col}"
        
        return None
    
    async def _build_order_clause(self, intent: QuestionIntent) -> Optional[str]:
        """Build ORDER BY clause"""
        if intent.intent_type == 'top':
            return "ORDER BY Total DESC"
        elif intent.intent_type in ['count', 'sum']:
            return "ORDER BY Total DESC"
            
        return None
    
    # Helper methods
    async def _find_grouping_column(self, aggregation: str, tables: List[str], schema: Optional[DatabaseSchema]) -> str:
        """Find appropriate column for grouping"""
        # Default grouping columns based on aggregation type
        if aggregation == 'customer':
            return f"{tables[0]}.NAME" if 'relation' in tables[0].lower() else f"{tables[0]}.CustomerName"
        elif aggregation == 'month':
            return f"MONTH({tables[0]}.Date)"
        elif aggregation == 'type':
            return f"{tables[0]}.Type"
        else:
            return f"{tables[0]}.ID"
    
    async def _find_sum_column(self, tables: List[str], schema: DatabaseSchema) -> str:
        """Find numeric column suitable for summing"""
        for metric in schema.key_metrics:
            if any(table in metric for table in tables):
                return metric.split('.')[1]  # Return column name
        
        # Fallback
        return "Amount"
    
    async def _find_ranking_column(self, tables: List[str], schema: DatabaseSchema) -> str:
        """Find column suitable for ranking"""
        return await self._find_sum_column(tables, schema)
    
    async def _find_key_columns(self, tables: List[str], schema: DatabaseSchema) -> List[str]:
        """Find important columns for general queries"""
        columns = []
        
        for table in tables:
            if table in schema.tables:
                table_cols = list(schema.tables[table]['columns'].keys())[:3]
                columns.extend([f"{table}.{col}" for col in table_cols])
        
        return columns
    
    async def _find_common_column(self, table1: str, table2: str, schema: DatabaseSchema) -> Optional[str]:
        """Find common column between two tables for joining"""
        if table1 not in schema.tables or table2 not in schema.tables:
            return None
            
        cols1 = set(schema.tables[table1]['columns'].keys())
        cols2 = set(schema.tables[table2]['columns'].keys())
        
        common = cols1.intersection(cols2)
        if common:
            return list(common)[0]
            
        return None
    
    async def _generate_explanation(self, intent: QuestionIntent, tables: List[str]) -> str:
        """Generate human-readable explanation of the query"""
        return f"Analyzing {intent.intent_type} query across {', '.join(tables)} for entities: {', '.join(intent.entities)}"
    
    async def _estimate_result_size(self, tables: List[str], intent: QuestionIntent) -> int:
        """Estimate number of rows in result"""
        if intent.intent_type in ['count', 'sum'] and not intent.aggregation:
            return 1  # Single aggregate result
        elif intent.intent_type == 'top':
            return 10  # Top 10 results
        else:
            return 50  # Default estimate
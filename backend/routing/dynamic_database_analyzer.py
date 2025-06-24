#!/usr/bin/env python3
"""
Dynamic Database Analyzer - Self-Improving Database Understanding
Uses sqlacodegen, ydata-profiling, and great-expectations for deep database insights
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.engine import Engine
import ydata_profiling
import sweetviz as sv
import great_expectations as gx
from great_expectations.core import ExpectationSuite

@dataclass
class TableInsight:
    """Rich insights about a database table"""
    table_name: str
    row_count: int
    column_count: int
    primary_keys: List[str]
    foreign_keys: List[Dict[str, str]]
    business_meaning: str
    data_quality_score: float
    common_queries: List[str]
    relationships: List[str]
    last_updated: str
    profiling_report_path: Optional[str] = None
    expectations: List[Dict[str, Any]] = None

class DynamicDatabaseAnalyzer:
    """Analyzes and learns about database structure and content dynamically"""
    
    def __init__(self, connection_string: str, output_dir: str = "./database_insights"):
        self.engine = create_engine(connection_string)
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.insights_cache = {}
        self.learning_history = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/profiles", exist_ok=True)
        os.makedirs(f"{output_dir}/expectations", exist_ok=True)
    
    def analyze_all_tables(self, sample_size: int = 1000) -> Dict[str, TableInsight]:
        """Perform comprehensive analysis of all tables"""
        self.logger.info("Starting comprehensive database analysis...")
        
        # Get all tables using SQLAlchemy inspection
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        
        self.logger.info(f"Found {len(table_names)} tables to analyze")
        
        insights = {}
        for table_name in table_names:
            try:
                self.logger.info(f"Analyzing table: {table_name}")
                insight = self._analyze_single_table(table_name, sample_size)
                insights[table_name] = insight
                
                # Save individual insight
                self._save_table_insight(insight)
                
            except Exception as e:
                self.logger.error(f"Failed to analyze table {table_name}: {e}")
                continue
        
        # Save comprehensive insights
        self._save_comprehensive_insights(insights)
        
        return insights
    
    def _analyze_single_table(self, table_name: str, sample_size: int) -> TableInsight:
        """Deep analysis of a single table"""
        
        # Basic metadata
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)['constrained_columns']
        foreign_keys = [
            {
                'column': fk['constrained_columns'][0],
                'referenced_table': fk['referred_table'],
                'referenced_column': fk['referred_columns'][0]
            }
            for fk in inspector.get_foreign_keys(table_name)
        ]
        
        # Get sample data for analysis
        query = f"SELECT TOP {sample_size} * FROM {table_name}"
        df = pd.read_sql(query, self.engine)
        
        row_count = self._get_row_count(table_name)
        
        # Generate data profiling report
        profile_path = self._generate_data_profile(table_name, df)
        
        # Generate business meaning using AI analysis
        business_meaning = self._generate_business_meaning(table_name, columns, df.head())
        
        # Calculate data quality score
        data_quality_score = self._calculate_data_quality_score(df)
        
        # Generate common queries
        common_queries = self._generate_common_queries(table_name, columns, foreign_keys)
        
        # Find relationships
        relationships = self._find_table_relationships(table_name, foreign_keys)
        
        # Create expectations for data validation
        expectations = self._create_table_expectations(table_name, df)
        
        return TableInsight(
            table_name=table_name,
            row_count=row_count,
            column_count=len(columns),
            primary_keys=primary_keys,
            foreign_keys=foreign_keys,
            business_meaning=business_meaning,
            data_quality_score=data_quality_score,
            common_queries=common_queries,
            relationships=relationships,
            last_updated=datetime.now().isoformat(),
            profiling_report_path=profile_path,
            expectations=expectations
        )
    
    def _get_row_count(self, table_name: str) -> int:
        """Get total row count for table"""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = pd.read_sql(query, self.engine)
        return int(result.iloc[0]['count'])
    
    def _generate_data_profile(self, table_name: str, df: pd.DataFrame) -> str:
        """Generate comprehensive data profiling report"""
        try:
            # Use ydata-profiling for comprehensive analysis
            profile = ydata_profiling.ProfileReport(
                df, 
                title=f"Data Profile: {table_name}",
                explorative=True,
                minimal=False
            )
            
            profile_path = f"{self.output_dir}/profiles/{table_name}_profile.html"
            profile.to_file(profile_path)
            
            return profile_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate profile for {table_name}: {e}")
            return None
    
    def _generate_business_meaning(self, table_name: str, columns: List[Dict], sample_data: pd.DataFrame) -> str:
        """Generate business meaning using pattern analysis"""
        
        # Analyze table name patterns
        name_indicators = {
            'R_': 'Master data table (Relations, Items, etc.)',
            'U_': 'User/Custom table extension',
            'SALES': 'Sales-related transactions',
            'INVOICE': 'Invoicing and billing data',
            'ITEM': 'Product/Item master data',
            'RELATION': 'Customer/Supplier relationships',
            'SERVICE': 'Service management data',
            'STOCK': 'Inventory management',
            'SERIAL': 'Serial number tracking'
        }
        
        business_meaning = f"Table: {table_name}\n"
        
        # Pattern-based meaning
        for pattern, meaning in name_indicators.items():
            if pattern in table_name.upper():
                business_meaning += f"Category: {meaning}\n"
                break
        
        # Column analysis
        column_types = []
        for col in columns:
            col_name = col['name']
            col_type = str(col['type'])
            
            if 'DATE' in col_name.upper():
                column_types.append(f"Temporal: {col_name} ({col_type})")
            elif 'FK_' in col_name.upper():
                column_types.append(f"Foreign Key: {col_name} -> references other table")
            elif 'PK_' in col_name.upper():
                column_types.append(f"Primary Key: {col_name}")
            elif 'AMOUNT' in col_name.upper() or 'PRICE' in col_name.upper():
                column_types.append(f"Financial: {col_name} ({col_type})")
            elif 'ID' in col_name.upper() or col_name.upper().endswith('NR'):
                column_types.append(f"Identifier: {col_name} ({col_type})")
        
        business_meaning += f"Key Columns: {'; '.join(column_types[:5])}\n"
        
        # Data characteristics
        if not sample_data.empty:
            business_meaning += f"Sample Records: {len(sample_data)}\n"
            business_meaning += f"Data Freshness: {self._assess_data_freshness(sample_data)}\n"
        
        return business_meaning
    
    def _assess_data_freshness(self, df: pd.DataFrame) -> str:
        """Assess how fresh/recent the data is"""
        date_columns = df.select_dtypes(include=['datetime64', 'object']).columns
        
        for col in date_columns:
            try:
                if 'date' in col.lower():
                    dates = pd.to_datetime(df[col], errors='coerce').dropna()
                    if not dates.empty:
                        latest_date = dates.max()
                        oldest_date = dates.min()
                        days_old = (datetime.now() - latest_date.to_pydatetime()).days
                        return f"Latest data: {days_old} days old (range: {oldest_date.date()} to {latest_date.date()})"
            except:
                continue
        
        return "Date information not available"
    
    def _calculate_data_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate comprehensive data quality score"""
        if df.empty:
            return 0.0
        
        scores = []
        
        # Completeness (non-null percentage)
        completeness = df.count().sum() / (df.shape[0] * df.shape[1])
        scores.append(completeness * 0.4)  # 40% weight
        
        # Uniqueness (for potential key columns)
        uniqueness_scores = []
        for col in df.columns:
            if df[col].dtype in ['int64', 'object']:
                unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
                uniqueness_scores.append(unique_ratio)
        
        avg_uniqueness = sum(uniqueness_scores) / len(uniqueness_scores) if uniqueness_scores else 0
        scores.append(avg_uniqueness * 0.3)  # 30% weight
        
        # Consistency (no obvious data errors)
        consistency = 1.0  # Default to perfect
        for col in df.select_dtypes(include=['object']).columns:
            if col.upper().endswith('DATE'):
                try:
                    pd.to_datetime(df[col], errors='raise')
                except:
                    consistency -= 0.2
        
        scores.append(consistency * 0.3)  # 30% weight
        
        return min(1.0, sum(scores))
    
    def _generate_common_queries(self, table_name: str, columns: List[Dict], foreign_keys: List[Dict]) -> List[str]:
        """Generate common SQL queries for this table"""
        queries = []
        
        # Basic count
        queries.append(f"SELECT COUNT(*) FROM {table_name}")
        
        # Recent data (if date column exists)
        date_cols = [col['name'] for col in columns if 'date' in col['name'].lower()]
        if date_cols:
            date_col = date_cols[0]
            queries.append(f"SELECT * FROM {table_name} WHERE {date_col} >= DATEADD(MONTH, -1, GETDATE())")
        
        # Joins with related tables
        for fk in foreign_keys:
            ref_table = fk['referenced_table']
            fk_col = fk['column']
            ref_col = fk['referenced_column']
            queries.append(f"SELECT t.*, r.* FROM {table_name} t JOIN {ref_table} r ON t.{fk_col} = r.{ref_col}")
        
        # Top records (if likely numeric columns exist)
        numeric_cols = [col['name'] for col in columns if 'amount' in col['name'].lower() or 'total' in col['name'].lower()]
        if numeric_cols:
            col = numeric_cols[0]
            queries.append(f"SELECT TOP 10 * FROM {table_name} ORDER BY {col} DESC")
        
        return queries[:5]  # Return top 5 most useful queries
    
    def _find_table_relationships(self, table_name: str, foreign_keys: List[Dict]) -> List[str]:
        """Find and describe table relationships"""
        relationships = []
        
        for fk in foreign_keys:
            ref_table = fk['referenced_table']
            relationship = f"{table_name} -> {ref_table} (via {fk['column']})"
            relationships.append(relationship)
        
        # Find reverse relationships (tables that reference this table)
        inspector = inspect(self.engine)
        all_tables = inspector.get_table_names()
        
        for other_table in all_tables:
            if other_table == table_name:
                continue
            
            try:
                other_fks = inspector.get_foreign_keys(other_table)
                for fk in other_fks:
                    if fk['referred_table'] == table_name:
                        relationship = f"{other_table} -> {table_name} (via {fk['constrained_columns'][0]})"
                        relationships.append(relationship)
            except:
                continue
        
        return relationships
    
    def _create_table_expectations(self, table_name: str, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Create Great Expectations for data validation"""
        expectations = []
        
        try:
            # Basic expectations
            expectations.append({
                "expectation_type": "expect_table_row_count_to_be_between",
                "kwargs": {"min_value": max(1, len(df) - 1000), "max_value": len(df) + 1000}
            })
            
            # Column expectations
            for col in df.columns:
                # Non-null expectations for important columns
                if col.upper().startswith('PK_') or 'ID' in col.upper():
                    expectations.append({
                        "expectation_type": "expect_column_values_to_not_be_null",
                        "kwargs": {"column": col}
                    })
                
                # Numeric range expectations
                if df[col].dtype in ['int64', 'float64']:
                    min_val = df[col].min()
                    max_val = df[col].max()
                    expectations.append({
                        "expectation_type": "expect_column_values_to_be_between",
                        "kwargs": {"column": col, "min_value": min_val, "max_value": max_val * 1.1}
                    })
            
        except Exception as e:
            self.logger.error(f"Failed to create expectations for {table_name}: {e}")
        
        return expectations
    
    def _save_table_insight(self, insight: TableInsight):
        """Save individual table insight to file"""
        insight_path = f"{self.output_dir}/{insight.table_name}_insight.json"
        with open(insight_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(insight), f, indent=2, ensure_ascii=False)
    
    def _save_comprehensive_insights(self, insights: Dict[str, TableInsight]):
        """Save comprehensive insights summary"""
        summary = {
            "analysis_date": datetime.now().isoformat(),
            "total_tables": len(insights),
            "tables": {name: asdict(insight) for name, insight in insights.items()},
            "recommendations": self._generate_recommendations(insights)
        }
        
        summary_path = f"{self.output_dir}/database_insights_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Also create a human-readable markdown report
        self._create_markdown_report(insights)
    
    def _generate_recommendations(self, insights: Dict[str, TableInsight]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Data quality recommendations
        low_quality_tables = [name for name, insight in insights.items() if insight.data_quality_score < 0.7]
        if low_quality_tables:
            recommendations.append(f"🔍 Review data quality for tables: {', '.join(low_quality_tables[:5])}")
        
        # Large tables that might need optimization
        large_tables = [(name, insight.row_count) for name, insight in insights.items() if insight.row_count > 100000]
        if large_tables:
            large_tables.sort(key=lambda x: x[1], reverse=True)
            recommendations.append(f"⚡ Consider indexing/optimization for large tables: {', '.join([t[0] for t in large_tables[:3]])}")
        
        # Missing relationships
        orphan_tables = [name for name, insight in insights.items() if not insight.foreign_keys and not insight.relationships]
        if orphan_tables:
            recommendations.append(f"🔗 Tables without clear relationships (potential for better linking): {', '.join(orphan_tables[:3])}")
        
        return recommendations
    
    def _create_markdown_report(self, insights: Dict[str, TableInsight]):
        """Create human-readable markdown report"""
        md_content = f"""# Database Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total Tables**: {len(insights)}
- **Analysis Date**: {datetime.now().date()}

## Table Overview

"""
        
        # Sort tables by importance (row count * data quality)
        sorted_tables = sorted(
            insights.items(), 
            key=lambda x: x[1].row_count * x[1].data_quality_score, 
            reverse=True
        )
        
        for table_name, insight in sorted_tables[:20]:  # Top 20 tables
            md_content += f"""### {table_name}
- **Business Purpose**: {insight.business_meaning.split('\\n')[0]}
- **Records**: {insight.row_count:,}
- **Data Quality**: {insight.data_quality_score:.1%}
- **Key Relationships**: {len(insight.relationships)}

"""
        
        md_path = f"{self.output_dir}/database_analysis_report.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
    
    def get_table_insight(self, table_name: str) -> Optional[TableInsight]:
        """Get cached insight for a specific table"""
        if table_name in self.insights_cache:
            return self.insights_cache[table_name]
        
        # Try to load from file
        insight_path = f"{self.output_dir}/{table_name}_insight.json"
        if os.path.exists(insight_path):
            with open(insight_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                insight = TableInsight(**data)
                self.insights_cache[table_name] = insight
                return insight
        
        return None
    
    def update_query_learning(self, table_name: str, query: str, success: bool, result_count: int):
        """Learn from query usage patterns"""
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "table_name": table_name,
            "query": query,
            "success": success,
            "result_count": result_count
        }
        
        self.learning_history.append(learning_entry)
        
        # Save learning history
        learning_path = f"{self.output_dir}/query_learning_history.json"
        with open(learning_path, 'w', encoding='utf-8') as f:
            json.dump(self.learning_history, f, indent=2, ensure_ascii=False)
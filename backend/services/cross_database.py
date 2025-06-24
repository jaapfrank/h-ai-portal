#!/usr/bin/env python3
"""
Cross-Database Query Engine for Hoeflon AI
Intelligently combines data from ERP (operational) and AccountView (financial) databases
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date
import pandas as pd

class CrossDatabaseEngine:
    """Engine for executing cross-database queries that combine ERP and AccountView data"""
    
    def __init__(self, multi_db_manager):
        self.multi_db_manager = multi_db_manager
        # Initialize transaction linker dynamically
        try:
            from enhanced_transaction_linking_engine import EnhancedTransactionLinkingEngine
            self.transaction_linker = EnhancedTransactionLinkingEngine(multi_db_manager)
        except ImportError:
            # Fallback to basic linking if enhanced not available
            self.transaction_linker = None
        
        # Define mapping between ERP and AccountView entities
        self.entity_mappings = {
            # Company/Customer mappings
            "companies": {
                "erp_table": "R_RELATION",
                "erp_key": "NAME",
                "accountview_key": "company_name",
                "common_values": ["Hoeflon B.V.", "Hoeflon International"]
            },
            
            # Product/Article mappings
            "products": {
                "erp_table": "R_ITEM", 
                "erp_key": "DESCRIPTION",
                "accountview_table": "ARTICLE",
                "accountview_key": "art_name"
            },
            
            # Financial periods
            "periods": {
                "erp_date_fields": ["INVOICEDATE", "ORDERDATE", "CREATEDDATE"],
                "accountview_date_fields": ["trans_date", "inp_date"]
            }
        }
        
        # Common business question patterns that require cross-database queries
        self.cross_db_patterns = {
            "revenue_vs_operations": {
                "keywords": ["omzet", "revenue", "verkoop", "sales", "financial", "vs", "tegenover", "compared"],
                "description": "Compare financial revenue data with operational metrics"
            },
            
            "customer_analysis": {
                "keywords": ["klant", "customer", "client", "analyse", "analysis", "performance"],
                "description": "Customer performance across both financial and operational data"
            },
            
            "product_profitability": {
                "keywords": ["product", "artikel", "machine", "profitability", "winstgevendheid", "margin"],
                "description": "Product profitability combining sales and financial data"
            },
            
            "period_comparison": {
                "keywords": ["vergelijk", "compare", "jaar", "year", "maand", "month", "periode", "period"],
                "description": "Time-based comparison across databases"
            }
        }
    
    def analyze_question(self, question: str) -> Dict[str, Any]:
        """Analyze question to determine if cross-database query is needed"""
        question_lower = question.lower()
        
        analysis = {
            "requires_cross_db": False,
            "databases_needed": [],
            "query_type": None,
            "entities": [],
            "time_period": None,
            "complexity": "simple"
        }
        
        # Check for cross-database patterns
        for pattern_name, pattern_data in self.cross_db_patterns.items():
            if any(keyword in question_lower for keyword in pattern_data["keywords"]):
                analysis["requires_cross_db"] = True
                analysis["query_type"] = pattern_name
                analysis["complexity"] = "cross_database"
                break
        
        # Determine which databases are needed
        if "machine" in question_lower or "productie" in question_lower or "voorraad" in question_lower:
            analysis["databases_needed"].append("erp")
        
        if any(word in question_lower for word in ["omzet", "financieel", "financial", "revenue", "ledger", "accounting"]):
            analysis["databases_needed"].extend(["hoeflon_bv", "hoeflon_international"])
        
        # If no specific database mentioned but cross-db required, use all
        if analysis["requires_cross_db"] and not analysis["databases_needed"]:
            analysis["databases_needed"] = ["erp", "hoeflon_bv", "hoeflon_international"]
        
        # Extract time period
        year_match = re.search(r'\b(20\d{2})\b', question)
        if year_match:
            analysis["time_period"] = int(year_match.group(1))
        elif "dit jaar" in question_lower or "this year" in question_lower:
            analysis["time_period"] = datetime.now().year
        elif "vorig jaar" in question_lower or "last year" in question_lower:
            analysis["time_period"] = datetime.now().year - 1
        
        return analysis
    
    def execute_cross_database_query(self, question: str) -> Dict[str, Any]:
        """Execute a cross-database query based on the question"""
        analysis = self.analyze_question(question)
        
        result = {
            "question": question,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "data_sources": {},
            "combined_insights": [],
            "summary": ""
        }
        
        try:
            # Check if this is a pure revenue question - prioritize Hoeflon International
            if any(word in question.lower() for word in ["omzet", "revenue", "verkoop"]) and not any(word in question.lower() for word in ["machine", "productie", "vergelijk"]):
                result.update(self._pure_revenue_query(analysis))
                
            elif analysis["query_type"] == "revenue_vs_operations":
                result.update(self._revenue_vs_operations_query(analysis))
                
            elif analysis["query_type"] == "customer_analysis":
                result.update(self._customer_analysis_query(analysis))
                
            elif analysis["query_type"] == "product_profitability":
                result.update(self._product_profitability_query(analysis))
                
            elif analysis["query_type"] == "period_comparison":
                result.update(self._period_comparison_query(analysis))
                
            else:
                # Default: get data from all needed databases
                result.update(self._general_cross_db_query(analysis))
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _pure_revenue_query(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pure revenue questions - Focus ONLY on Hoeflon International real sales"""
        from decimal import Decimal
        
        def safe_convert_amount(value):
            """Safely convert amount to float"""
            if value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, Decimal):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value.replace(',', ''))
                except:
                    return 0.0
            return 0.0
        
        data_sources = {}
        insights = []
        
        insights.append("🎯 Omzetanalyse: Focus op Hoeflon International (echte externe verkoop)")
        insights.append("📊 Correcte databron: PREV_GJL tabel (werkelijke transacties)")
        
        try:
            # Get REAL revenue from PREV_GJL table (actual transactions)
            transaction_data = self.multi_db_manager.query_dbf("hoeflon_international", "PREV_GJL", limit=500)
            
            # Calculate revenue by analyzing transaction records
            total_revenue = 0
            revenue_details = []
            current_year = datetime.now().year
            
            for row in transaction_data:
                account_nr = str(row.get('ACCT_NR', ''))
                amount = safe_convert_amount(row.get('AMOUNT', 0))
                trn_desc = str(row.get('TRN_DESC', ''))
                trn_date = str(row.get('TRN_DATE', ''))
                
                # Revenue accounts start with 8 in Dutch accounting
                # AccountView shows revenue as negative amounts
                if account_nr.startswith('8') and amount != 0:
                    # Convert negative amounts to positive for revenue display
                    revenue_amount = abs(amount)
                    total_revenue += revenue_amount
                    
                    revenue_details.append({
                        "account": account_nr,
                        "description": trn_desc,
                        "amount": revenue_amount,
                        "original_amount": amount,
                        "date": trn_date
                    })
            
            data_sources["hoeflon_international_revenue"] = {
                "total_revenue": total_revenue,
                "revenue_transactions": len(revenue_details),
                "top_revenue_items": sorted(revenue_details, key=lambda x: x['amount'], reverse=True)[:10],
                "data_source": "AccountView Hoeflon International - PREV_GJL"
            }
            
            if total_revenue > 0:
                insights.append(f"💰 Hoeflon International totale omzet: €{total_revenue:,.2f}")
                insights.append(f"📊 Gebaseerd op {len(revenue_details)} omzettransacties")
                
                # Show top revenue items
                top_items = sorted(revenue_details, key=lambda x: x['amount'], reverse=True)[:5]
                insights.append("🏆 Top omzet items:")
                for i, item in enumerate(top_items, 1):
                    insights.append(f"  {i}. €{item['amount']:,.2f} - {item['description']} ({item['date']})")
                
            else:
                insights.append("⚠️ Geen omzetgegevens gevonden in PREV_GJL tabel")
            
            # Also check TRANSACT table for additional revenue data
            try:
                transact_data = self.multi_db_manager.query_dbf("hoeflon_international", "TRANSACT", limit=200)
                transact_revenue = 0
                transact_8xxx = []
                
                for row in transact_data:
                    account_nr = str(row.get('ACCT_NR', ''))
                    if account_nr.startswith('8'):
                        amount = safe_convert_amount(row.get('AMOUNT', 0))
                        if amount != 0:
                            transact_8xxx.append({
                                "account": account_nr,
                                "amount": abs(amount),
                                "description": row.get('TRN_DESC', ''),
                                "date": row.get('TRN_DATE', '')
                            })
                            transact_revenue += abs(amount)
                
                if transact_8xxx:
                    data_sources["transact_revenue"] = {
                        "total": transact_revenue,
                        "transactions": len(transact_8xxx),
                        "source": "TRANSACT table"
                    }
                    insights.append(f"📈 Aanvullende omzet uit TRANSACT: €{transact_revenue:,.2f}")
                
            except Exception as e:
                data_sources["transact_error"] = str(e)
            
            # Also check current transactions for more recent data
            try:
                # Check if there are more recent transactions in other tables
                all_tables = self.multi_db_manager.get_dbf_tables("hoeflon_international")
                transaction_tables = [t for t in all_tables if any(keyword in t.lower() 
                                    for keyword in ['trn', 'gjl', 'transact'])]
                
                insights.append(f"🔍 Beschikbare transactietabellen: {', '.join(transaction_tables)}")
                
            except Exception as e:
                pass
            
        except Exception as e:
            data_sources["hoeflon_international_error"] = str(e)
            insights.append(f"❌ Fout bij ophalen Hoeflon International data: {str(e)}")
        
        # Get basic info for context
        try:
            tables = self.multi_db_manager.get_dbf_tables("hoeflon_international")
            data_sources["available_tables"] = {
                "table_count": len(tables),
                "transaction_tables": [t for t in tables if any(keyword in t.lower() 
                                     for keyword in ['prev_gjl', 'transact', 'trn_hdr', 'transit'])]
            }
            insights.append(f"📋 Beschikbare transactietabellen: {len(data_sources['available_tables']['transaction_tables'])}")
            
        except Exception as e:
            data_sources["table_info_error"] = str(e)
        
        summary = "Omzetanalyse vanuit Hoeflon International AccountView database (PREV_GJL transacties)"
        
        return {
            "data_sources": data_sources,
            "combined_insights": insights,
            "summary": summary
        }
    
    def _revenue_vs_operations_query(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compare financial revenue with operational metrics - Focus on Hoeflon International for real revenue"""
        data_sources = {}
        insights = []
        
        # Get ERP operational data (for context only)
        try:
            # Machine production data
            machine_query = """
                SELECT 
                    COUNT(*) as total_machines,
                    SUM(CASE WHEN STATE = 2 THEN 1 ELSE 0 END) as ready_machines,
                    SUM(CASE WHEN STATE = 1 THEN 1 ELSE 0 END) as in_production
                FROM U_SERIENUMMERSHOEFLON
            """
            machine_data = self.multi_db_manager.query_erp(machine_query)
            data_sources["erp_machines"] = machine_data[0] if machine_data else {}
            
        except Exception as e:
            data_sources["erp_error"] = str(e)
        
        # PRIORITIZE Hoeflon International for REAL revenue data
        insights.append("💡 Focus: Hoeflon International heeft de echte externe omzet")
        
        try:
            # Get REAL revenue from Hoeflon International AccountView
            ledger_data = self.multi_db_manager.query_dbf("hoeflon_international", "LEDGER", limit=100)
            
            # Calculate total revenue from ledger
            total_revenue = 0
            revenue_accounts = []
            
            for row in ledger_data:
                cr_amt = row.get('CR_AMT', 0) or 0
                dr_amt = row.get('DR_AMT', 0) or 0
                account_name = str(row.get('ACCT_NAME', '')).lower()
                
                # Look for revenue indicators
                if any(keyword in account_name for keyword in ['verkoop', 'omzet', 'revenue', 'sales', '8']):  # Account 8xxx = revenue
                    if isinstance(cr_amt, (int, float)) and cr_amt > 0:
                        total_revenue += cr_amt
                        revenue_accounts.append({
                            "account": row.get('ACCT_NR', ''),
                            "name": row.get('ACCT_NAME', ''),
                            "amount": cr_amt
                        })
            
            data_sources["hoeflon_international_real_revenue"] = {
                "total_revenue": total_revenue,
                "revenue_accounts_count": len(revenue_accounts),
                "top_revenue_accounts": sorted(revenue_accounts, key=lambda x: x['amount'], reverse=True)[:5]
            }
            
            if total_revenue > 0:
                insights.append(f"🌍 Hoeflon International echte omzet: €{total_revenue:,.2f}")
            
        except Exception as e:
            data_sources["hoeflon_international_error"] = str(e)
            insights.append("⚠️ Kan Hoeflon International omzetdata niet ophalen")
        
        # Get Hoeflon B.V. for comparison (secondary)
        try:
            ledger_data_bv = self.multi_db_manager.query_dbf("hoeflon_bv", "LEDGER", limit=50)
            
            bv_revenue = 0
            for row in ledger_data_bv:
                cr_amt = row.get('CR_AMT', 0) or 0
                account_name = str(row.get('ACCT_NAME', '')).lower()
                if any(keyword in account_name for keyword in ['verkoop', 'omzet', 'revenue']) and isinstance(cr_amt, (int, float)):
                    bv_revenue += cr_amt
            
            data_sources["hoeflon_bv_revenue"] = {"total_revenue": bv_revenue}
            
            if bv_revenue > 0:
                insights.append(f"🏢 Hoeflon B.V. omzet (meer intern): €{bv_revenue:,.2f}")
                
        except Exception as e:
            data_sources["hoeflon_bv_error"] = str(e)
        
        # Generate insights
        if "erp_machines" in data_sources:
            machine_info = data_sources["erp_machines"]
            if machine_info.get("total_machines", 0) > 0:
                production_efficiency = (machine_info.get("ready_machines", 0) / machine_info.get("total_machines", 1)) * 100
                insights.append(f"Production efficiency: {production_efficiency:.1f}% machines ready")
        
        if "erp_sales" in data_sources:
            for year_data in data_sources["erp_sales"]:
                year = year_data.get("year")
                revenue = year_data.get("total_revenue", 0)
                if revenue > 0:
                    insights.append(f"{year}: €{revenue:,.2f} ERP revenue from {year_data.get('invoice_count', 0)} invoices")
        
        summary = f"Cross-database analysis combining operational metrics with financial data from ERP and AccountView systems."
        
        return {
            "data_sources": data_sources,
            "combined_insights": insights,
            "summary": summary
        }
    
    def _customer_analysis_query(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer performance across databases"""
        data_sources = {}
        insights = []
        
        # Get customer data from ERP
        try:
            customer_query = """
                SELECT TOP 10
                    r.NAME as customer_name,
                    COUNT(si.PK_R_SALESINVOICE) as invoice_count,
                    SUM(si.TOTALAMOUNT) as total_revenue,
                    MAX(si.INVOICEDATE) as last_invoice_date
                FROM R_RELATION r
                JOIN R_SALESINVOICE si ON r.PK_R_RELATION = si.FK_INVOICERELATION
                WHERE r.NAME NOT LIKE '%Hoeflon%'
                GROUP BY r.NAME
                ORDER BY SUM(si.TOTALAMOUNT) DESC
            """
            customer_data = self.multi_db_manager.query_erp(customer_query)
            data_sources["erp_customers"] = customer_data
            
        except Exception as e:
            data_sources["erp_error"] = str(e)
        
        # Analyze AccountView for customer-related financial data
        for db_name in ["hoeflon_bv", "hoeflon_international"]:
            try:
                # Get customer-related accounts
                ledger_data = self.multi_db_manager.query_dbf(db_name, "LEDGER", limit=100)
                customer_accounts = [row for row in ledger_data if 
                                   any(keyword in str(row.get('ACCT_NAME', '')).lower() for keyword in ['debtor', 'customer', 'klant'])]
                
                data_sources[f"{db_name}_customers"] = {
                    "customer_account_count": len(customer_accounts),
                    "sample_accounts": customer_accounts[:3]
                }
                
            except Exception as e:
                data_sources[f"{db_name}_error"] = str(e)
        
        # Generate insights
        if "erp_customers" in data_sources:
            top_customer = data_sources["erp_customers"][0] if data_sources["erp_customers"] else None
            if top_customer:
                insights.append(f"Top customer: {top_customer.get('customer_name')} with €{top_customer.get('total_revenue', 0):,.2f}")
        
        summary = "Customer analysis combining ERP sales data with AccountView financial records"
        
        return {
            "data_sources": data_sources,
            "combined_insights": insights,
            "summary": summary
        }
    
    def _product_profitability_query(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze product profitability across systems"""
        data_sources = {}
        insights = []
        
        # Get product data from ERP
        try:
            product_query = """
                SELECT TOP 10
                    i.DESCRIPTION as product_name,
                    i.ITEMCODE as product_code,
                    COUNT(sid.PK_R_SALESINVOICEDETAILITEM) as sales_count,
                    SUM(sid.QUANTITY) as total_quantity,
                    SUM(sid.TOTALAMOUNT) as total_revenue
                FROM R_ITEM i
                JOIN R_SALESINVOICEDETAILITEM sid ON i.PK_R_ITEM = sid.FK_ITEM
                JOIN R_SALESINVOICE si ON sid.FK_SALESINVOICE = si.PK_R_SALESINVOICE
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                GROUP BY i.DESCRIPTION, i.ITEMCODE
                ORDER BY SUM(sid.TOTALAMOUNT) DESC
            """
            product_data = self.multi_db_manager.query_erp(product_query)
            data_sources["erp_products"] = product_data
            
        except Exception as e:
            data_sources["erp_error"] = str(e)
        
        # Get product/article data from AccountView
        for db_name in ["hoeflon_bv", "hoeflon_international"]:
            try:
                article_data = self.multi_db_manager.query_dbf(db_name, "ARTICLE", limit=20)
                data_sources[f"{db_name}_articles"] = {
                    "article_count": len(article_data),
                    "sample_articles": article_data[:3]
                }
                
            except Exception as e:
                data_sources[f"{db_name}_error"] = str(e)
        
        # Generate insights
        if "erp_products" in data_sources:
            top_product = data_sources["erp_products"][0] if data_sources["erp_products"] else None
            if top_product:
                insights.append(f"Top product: {top_product.get('product_name')} - €{top_product.get('total_revenue', 0):,.2f}")
        
        summary = "Product profitability analysis combining ERP sales with AccountView financial data"
        
        return {
            "data_sources": data_sources,
            "combined_insights": insights,
            "summary": summary
        }
    
    def _period_comparison_query(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compare data across time periods"""
        data_sources = {}
        insights = []
        
        year = analysis.get("time_period", datetime.now().year)
        
        # Get yearly comparison from ERP
        try:
            yearly_query = f"""
                SELECT 
                    YEAR(INVOICEDATE) as year,
                    COUNT(*) as invoice_count,
                    SUM(TOTALAMOUNT) as total_revenue
                FROM R_SALESINVOICE 
                WHERE YEAR(INVOICEDATE) IN ({year}, {year-1})
                GROUP BY YEAR(INVOICEDATE)
                ORDER BY YEAR(INVOICEDATE)
            """
            yearly_data = self.multi_db_manager.query_erp(yearly_query)
            data_sources["erp_yearly"] = yearly_data
            
        except Exception as e:
            data_sources["erp_error"] = str(e)
        
        # Analyze AccountView for period data
        for db_name in ["hoeflon_bv", "hoeflon_international"]:
            try:
                # Get recent transaction data
                daily_data = self.multi_db_manager.query_dbf(db_name, "DAILY", limit=50)
                data_sources[f"{db_name}_transactions"] = {
                    "transaction_count": len(daily_data),
                    "sample_transactions": daily_data[:3]
                }
                
            except Exception as e:
                data_sources[f"{db_name}_error"] = str(e)
        
        # Generate insights
        if "erp_yearly" in data_sources and len(data_sources["erp_yearly"]) >= 2:
            current_year = data_sources["erp_yearly"][-1]
            previous_year = data_sources["erp_yearly"][-2]
            
            current_revenue = current_year.get("total_revenue", 0)
            previous_revenue = previous_year.get("total_revenue", 0)
            
            if previous_revenue > 0:
                growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
                insights.append(f"Revenue growth: {growth:+.1f}% from {previous_year.get('year')} to {current_year.get('year')}")
        
        summary = f"Period comparison for {year} combining ERP operational data with AccountView financial records"
        
        return {
            "data_sources": data_sources,
            "combined_insights": insights,
            "summary": summary
        }
    
    def _general_cross_db_query(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """General cross-database query for unspecified patterns"""
        data_sources = {}
        insights = []
        
        # Get summary data from each requested database
        for db_name in analysis["databases_needed"]:
            if db_name == "erp":
                try:
                    # Get basic ERP statistics
                    erp_stats = self.multi_db_manager.query_erp("""
                        SELECT 
                            (SELECT COUNT(*) FROM U_SERIENUMMERSHOEFLON) as total_machines,
                            (SELECT COUNT(*) FROM R_SALESINVOICE WHERE YEAR(INVOICEDATE) = YEAR(GETDATE())) as invoices_this_year,
                            (SELECT SUM(TOTALAMOUNT) FROM R_SALESINVOICE WHERE YEAR(INVOICEDATE) = YEAR(GETDATE())) as revenue_this_year
                    """)
                    data_sources["erp_summary"] = erp_stats[0] if erp_stats else {}
                    
                except Exception as e:
                    data_sources["erp_error"] = str(e)
            
            else:  # AccountView databases
                try:
                    tables = self.multi_db_manager.get_dbf_tables(db_name)
                    ledger_data = self.multi_db_manager.query_dbf(db_name, "LEDGER", limit=10) if "LEDGER" in tables else []
                    
                    data_sources[f"{db_name}_summary"] = {
                        "table_count": len(tables),
                        "ledger_accounts": len(ledger_data),
                        "sample_tables": tables[:5]
                    }
                    
                except Exception as e:
                    data_sources[f"{db_name}_error"] = str(e)
        
        # Generate basic insights
        if "erp_summary" in data_sources:
            erp_data = data_sources["erp_summary"]
            insights.append(f"ERP: {erp_data.get('total_machines', 0)} machines, {erp_data.get('invoices_this_year', 0)} invoices this year")
        
        summary = f"General cross-database query across {', '.join(analysis['databases_needed'])} systems"
        
        return {
            "data_sources": data_sources,
            "combined_insights": insights,
            "summary": summary
        }
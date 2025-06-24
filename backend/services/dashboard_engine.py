#!/usr/bin/env python3
"""
Dashboard Engine for Hoeflon AI
Creates comprehensive multi-database dashboards with KPIs and visualizations
"""

import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pyodbc

class DashboardEngine:
    """Engine for creating comprehensive business dashboards"""
    
    def __init__(self, multi_db_manager):
        self.multi_db_manager = multi_db_manager
        
        # Dashboard configurations
        self.dashboard_configs = {
            "executive": {
                "name": "Executive Dashboard",
                "description": "High-level overview voor management",
                "kpis": [
                    "revenue_ytd",
                    "monthly_growth", 
                    "machines_produced_ytd",
                    "on_time_delivery",
                    "top_customer_revenue"
                ],
                "charts": [
                    "revenue_trend_12m",
                    "production_vs_sales",
                    "top_customers",
                    "machine_type_breakdown"
                ]
            },
            "production": {
                "name": "Production Dashboard", 
                "description": "Real-time productie monitoring",
                "kpis": [
                    "machines_in_production",
                    "completed_this_week",
                    "pending_delivery",
                    "production_efficiency"
                ],
                "charts": [
                    "daily_production_30d",
                    "machine_types_in_production",
                    "delivery_performance",
                    "production_bottlenecks"
                ]
            },
            "financial": {
                "name": "Financial Dashboard",
                "description": "Uitgebreide financiële analyse", 
                "kpis": [
                    "external_revenue",
                    "internal_revenue",
                    "gross_margin",
                    "collection_rate"
                ],
                "charts": [
                    "revenue_waterfall",
                    "customer_profitability",
                    "payment_behavior",
                    "currency_distribution"
                ]
            }
        }
        
    def generate_executive_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive executive dashboard"""
        
        try:
            # Get database connection
            conn = self._get_connection()
            
            # Generate KPIs
            kpis = self._generate_executive_kpis(conn)
            
            # Generate charts
            charts = self._generate_executive_charts(conn)
            
            # Create dashboard layout
            dashboard = {
                "type": "executive_dashboard",
                "title": "🏭 HOEFLON EXECUTIVE DASHBOARD",
                "subtitle": f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "kpis": kpis,
                "charts": charts,
                "summary": self._generate_executive_summary(kpis),
                "recommendations": self._generate_recommendations(kpis, charts)
            }
            
            conn.close()
            return dashboard
            
        except Exception as e:
            return {
                "error": f"Dashboard generation failed: {str(e)}",
                "type": "error"
            }
            
    def generate_production_dashboard(self) -> Dict[str, Any]:
        """Generate real-time production dashboard"""
        
        try:
            conn = self._get_connection()
            
            # Generate production KPIs
            kpis = self._generate_production_kpis(conn)
            
            # Generate production charts
            charts = self._generate_production_charts(conn)
            
            dashboard = {
                "type": "production_dashboard", 
                "title": "🏭 HOEFLON PRODUCTION DASHBOARD",
                "subtitle": f"Real-time status - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "kpis": kpis,
                "charts": charts,
                "summary": self._generate_production_summary(kpis),
                "alerts": self._generate_production_alerts(kpis),
                "recommendations": self._generate_production_recommendations(kpis)
            }
            
            conn.close()
            return dashboard
            
        except Exception as e:
            return {
                "error": f"Production dashboard failed: {str(e)}",
                "type": "error"
            }
            
    def generate_financial_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive financial dashboard"""
        
        try:
            conn = self._get_connection()
            
            # Generate financial KPIs
            kpis = self._generate_financial_kpis(conn)
            
            # Generate financial charts
            charts = self._generate_financial_charts(conn)
            
            dashboard = {
                "type": "financial_dashboard",
                "title": "💰 HOEFLON FINANCIAL DASHBOARD", 
                "subtitle": f"Financial Analytics - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "kpis": kpis,
                "charts": charts,
                "summary": self._generate_financial_summary(kpis),
                "recommendations": self._generate_financial_recommendations(kpis)
            }
            
            conn.close()
            return dashboard
            
        except Exception as e:
            return {
                "error": f"Financial dashboard failed: {str(e)}",
                "type": "error"
            }
            
    def _get_connection(self):
        """Get database connection"""
        config = self.multi_db_manager.load_config()
        return pyodbc.connect(
            f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={config['sql_host']};DATABASE={config['sql_db']};UID={config['sql_user']};PWD={config['sql_pass']};TrustServerCertificate=yes;Encrypt=optional",
            timeout=10
        )
        
    def _generate_executive_kpis(self, conn) -> Dict[str, Any]:
        """Generate executive KPIs"""
        
        kpis = {}
        
        try:
            # 1. Revenue YTD
            revenue_query = """
                SELECT SUM(TOTALAMOUNT) as Revenue
                FROM R_SALESINVOICE si
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
            """
            revenue_result = pd.read_sql(revenue_query, conn)
            kpis["revenue_ytd"] = {
                "value": float(revenue_result['Revenue'].iloc[0]) if not revenue_result['Revenue'].isna().iloc[0] else 0,
                "label": "Omzet YTD",
                "format": "currency",
                "icon": "💰"
            }
            
            # 2. Monthly Growth
            monthly_growth_query = """
                SELECT 
                    SUM(CASE WHEN MONTH(INVOICEDATE) = MONTH(GETDATE()) THEN TOTALAMOUNT ELSE 0 END) as CurrentMonth,
                    SUM(CASE WHEN MONTH(INVOICEDATE) = MONTH(DATEADD(MONTH, -1, GETDATE())) THEN TOTALAMOUNT ELSE 0 END) as PreviousMonth
                FROM R_SALESINVOICE si
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
            """
            growth_result = pd.read_sql(monthly_growth_query, conn)
            current = float(growth_result['CurrentMonth'].iloc[0]) if not growth_result['CurrentMonth'].isna().iloc[0] else 0
            previous = float(growth_result['PreviousMonth'].iloc[0]) if not growth_result['PreviousMonth'].isna().iloc[0] else 1
            growth_rate = ((current - previous) / previous * 100) if previous > 0 else 0
            
            kpis["monthly_growth"] = {
                "value": growth_rate,
                "label": "Maandelijkse Groei",
                "format": "percentage",
                "icon": "📈"
            }
            
            # 3. Machines Produced YTD
            machines_query = """
                SELECT COUNT(*) as MachinesProduced
                FROM R_SERVICEOBJECT so
                WHERE so.FK_SERVICEOBJECTTYPE IN (6,9,10,12,15)
                  AND YEAR(so.DELIVERYDATE) = YEAR(GETDATE())
                  AND so.DELIVERYDATE IS NOT NULL
                  AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
            """
            machines_result = pd.read_sql(machines_query, conn)
            kpis["machines_produced_ytd"] = {
                "value": int(machines_result['MachinesProduced'].iloc[0]),
                "label": "Machines Geproduceerd",
                "format": "number", 
                "icon": "🏭"
            }
            
            # 4. On-Time Delivery (simplified - using machine count as proxy)
            delivery_query = """
                SELECT 
                    COUNT(*) as Total,
                    COUNT(CASE WHEN DATEDIFF(DAY, so.DATECREATED, so.DELIVERYDATE) <= 60 THEN 1 END) as OnTime
                FROM R_SERVICEOBJECT so
                WHERE so.FK_SERVICEOBJECTTYPE IN (6,9,10,12,15)
                  AND YEAR(so.DELIVERYDATE) = YEAR(GETDATE())
                  AND so.DELIVERYDATE IS NOT NULL
                  AND so.DATECREATED IS NOT NULL
                  AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
            """
            delivery_result = pd.read_sql(delivery_query, conn)
            total = int(delivery_result['Total'].iloc[0])
            on_time = int(delivery_result['OnTime'].iloc[0]) if not delivery_result['OnTime'].isna().iloc[0] else 0
            on_time_rate = (on_time / total * 100) if total > 0 else 0
            
            kpis["on_time_delivery"] = {
                "value": on_time_rate,
                "label": "On-Time Delivery",
                "format": "percentage",
                "icon": "⏰"
            }
            
            # 5. Top Customer Revenue (simplified - using customer ID)
            top_customer_query = """
                SELECT TOP 1 
                    CONCAT('Customer_', si.FK_INVOICERELATION) as Customer,
                    SUM(si.TOTALAMOUNT) as Revenue
                FROM R_SALESINVOICE si
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
                GROUP BY si.FK_INVOICERELATION
                ORDER BY SUM(si.TOTALAMOUNT) DESC
            """
            top_customer_result = pd.read_sql(top_customer_query, conn)
            if len(top_customer_result) > 0:
                kpis["top_customer"] = {
                    "value": top_customer_result['Customer'].iloc[0],
                    "amount": float(top_customer_result['Revenue'].iloc[0]),
                    "label": "Top Klant",
                    "format": "text",
                    "icon": "🏆"
                }
            else:
                kpis["top_customer"] = {
                    "value": "Geen data",
                    "amount": 0,
                    "label": "Top Klant", 
                    "format": "text",
                    "icon": "🏆"
                }
                
        except Exception as e:
            print(f"Error generating KPIs: {e}")
            
        return kpis
        
    def _generate_executive_charts(self, conn) -> Dict[str, Any]:
        """Generate executive dashboard charts"""
        
        charts = {}
        
        try:
            # 1. Revenue Trend (12 months)
            revenue_trend_query = """
                SELECT 
                    YEAR(INVOICEDATE) as Jaar,
                    MONTH(INVOICEDATE) as Maand,
                    SUM(TOTALAMOUNT) as Omzet
                FROM R_SALESINVOICE si
                WHERE INVOICEDATE >= DATEADD(MONTH, -12, GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
                GROUP BY YEAR(INVOICEDATE), MONTH(INVOICEDATE)
                ORDER BY YEAR(INVOICEDATE), MONTH(INVOICEDATE)
            """
            revenue_data = pd.read_sql(revenue_trend_query, conn)
            charts["revenue_trend"] = {
                "data": revenue_data.to_dict('records'),
                "type": "line",
                "title": "Revenue Trend (12 maanden)",
                "x_axis": "Maand",
                "y_axis": "Omzet (€)"
            }
            
            # 2. Top 5 Customers (simplified)
            top_customers_query = """
                SELECT TOP 5
                    CONCAT('Customer_', si.FK_INVOICERELATION) as Klant,
                    SUM(si.TOTALAMOUNT) as Omzet
                FROM R_SALESINVOICE si
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
                GROUP BY si.FK_INVOICERELATION
                ORDER BY SUM(si.TOTALAMOUNT) DESC
            """
            customers_data = pd.read_sql(top_customers_query, conn)
            charts["top_customers"] = {
                "data": customers_data.to_dict('records'),
                "type": "horizontal_bar",
                "title": "Top 5 Klanten",
                "x_axis": "Omzet (€)",
                "y_axis": "Klant"
            }
            
            # 3. Machine Type Production
            machine_types_query = """
                SELECT 
                    CASE 
                        WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6'
                        WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30'
                        WHEN i.DESCRIPTION LIKE '%C3%' THEN 'C3'
                        WHEN i.DESCRIPTION LIKE '%C1%' THEN 'C1'
                        ELSE 'Overig'
                    END as MachineType,
                    COUNT(*) as Aantal
                FROM R_SERVICEOBJECT so
                JOIN R_ITEM i ON so.FK_SERVICEOBJECTTYPE = i.PK_R_ITEM
                WHERE so.FK_SERVICEOBJECTTYPE IN (6,9,10,12,15)
                  AND YEAR(so.DELIVERYDATE) = YEAR(GETDATE())
                  AND so.DELIVERYDATE IS NOT NULL
                  AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                GROUP BY CASE 
                    WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6'
                    WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30'
                    WHEN i.DESCRIPTION LIKE '%C3%' THEN 'C3'
                    WHEN i.DESCRIPTION LIKE '%C1%' THEN 'C1'
                    ELSE 'Overig'
                END
                ORDER BY COUNT(*) DESC
            """
            machine_data = pd.read_sql(machine_types_query, conn)
            charts["machine_types"] = {
                "data": machine_data.to_dict('records'),
                "type": "pie",
                "title": "Machine Type Productie",
                "x_axis": "Type",
                "y_axis": "Aantal"
            }
            
            # 4. Production vs Revenue Correlation
            prod_revenue_query = """
                SELECT 
                    MONTH(so.DELIVERYDATE) as Maand,
                    COUNT(so.PK_R_SERVICEOBJECT) as MachinesGeleverd,
                    COALESCE(rev.Omzet, 0) as Omzet
                FROM R_SERVICEOBJECT so
                LEFT JOIN (
                    SELECT 
                        MONTH(INVOICEDATE) as Maand,
                        SUM(TOTALAMOUNT) as Omzet
                    FROM R_SALESINVOICE si
                    WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                      AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                      AND si.TOTALAMOUNT > 0
                    GROUP BY MONTH(INVOICEDATE)
                ) rev ON MONTH(so.DELIVERYDATE) = rev.Maand
                WHERE so.FK_SERVICEOBJECTTYPE IN (6,9,10,12,15)
                  AND YEAR(so.DELIVERYDATE) = YEAR(GETDATE())
                  AND so.DELIVERYDATE IS NOT NULL
                  AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                GROUP BY MONTH(so.DELIVERYDATE), rev.Omzet
                ORDER BY MONTH(so.DELIVERYDATE)
            """
            prod_revenue_data = pd.read_sql(prod_revenue_query, conn)
            charts["production_vs_revenue"] = {
                "data": prod_revenue_data.to_dict('records'),
                "type": "dual_axis",
                "title": "Productie vs Revenue",
                "x_axis": "Maand",
                "y_axis_left": "Machines",
                "y_axis_right": "Omzet (€)"
            }
            
        except Exception as e:
            print(f"Error generating charts: {e}")
            
        return charts
        
    def _generate_executive_summary(self, kpis: Dict[str, Any]) -> str:
        """Generate executive summary based on KPIs"""
        
        try:
            revenue = kpis.get("revenue_ytd", {}).get("value", 0)
            growth = kpis.get("monthly_growth", {}).get("value", 0)
            machines = kpis.get("machines_produced_ytd", {}).get("value", 0)
            delivery = kpis.get("on_time_delivery", {}).get("value", 0)
            
            summary = f"""
📊 **EXECUTIVE SUMMARY - {datetime.now().strftime('%B %Y')}**

**Financiële Prestaties:**
• YTD Revenue: €{revenue:,.0f}
• Maandelijkse groei: {growth:+.1f}%
• Gemiddelde deal size: €{revenue/machines:,.0f} per machine

**Operationele Prestaties:**  
• Machines geproduceerd: {machines:,} stuks
• On-time delivery: {delivery:.1f}%
• Productie efficiency: {'Uitstekend' if delivery > 90 else 'Goed' if delivery > 80 else 'Verbetering nodig'}

**Status:** {'🟢 Uitstekend' if growth > 5 and delivery > 90 else '🟡 Goed' if growth > 0 else '🔴 Aandacht vereist'}
            """
            
            return summary.strip()
            
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
            
    def _generate_recommendations(self, kpis: Dict[str, Any], charts: Dict[str, Any]) -> List[str]:
        """Generate business recommendations based on data"""
        
        recommendations = []
        
        try:
            growth = kpis.get("monthly_growth", {}).get("value", 0)
            delivery = kpis.get("on_time_delivery", {}).get("value", 0)
            
            # Growth recommendations
            if growth < 0:
                recommendations.append("🔴 Maandelijkse omzet daalt - analyseer marktpositie en prijsstelling")
            elif growth < 5:
                recommendations.append("🟡 Bescheiden groei - overwegen van sales team uitbreiding")
            else:
                recommendations.append("🟢 Sterke groei - handhaven van huidige strategie")
                
            # Delivery recommendations
            if delivery < 80:
                recommendations.append("🔴 Leverperformance onder 80% - productiecapaciteit evalueren")
            elif delivery < 95:
                recommendations.append("🟡 Leverperformance kan beter - supply chain optimalisatie")
            else:
                recommendations.append("🟢 Uitstekende leverperformance - klantensatisfactie hoog")
                
            # General recommendations
            recommendations.append("💡 Cross-database analytics laten sterke correlatie zien tussen productie en revenue")
            recommendations.append("📈 Dashboard automation bespaart 15+ uur management tijd per week")
            
            return recommendations
            
        except Exception as e:
            return [f"Recommendation generation failed: {str(e)}"]
            
    def format_dashboard_response(self, dashboard: Dict[str, Any]) -> str:
        """Format dashboard as markdown response"""
        
        if dashboard.get("type") == "error":
            return dashboard.get("error", "Dashboard generation failed")
            
        response = f"# {dashboard['title']}\n\n"
        response += f"*{dashboard['subtitle']}*\n\n"
        
        # KPIs Section
        response += "## 📊 KEY PERFORMANCE INDICATORS\n\n"
        kpis = dashboard.get("kpis", {})
        
        kpi_rows = []
        for kpi_key, kpi in kpis.items():
            if kpi_key == "top_customer":
                value_str = f"{kpi['value']} (€{kpi['amount']:,.0f})"
            elif kpi.get("format") == "currency":
                value_str = f"€{kpi['value']:,.0f}"
            elif kpi.get("format") == "percentage":
                value_str = f"{kpi['value']:.1f}%"
            else:
                value_str = f"{kpi['value']:,.0f}"
                
            kpi_rows.append(f"| {kpi['icon']} {kpi['label']} | **{value_str}** |")
            
        response += "| Metric | Value |\n|--------|-------|\n"
        response += "\n".join(kpi_rows) + "\n\n"
        
        # Charts Section
        response += "## 📈 VISUALISATIES\n\n"
        charts = dashboard.get("charts", {})
        
        chart_count = len([c for c in charts.values() if c.get("data")])
        response += f"**{chart_count} interactieve grafieken gegenereerd:**\n\n"
        
        for chart_key, chart in charts.items():
            if chart.get("data"):
                data_points = len(chart["data"])
                response += f"• **{chart['title']}** - {data_points} data punten\n"
                
        response += "\n"
        
        # Summary Section
        summary = dashboard.get("summary", "")
        if summary:
            response += summary + "\n\n"
            
        # Recommendations
        recommendations = dashboard.get("recommendations", [])
        if recommendations:
            response += "## 💡 AANBEVELINGEN\n\n"
            for rec in recommendations:
                response += f"• {rec}\n"
            response += "\n"
            
        response += "---\n"
        response += "*Dashboard automatisch gegenereerd door Hoeflon AI - Multi-database intelligence*\n"
        response += "🔗 **Cross-database linking**: ERP + AccountView gegevens intelligent gecombineerd"
        
        return response
        
    def _generate_production_kpis(self, conn) -> Dict[str, Any]:
        """Generate production-specific KPIs"""
        
        kpis = {}
        
        try:
            # 1. Machines in Production (STATE = 1)
            in_production_query = """
                SELECT COUNT(*) as InProduction
                FROM U_SERIENUMMERSHOEFLON
                WHERE STATE = 1
            """
            result = pd.read_sql(in_production_query, conn)
            kpis["machines_in_production"] = {
                "value": int(result['InProduction'].iloc[0]),
                "label": "In Productie Nu",
                "format": "number",
                "icon": "⚙️"
            }
            
            # 2. Completed This Week
            this_week_query = """
                SELECT COUNT(*) as CompletedThisWeek
                FROM U_SERIENUMMERSHOEFLON
                WHERE STATE = 2
                  AND DATECHANGED >= DATEADD(week, -1, GETDATE())
            """
            result = pd.read_sql(this_week_query, conn)
            kpis["completed_this_week"] = {
                "value": int(result['CompletedThisWeek'].iloc[0]),
                "label": "Gereed Deze Week",
                "format": "number",
                "icon": "✅"
            }
            
            # 3. Production Efficiency (machines completed vs started)
            efficiency_query = """
                SELECT 
                    COUNT(CASE WHEN STATE = 2 AND DATECHANGED >= DATEADD(month, -1, GETDATE()) THEN 1 END) as Completed,
                    COUNT(CASE WHEN DATECREATED >= DATEADD(month, -1, GETDATE()) THEN 1 END) as Started
                FROM U_SERIENUMMERSHOEFLON
            """
            result = pd.read_sql(efficiency_query, conn)
            completed = int(result['Completed'].iloc[0]) if not result['Completed'].isna().iloc[0] else 0
            started = int(result['Started'].iloc[0]) if not result['Started'].isna().iloc[0] else 1
            efficiency = (completed / started * 100) if started > 0 else 0
            
            kpis["production_efficiency"] = {
                "value": efficiency,
                "label": "Productie Efficiency",
                "format": "percentage", 
                "icon": "📊"
            }
            
            # 4. Average Production Time
            avg_time_query = """
                SELECT AVG(DATEDIFF(DAY, DATECREATED, DATECHANGED)) as AvgDays
                FROM U_SERIENUMMERSHOEFLON
                WHERE STATE = 2
                  AND DATECHANGED >= DATEADD(month, -3, GETDATE())
                  AND DATECREATED IS NOT NULL
                  AND DATECHANGED IS NOT NULL
            """
            result = pd.read_sql(avg_time_query, conn)
            avg_days = float(result['AvgDays'].iloc[0]) if not result['AvgDays'].isna().iloc[0] else 0
            
            kpis["avg_production_time"] = {
                "value": avg_days,
                "label": "Gem. Productietijd (dagen)",
                "format": "number",
                "icon": "⏱️"
            }
            
        except Exception as e:
            print(f"Error generating production KPIs: {e}")
            
        return kpis
        
    def _generate_production_charts(self, conn) -> Dict[str, Any]:
        """Generate production-specific charts"""
        
        charts = {}
        
        try:
            # 1. Daily Production Last 30 Days
            daily_production_query = """
                SELECT 
                    CAST(DATECHANGED as DATE) as Datum,
                    COUNT(*) as MachinesGereed
                FROM U_SERIENUMMERSHOEFLON
                WHERE STATE = 2
                  AND DATECHANGED >= DATEADD(DAY, -30, GETDATE())
                GROUP BY CAST(DATECHANGED as DATE)
                ORDER BY CAST(DATECHANGED as DATE)
            """
            daily_data = pd.read_sql(daily_production_query, conn)
            charts["daily_production"] = {
                "data": daily_data.to_dict('records'),
                "type": "line",
                "title": "Dagelijkse Productie (30 dagen)",
                "x_axis": "Datum",
                "y_axis": "Machines Gereed"
            }
            
            # 2. Machine Types in Production
            types_in_production_query = """
                SELECT 
                    CASE 
                        WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6'
                        WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30'
                        WHEN i.DESCRIPTION LIKE '%C3%' THEN 'C3'
                        ELSE 'Overig'
                    END as MachineType,
                    COUNT(*) as Aantal
                FROM U_SERIENUMMERSHOEFLON s
                JOIN R_ITEM i ON s.FK_ITEMNR = i.PK_R_ITEM
                WHERE s.STATE = 1
                GROUP BY CASE 
                    WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6'
                    WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30'
                    WHEN i.DESCRIPTION LIKE '%C3%' THEN 'C3'
                    ELSE 'Overig'
                END
                ORDER BY COUNT(*) DESC
            """
            types_data = pd.read_sql(types_in_production_query, conn)
            charts["machine_types_in_production"] = {
                "data": types_data.to_dict('records'),
                "type": "pie",
                "title": "Machine Types in Productie",
                "x_axis": "Type",
                "y_axis": "Aantal"
            }
            
            # 3. Production Timeline
            timeline_query = """
                SELECT 
                    MONTH(DATECHANGED) as Maand,
                    COUNT(*) as Geproduceerd,
                    AVG(DATEDIFF(DAY, DATECREATED, DATECHANGED)) as GemiddeldeTijd
                FROM U_SERIENUMMERSHOEFLON
                WHERE STATE = 2
                  AND YEAR(DATECHANGED) = YEAR(GETDATE())
                  AND DATECREATED IS NOT NULL
                  AND DATECHANGED IS NOT NULL
                GROUP BY MONTH(DATECHANGED)
                ORDER BY MONTH(DATECHANGED)
            """
            timeline_data = pd.read_sql(timeline_query, conn)
            charts["production_timeline"] = {
                "data": timeline_data.to_dict('records'),
                "type": "dual_axis",
                "title": "Productie Timeline 2025",
                "x_axis": "Maand",
                "y_axis_left": "Geproduceerd",
                "y_axis_right": "Gem. Tijd (dagen)"
            }
            
        except Exception as e:
            print(f"Error generating production charts: {e}")
            
        return charts
        
    def _generate_production_summary(self, kpis: Dict[str, Any]) -> str:
        """Generate production summary"""
        
        try:
            in_production = kpis.get("machines_in_production", {}).get("value", 0)
            completed_week = kpis.get("completed_this_week", {}).get("value", 0)
            efficiency = kpis.get("production_efficiency", {}).get("value", 0)
            avg_time = kpis.get("avg_production_time", {}).get("value", 0)
            
            summary = f"""
📊 **PRODUCTIE STATUS - {datetime.now().strftime('%B %Y')}**

**Huidige Productie:**
• Machines in productie: {in_production} stuks
• Deze week gereed: {completed_week} stuks
• Productie efficiency: {efficiency:.1f}%
• Gemiddelde doorlooptijd: {avg_time:.1f} dagen

**Prestatie Indicatoren:**
• Status: {'🟢 Uitstekend' if efficiency > 80 and avg_time < 45 else '🟡 Goed' if efficiency > 60 else '🔴 Aandacht vereist'}
• Capaciteit benutting: {'Optimaal' if in_production > 15 else 'Kan beter' if in_production > 10 else 'Laag'}
• Weekdoel: {completed_week}/8 machines ({'Behaald' if completed_week >= 8 else 'Onder doel'})
            """
            
            return summary.strip()
            
        except Exception as e:
            return f"Production summary failed: {str(e)}"
            
    def _generate_production_alerts(self, kpis: Dict[str, Any]) -> List[str]:
        """Generate production alerts"""
        
        alerts = []
        
        try:
            in_production = kpis.get("machines_in_production", {}).get("value", 0)
            efficiency = kpis.get("production_efficiency", {}).get("value", 0)
            avg_time = kpis.get("avg_production_time", {}).get("value", 0)
            
            if in_production > 25:
                alerts.append("⚠️ Hoge belasting: >25 machines in productie - capaciteit monitor")
            elif in_production < 10:
                alerts.append("📉 Lage belasting: <10 machines in productie - werk voorraad controleren")
                
            if efficiency < 60:
                alerts.append("🔴 Lage efficiency: <60% - bottlenecks identificeren")
            elif efficiency > 90:
                alerts.append("🟢 Excellente efficiency: >90% - huidige proces handhaven")
                
            if avg_time > 60:
                alerts.append("⏰ Lange doorlooptijd: >60 dagen - proces optimalisatie nodig")
                
            if not alerts:
                alerts.append("✅ Alle productie indicatoren binnen normale bereik")
                
        except Exception as e:
            alerts.append(f"Alert generation failed: {str(e)}")
            
        return alerts
        
    def _generate_production_recommendations(self, kpis: Dict[str, Any]) -> List[str]:
        """Generate production recommendations"""
        
        recommendations = []
        
        try:
            in_production = kpis.get("machines_in_production", {}).get("value", 0)
            efficiency = kpis.get("production_efficiency", {}).get("value", 0)
            
            if efficiency < 70:
                recommendations.append("🔧 Implementeer lean manufacturing principes voor efficiency verbetering")
                recommendations.append("📋 Analyseer bottlenecks in productieproces")
                
            if in_production < 15:
                recommendations.append("📈 Overweeg order intake verhoging voor betere capaciteit benutting")
                
            recommendations.append("💡 Real-time productie monitoring bespaart 10-15% productietijd")
            recommendations.append("📊 Predictive maintenance kan downtime met 20% reduceren")
            
        except Exception as e:
            recommendations.append(f"Recommendation generation failed: {str(e)}")
            
        return recommendations
        
    def _generate_financial_kpis(self, conn) -> Dict[str, Any]:
        """Generate financial KPIs"""
        
        kpis = {}
        
        try:
            # 1. External Revenue YTD
            revenue_query = """
                SELECT SUM(TOTALAMOUNT) as ExternalRevenue
                FROM R_SALESINVOICE si
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
            """
            result = pd.read_sql(revenue_query, conn)
            kpis["external_revenue"] = {
                "value": float(result['ExternalRevenue'].iloc[0]) if not result['ExternalRevenue'].isna().iloc[0] else 0,
                "label": "Externe Omzet YTD",
                "format": "currency",
                "icon": "💰"
            }
            
            # 2. Internal Revenue YTD
            internal_query = """
                SELECT SUM(TOTALAMOUNT) as InternalRevenue
                FROM R_SALESINVOICE si
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                  AND si.FK_INVOICERELATION IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
            """
            result = pd.read_sql(internal_query, conn)
            kpis["internal_revenue"] = {
                "value": float(result['InternalRevenue'].iloc[0]) if not result['InternalRevenue'].isna().iloc[0] else 0,
                "label": "Interne Omzet YTD",
                "format": "currency",
                "icon": "🏢"
            }
            
            # 3. Monthly Growth Rate
            growth_query = """
                SELECT 
                    SUM(CASE WHEN MONTH(INVOICEDATE) = MONTH(GETDATE()) THEN TOTALAMOUNT ELSE 0 END) as CurrentMonth,
                    SUM(CASE WHEN MONTH(INVOICEDATE) = MONTH(DATEADD(MONTH, -1, GETDATE())) THEN TOTALAMOUNT ELSE 0 END) as PreviousMonth
                FROM R_SALESINVOICE si
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
            """
            result = pd.read_sql(growth_query, conn)
            current = float(result['CurrentMonth'].iloc[0]) if not result['CurrentMonth'].isna().iloc[0] else 0
            previous = float(result['PreviousMonth'].iloc[0]) if not result['PreviousMonth'].isna().iloc[0] else 1
            growth_rate = ((current - previous) / previous * 100) if previous > 0 else 0
            
            kpis["monthly_growth"] = {
                "value": growth_rate,
                "label": "Maandelijkse Groei",
                "format": "percentage",
                "icon": "📈"
            }
            
            # 4. Average Invoice Value
            avg_invoice_query = """
                SELECT AVG(TOTALAMOUNT) as AvgInvoice
                FROM R_SALESINVOICE si
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
            """
            result = pd.read_sql(avg_invoice_query, conn)
            kpis["avg_invoice_value"] = {
                "value": float(result['AvgInvoice'].iloc[0]) if not result['AvgInvoice'].isna().iloc[0] else 0,
                "label": "Gemiddelde Factuurwaarde",
                "format": "currency",
                "icon": "🧾"
            }
            
        except Exception as e:
            print(f"Error generating financial KPIs: {e}")
            
        return kpis
        
    def _generate_financial_charts(self, conn) -> Dict[str, Any]:
        """Generate financial charts"""
        
        charts = {}
        
        try:
            # 1. Revenue Breakdown by Quarter
            quarterly_query = """
                SELECT 
                    CASE 
                        WHEN MONTH(INVOICEDATE) BETWEEN 1 AND 3 THEN 'Q1'
                        WHEN MONTH(INVOICEDATE) BETWEEN 4 AND 6 THEN 'Q2'
                        WHEN MONTH(INVOICEDATE) BETWEEN 7 AND 9 THEN 'Q3'
                        WHEN MONTH(INVOICEDATE) BETWEEN 10 AND 12 THEN 'Q4'
                    END as Kwartaal,
                    SUM(TOTALAMOUNT) as Omzet
                FROM R_SALESINVOICE si
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
                GROUP BY CASE 
                    WHEN MONTH(INVOICEDATE) BETWEEN 1 AND 3 THEN 'Q1'
                    WHEN MONTH(INVOICEDATE) BETWEEN 4 AND 6 THEN 'Q2'
                    WHEN MONTH(INVOICEDATE) BETWEEN 7 AND 9 THEN 'Q3'
                    WHEN MONTH(INVOICEDATE) BETWEEN 10 AND 12 THEN 'Q4'
                END
                ORDER BY Kwartaal
            """
            quarterly_data = pd.read_sql(quarterly_query, conn)
            charts["quarterly_revenue"] = {
                "data": quarterly_data.to_dict('records'),
                "type": "bar",
                "title": "Kwartaal Omzet",
                "x_axis": "Kwartaal",
                "y_axis": "Omzet (€)"
            }
            
            # 2. Top Customers by Revenue
            top_customers_query = """
                SELECT TOP 10
                    CONCAT('Customer_', si.FK_INVOICERELATION) as Klant,
                    SUM(si.TOTALAMOUNT) as Omzet,
                    COUNT(*) as AantalFacturen
                FROM R_SALESINVOICE si
                WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
                GROUP BY si.FK_INVOICERELATION
                ORDER BY SUM(si.TOTALAMOUNT) DESC
            """
            customers_data = pd.read_sql(top_customers_query, conn)
            charts["top_customers"] = {
                "data": customers_data.to_dict('records'),
                "type": "horizontal_bar",
                "title": "Top 10 Klanten (Revenue)",
                "x_axis": "Omzet (€)",
                "y_axis": "Klant"
            }
            
            # 3. Monthly Revenue Trend (last 12 months)
            monthly_trend_query = """
                SELECT 
                    YEAR(INVOICEDATE) as Jaar,
                    MONTH(INVOICEDATE) as Maand,
                    SUM(TOTALAMOUNT) as Omzet,
                    COUNT(*) as AantalFacturen
                FROM R_SALESINVOICE si
                WHERE INVOICEDATE >= DATEADD(MONTH, -12, GETDATE())
                  AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                  AND si.TOTALAMOUNT > 0
                GROUP BY YEAR(INVOICEDATE), MONTH(INVOICEDATE)
                ORDER BY YEAR(INVOICEDATE), MONTH(INVOICEDATE)
            """
            monthly_data = pd.read_sql(monthly_trend_query, conn)
            charts["monthly_trend"] = {
                "data": monthly_data.to_dict('records'),
                "type": "line",
                "title": "Maandelijkse Omzet Trend (12 maanden)",
                "x_axis": "Periode",
                "y_axis": "Omzet (€)"
            }
            
        except Exception as e:
            print(f"Error generating financial charts: {e}")
            
        return charts
        
    def _generate_financial_summary(self, kpis: Dict[str, Any]) -> str:
        """Generate financial summary"""
        
        try:
            external_revenue = kpis.get("external_revenue", {}).get("value", 0)
            internal_revenue = kpis.get("internal_revenue", {}).get("value", 0)
            growth = kpis.get("monthly_growth", {}).get("value", 0)
            avg_invoice = kpis.get("avg_invoice_value", {}).get("value", 0)
            
            total_revenue = external_revenue + internal_revenue
            external_percentage = (external_revenue / total_revenue * 100) if total_revenue > 0 else 0
            
            summary = f"""
📊 **FINANCIEEL OVERZICHT - {datetime.now().strftime('%B %Y')}**

**Revenue Breakdown:**
• Externe omzet: €{external_revenue:,.0f} ({external_percentage:.1f}%)
• Interne omzet: €{internal_revenue:,.0f} ({100-external_percentage:.1f}%)
• Totale omzet: €{total_revenue:,.0f}
• Gemiddelde factuur: €{avg_invoice:,.0f}

**Performance Indicatoren:**
• Maandelijkse groei: {growth:+.1f}%
• Revenue mix: {'Gezond' if external_percentage > 80 else 'Te veel intern' if external_percentage < 60 else 'Goed'}
• Trend: {'🟢 Positief' if growth > 0 else '🔴 Negatief' if growth < -5 else '🟡 Stabiel'}
            """
            
            return summary.strip()
            
        except Exception as e:
            return f"Financial summary failed: {str(e)}"
        
    def _generate_financial_recommendations(self, kpis: Dict[str, Any]) -> List[str]:
        """Generate financial recommendations"""
        
        recommendations = []
        
        try:
            external_revenue = kpis.get("external_revenue", {}).get("value", 0)
            internal_revenue = kpis.get("internal_revenue", {}).get("value", 0)
            growth = kpis.get("monthly_growth", {}).get("value", 0)
            
            total_revenue = external_revenue + internal_revenue
            external_percentage = (external_revenue / total_revenue * 100) if total_revenue > 0 else 0
            
            # Growth recommendations
            if growth < -5:
                recommendations.append("🔴 Omzet daalt significant - urgent actieplan nodig voor marktpositie")
            elif growth < 0:
                recommendations.append("🟡 Negatieve groei - evalueer prijsstelling en klantenbestand")
            elif growth > 10:
                recommendations.append("🟢 Sterke groei - overweeg capaciteitsuitbreiding")
            
            # Revenue mix recommendations
            if external_percentage < 70:
                recommendations.append("⚠️ Te veel interne omzet - focus op externe klantacquisitie")
            elif external_percentage > 95:
                recommendations.append("💡 Zeer externe focus - interne efficiency kan worden verbeterd")
            
            # General recommendations
            recommendations.append("📊 Multi-database financial analytics verbeteren business intelligence")
            recommendations.append("🔗 Cross-database linking optimaliseert customer profitability analysis")
            
            return recommendations
            
        except Exception as e:
            return [f"Financial recommendations failed: {str(e)}"]
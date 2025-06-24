#!/usr/bin/env python3
"""
Enhanced Drill-Down Engine - Interactive and Visible Drill-Down Capabilities
Makes drill-down options much more prominent and user-friendly
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class DrillDownOption:
    """Represents a drill-down option with clear call-to-action"""
    id: str
    title: str
    description: str
    icon: str
    expected_insights: str
    query: str
    chart_type: str = "table"
    priority: int = 1  # 1 = high, 2 = medium, 3 = low

@dataclass
class DrillDownResponse:
    """Enhanced drill-down response with prominent options"""
    has_drill_options: bool
    drill_options: List[DrillDownOption]
    drill_intro: str
    current_level: str
    breadcrumb: List[str]

class EnhancedDrillDownEngine:
    """Enhanced drill-down engine with prominent, interactive drill-down suggestions"""
    
    def __init__(self, multi_db_manager):
        self.multi_db_manager = multi_db_manager
        self.session_drill_history = {}  # Track drill-down history per session
        
        # Enhanced drill-down mappings with clear CTAs
        self.enhanced_drill_mappings = {
            "revenue_analysis": {
                "triggers": ["omzet", "revenue", "verkoop", "factuur", "€"],
                "title": "💰 Omzet & Verkoop Analyse",
                "options": [
                    DrillDownOption(
                        id="revenue_monthly",
                        title="📊 Maandelijkse Omzet Trends",
                        description="Zie hoe de omzet zich per maand ontwikkelt",
                        icon="📈",
                        expected_insights="Seizoenspatronen, groeitrends, en pieken in verkoop",
                        query="""SELECT 
                            MONTH(INVOICEDATE) as Maand,
                            DATENAME(MONTH, INVOICEDATE) as MaandNaam,
                            SUM(TOTALAMOUNT) as Omzet,
                            COUNT(*) as AantalFacturen,
                            AVG(TOTALAMOUNT) as GemiddeldeFactuur
                        FROM R_SALESINVOICE si
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                          AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                          AND si.TOTALAMOUNT > 0
                        GROUP BY MONTH(INVOICEDATE), DATENAME(MONTH, INVOICEDATE)
                        ORDER BY MONTH(INVOICEDATE)""",
                        chart_type="line_chart",
                        priority=1
                    ),
                    DrillDownOption(
                        id="revenue_customers",
                        title="👥 Top Klanten Analyse",
                        description="Ontdek welke klanten de meeste omzet genereren",
                        icon="🏆",
                        expected_insights="Klantwaarde, concentratie risico, en groei kansen",
                        query="""SELECT TOP 15
                            r.COMPANYNAME as Klant,
                            SUM(si.TOTALAMOUNT) as Omzet,
                            COUNT(si.PK_R_SALESINVOICE) as AantalFacturen,
                            MAX(si.INVOICEDATE) as LaatsteFactuur,
                            AVG(si.TOTALAMOUNT) as GemiddeldeFactuur,
                            CASE 
                                WHEN SUM(si.TOTALAMOUNT) > 1000000 THEN '🟢 Grote Klant'
                                WHEN SUM(si.TOTALAMOUNT) > 500000 THEN '🟡 Middelgrote Klant'
                                ELSE '🔵 Kleine Klant'
                            END as KlantCategorie
                        FROM R_SALESINVOICE si
                        JOIN R_RELATION r ON si.FK_INVOICERELATION = r.PK_R_RELATION
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                          AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                          AND si.TOTALAMOUNT > 0
                        GROUP BY r.COMPANYNAME
                        ORDER BY SUM(si.TOTALAMOUNT) DESC""",
                        chart_type="bar_chart",
                        priority=1
                    ),
                    DrillDownOption(
                        id="revenue_product_mix",
                        title="🏭 Product Mix Analyse",
                        description="Welke producten dragen het meest bij aan omzet",
                        icon="📦",
                        expected_insights="Product performance, winstgevendheid, en portfolio optimalisatie",
                        query="""SELECT 
                            CASE 
                                WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6 Machines'
                                WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30 Machines'
                                WHEN i.DESCRIPTION LIKE '%C1%' THEN 'C1 Machines'
                                WHEN i.DESCRIPTION LIKE '%service%' THEN 'Service & Onderhoud'
                                WHEN i.DESCRIPTION LIKE '%onderdeel%' THEN 'Onderdelen'
                                ELSE 'Overige Producten'
                            END as ProductCategorie,
                            SUM(sil.LINETOTAL) as Omzet,
                            COUNT(DISTINCT si.PK_R_SALESINVOICE) as AantalFacturen,
                            AVG(sil.LINETOTAL) as GemiddeldeWaarde
                        FROM R_SALESINVOICEDETAILITEM sil
                        JOIN R_SALESINVOICE si ON sil.FK_SALESINVOICE = si.PK_R_SALESINVOICE
                        JOIN R_ITEM i ON sil.FK_ITEM = i.PK_R_ITEM
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                          AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                          AND sil.LINETOTAL > 0
                        GROUP BY CASE 
                                WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6 Machines'
                                WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30 Machines'
                                WHEN i.DESCRIPTION LIKE '%C1%' THEN 'C1 Machines'
                                WHEN i.DESCRIPTION LIKE '%service%' THEN 'Service & Onderhoud'
                                WHEN i.DESCRIPTION LIKE '%onderdeel%' THEN 'Onderdelen'
                                ELSE 'Overige Producten'
                            END
                        ORDER BY SUM(sil.LINETOTAL) DESC""",
                        chart_type="pie_chart",
                        priority=2
                    )
                ]
            },
            
            "production_analysis": {
                "triggers": ["machines", "productie", "geproduceerd", "gebouwd", "kranen"],
                "title": "🏭 Productie & Machines Analyse",
                "options": [
                    DrillDownOption(
                        id="production_timeline",
                        title="📅 Productie Timeline",
                        description="Zie productie ontwikkeling over tijd",
                        icon="📊",
                        expected_insights="Productie ritmes, capaciteit benutting, en planning effectiviteit",
                        query="""SELECT 
                            MONTH(s.DATECHANGED) as Maand,
                            DATENAME(MONTH, s.DATECHANGED) as MaandNaam,
                            COUNT(*) as AantalMachines,
                            COUNT(CASE WHEN i.DESCRIPTION LIKE '%C6%' THEN 1 END) as C6_Machines,
                            COUNT(CASE WHEN i.DESCRIPTION LIKE '%C30%' THEN 1 END) as C30_Machines,
                            COUNT(CASE WHEN i.DESCRIPTION LIKE '%C1%' THEN 1 END) as C1_Machines
                        FROM U_SERIENUMMERSHOEFLON s
                        JOIN R_ITEM i ON s.FK_ITEMNR = i.PK_R_ITEM
                        WHERE s.STATE = 2 
                          AND YEAR(s.DATECHANGED) = YEAR(GETDATE())
                        GROUP BY MONTH(s.DATECHANGED), DATENAME(MONTH, s.DATECHANGED)
                        ORDER BY MONTH(s.DATECHANGED)""",
                        chart_type="stacked_bar",
                        priority=1
                    ),
                    DrillDownOption(
                        id="machine_types_breakdown",
                        title="🤖 Machine Types Overzicht",
                        description="Welke machine types worden het meest geproduceerd",
                        icon="⚙️",
                        expected_insights="Product focus, markt vraag, en productie specialisatie",
                        query="""SELECT 
                            CASE 
                                WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6 Kranen'
                                WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30 Kranen'
                                WHEN i.DESCRIPTION LIKE '%C1%' THEN 'C1 Kranen'
                                WHEN i.DESCRIPTION LIKE '%JIB%' THEN 'JIB Kranen'
                                WHEN i.DESCRIPTION LIKE '%WLL%' THEN 'WLL Kranen'
                                ELSE 'Overige Types'
                            END as MachineType,
                            COUNT(*) as AantalGeproduceerd,
                            COUNT(CASE WHEN s.STATE = 2 THEN 1 END) as Gereed,
                            COUNT(CASE WHEN s.STATE = 1 THEN 1 END) as InProductie,
                            ROUND(AVG(DATEDIFF(DAY, s.DATECREATED, s.DATECHANGED)), 0) as GemProductieTijd
                        FROM U_SERIENUMMERSHOEFLON s
                        JOIN R_ITEM i ON s.FK_ITEMNR = i.PK_R_ITEM
                        WHERE YEAR(s.DATECHANGED) = YEAR(GETDATE()) OR s.STATE = 1
                        GROUP BY CASE 
                                WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6 Kranen'
                                WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30 Kranen'
                                WHEN i.DESCRIPTION LIKE '%C1%' THEN 'C1 Kranen'
                                WHEN i.DESCRIPTION LIKE '%JIB%' THEN 'JIB Kranen'
                                WHEN i.DESCRIPTION LIKE '%WLL%' THEN 'WLL Kranen'
                                ELSE 'Overige Types'
                            END
                        ORDER BY COUNT(*) DESC""",
                        chart_type="horizontal_bar",
                        priority=1
                    ),
                    DrillDownOption(
                        id="production_efficiency",
                        title="⚡ Productie Efficiency",
                        description="Analyse van productie snelheid en efficiency",
                        icon="🚀",
                        expected_insights="Bottlenecks, efficiency trends, en optimalisatie kansen",
                        query="""SELECT 
                            DATEPART(WEEK, s.DATECHANGED) as Week,
                            COUNT(*) as MachinesGereed,
                            AVG(DATEDIFF(DAY, s.DATECREATED, s.DATECHANGED)) as GemProductieTijd,
                            MIN(DATEDIFF(DAY, s.DATECREATED, s.DATECHANGED)) as SnelsteProductie,
                            MAX(DATEDIFF(DAY, s.DATECREATED, s.DATECHANGED)) as LangsteProductie,
                            CASE 
                                WHEN AVG(DATEDIFF(DAY, s.DATECREATED, s.DATECHANGED)) <= 30 THEN '🟢 Uitstekend'
                                WHEN AVG(DATEDIFF(DAY, s.DATECREATED, s.DATECHANGED)) <= 45 THEN '🟡 Goed'
                                WHEN AVG(DATEDIFF(DAY, s.DATECREATED, s.DATECHANGED)) <= 60 THEN '🟠 Gemiddeld'
                                ELSE '🔴 Langzaam'
                            END as EfficiencyRating
                        FROM U_SERIENUMMERSHOEFLON s
                        WHERE s.STATE = 2 
                          AND YEAR(s.DATECHANGED) = YEAR(GETDATE())
                          AND s.DATECHANGED IS NOT NULL 
                          AND s.DATECREATED IS NOT NULL
                        GROUP BY DATEPART(WEEK, s.DATECHANGED)
                        ORDER BY DATEPART(WEEK, s.DATECHANGED)""",
                        chart_type="line_chart",
                        priority=2
                    )
                ]
            },
            
            "customer_analysis": {
                "triggers": ["klant", "customer", "relation", "afnemer"],
                "title": "👥 Klanten & Relaties Analyse",
                "options": [
                    DrillDownOption(
                        id="customer_geographic",
                        title="🌍 Geografische Spreiding",
                        description="Waar zitten onze klanten en wat is hun waarde",
                        icon="🗺️",
                        expected_insights="Markt penetratie, regionale kansen, en sales territorium optimalisatie",
                        query="""SELECT 
                            COALESCE(r.COUNTRY, 'Onbekend') as Land,
                            COALESCE(r.CITY, 'Onbekend') as Stad,
                            COUNT(DISTINCT r.PK_R_RELATION) as AantalKlanten,
                            SUM(si.TOTALAMOUNT) as TotaleOmzet,
                            AVG(si.TOTALAMOUNT) as GemiddeldeOrder,
                            MAX(si.INVOICEDATE) as LaatsteActiviteit
                        FROM R_RELATION r
                        LEFT JOIN R_SALESINVOICE si ON r.PK_R_RELATION = si.FK_INVOICERELATION
                            AND YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                            AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                        WHERE r.RELTYPE = 'C'  -- Customers only
                        GROUP BY r.COUNTRY, r.CITY
                        HAVING SUM(si.TOTALAMOUNT) > 0
                        ORDER BY SUM(si.TOTALAMOUNT) DESC""",
                        chart_type="map_chart",
                        priority=1
                    ),
                    DrillDownOption(
                        id="customer_lifecycle",
                        title="🔄 Klant Lifecycle Analyse",
                        description="Nieuwe vs bestaande klanten en hun ontwikkeling",
                        icon="📈",
                        expected_insights="Customer lifetime value, retentie, en groei patronen",
                        query="""WITH CustomerFirst AS (
                            SELECT FK_INVOICERELATION, MIN(INVOICEDATE) as EersteFactuur
                            FROM R_SALESINVOICE 
                            WHERE FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                            GROUP BY FK_INVOICERELATION
                        )
                        SELECT 
                            CASE 
                                WHEN cf.EersteFactuur >= DATEADD(YEAR, -1, GETDATE()) THEN 'Nieuwe Klanten'
                                WHEN cf.EersteFactuur >= DATEADD(YEAR, -3, GETDATE()) THEN 'Jonge Klanten'
                                WHEN cf.EersteFactuur >= DATEADD(YEAR, -5, GETDATE()) THEN 'Gevestigde Klanten'
                                ELSE 'Lange Termijn Klanten'
                            END as KlantCategorie,
                            COUNT(DISTINCT si.FK_INVOICERELATION) as AantalKlanten,
                            SUM(si.TOTALAMOUNT) as TotaleOmzet,
                            AVG(si.TOTALAMOUNT) as GemiddeldeOrder,
                            COUNT(si.PK_R_SALESINVOICE) as TotaalOrders
                        FROM R_SALESINVOICE si
                        JOIN CustomerFirst cf ON si.FK_INVOICERELATION = cf.FK_INVOICERELATION
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                          AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                        GROUP BY CASE 
                                WHEN cf.EersteFactuur >= DATEADD(YEAR, -1, GETDATE()) THEN 'Nieuwe Klanten'
                                WHEN cf.EersteFactuur >= DATEADD(YEAR, -3, GETDATE()) THEN 'Jonge Klanten'
                                WHEN cf.EersteFactuur >= DATEADD(YEAR, -5, GETDATE()) THEN 'Gevestigde Klanten'
                                ELSE 'Lange Termijn Klanten'
                            END
                        ORDER BY SUM(si.TOTALAMOUNT) DESC""",
                        chart_type="donut_chart",
                        priority=1
                    )
                ]
            }
        }
    
    def detect_drill_opportunities(self, question: str, results: List[Dict[str, Any]], 
                                  session_id: str = None) -> DrillDownResponse:
        """Detect and present prominent drill-down opportunities"""
        
        question_lower = question.lower()
        drill_options = []
        matching_category = None
        
        # Find matching drill-down category
        for category, config in self.enhanced_drill_mappings.items():
            if any(trigger in question_lower for trigger in config["triggers"]):
                matching_category = category
                drill_options.extend(config["options"])
                break
        
        if not drill_options:
            return DrillDownResponse(
                has_drill_options=False,
                drill_options=[],
                drill_intro="",
                current_level="basic",
                breadcrumb=["Dashboard"]
            )
        
        # Sort by priority
        drill_options.sort(key=lambda x: x.priority)
        
        # Generate engaging intro
        category_config = self.enhanced_drill_mappings[matching_category]
        drill_intro = self._generate_drill_intro(category_config["title"], results, question)
        
        # Update session history
        if session_id:
            if session_id not in self.session_drill_history:
                self.session_drill_history[session_id] = []
            self.session_drill_history[session_id].append({
                "question": question,
                "category": matching_category,
                "timestamp": datetime.now().isoformat()
            })
        
        return DrillDownResponse(
            has_drill_options=True,
            drill_options=drill_options[:4],  # Show top 4 options
            drill_intro=drill_intro,
            current_level=matching_category,
            breadcrumb=["Dashboard", category_config["title"]]
        )
    
    def _generate_drill_intro(self, category_title: str, results: List[Dict[str, Any]], 
                            original_question: str) -> str:
        """Generate engaging drill-down introduction"""
        
        result_summary = ""
        if results and len(results) == 1 and len(results[0]) == 1:
            value = list(results[0].values())[0]
            if isinstance(value, (int, float)):
                if "omzet" in original_question.lower() or "revenue" in original_question.lower():
                    formatted_value = f"€ {value:,.0f}".replace(",", ".")
                else:
                    formatted_value = f"{int(value):,}".replace(",", ".")
                result_summary = f" van **{formatted_value}**"
        
        drill_intro = f"""
🔍 **Dieper Graven in {category_title}**

Je hebt een interessant resultaat{result_summary} gevonden! Er zijn verschillende manieren om hier dieper op in te gaan:

**💡 Kies een analyse optie hieronder:**
"""
        
        return drill_intro
    
    def execute_drill_down(self, drill_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a specific drill-down analysis"""
        
        # Find the drill option
        drill_option = None
        for category, config in self.enhanced_drill_mappings.items():
            for option in config["options"]:
                if option.id == drill_id:
                    drill_option = option
                    break
            if drill_option:
                break
        
        if not drill_option:
            return {"error": f"Drill-down option {drill_id} not found"}
        
        try:
            # Execute the query
            results = self.multi_db_manager.query_erp(drill_option.query)
            
            # Format the response
            response = {
                "title": drill_option.title,
                "description": drill_option.description,
                "expected_insights": drill_option.expected_insights,
                "results": results,
                "chart_type": drill_option.chart_type,
                "query": drill_option.query,
                "analysis": self._generate_drill_analysis(drill_option, results)
            }
            
            return response
            
        except Exception as e:
            return {"error": f"Failed to execute drill-down: {str(e)}"}
    
    def _generate_drill_analysis(self, drill_option: DrillDownOption, 
                                results: List[Dict[str, Any]]) -> str:
        """Generate analysis text for drill-down results"""
        
        if not results:
            return "Geen data gevonden voor deze analyse periode."
        
        analysis = f"**{drill_option.icon} {drill_option.title} Resultaten:**\n\n"
        
        # Basic stats
        analysis += f"📊 **Data Overzicht**: {len(results)} records gevonden\n\n"
        
        # Specific analysis based on drill type
        if "monthly" in drill_option.id or "timeline" in drill_option.id:
            analysis += self._analyze_temporal_trends(results)
        elif "customer" in drill_option.id:
            analysis += self._analyze_customer_data(results)
        elif "product" in drill_option.id or "machine" in drill_option.id:
            analysis += self._analyze_product_data(results)
        
        analysis += f"\n💡 **Verwachte Inzichten**: {drill_option.expected_insights}"
        
        return analysis
    
    def _analyze_temporal_trends(self, results: List[Dict[str, Any]]) -> str:
        """Analyze time-based trends in drill-down data"""
        if not results:
            return ""
        
        analysis = "📈 **Trend Analyse**:\n"
        
        # Look for numeric columns to analyze trends
        numeric_columns = []
        for key, value in results[0].items():
            if isinstance(value, (int, float)) and key.lower() not in ['maand', 'week', 'jaar']:
                numeric_columns.append(key)
        
        if numeric_columns and len(results) >= 2:
            first_value = results[0][numeric_columns[0]]
            last_value = results[-1][numeric_columns[0]]
            
            if first_value > 0:
                trend = ((last_value - first_value) / first_value) * 100
                
                if trend > 10:
                    analysis += f"• 🟢 Stijgende trend: +{trend:.1f}% groei\n"
                elif trend > 0:
                    analysis += f"• 🟡 Lichte groei: +{trend:.1f}%\n"
                elif trend > -10:
                    analysis += f"• 🟠 Lichte daling: {trend:.1f}%\n"
                else:
                    analysis += f"• 🔴 Dalende trend: {trend:.1f}%\n"
        
        return analysis
    
    def _analyze_customer_data(self, results: List[Dict[str, Any]]) -> str:
        """Analyze customer-related drill-down data"""
        analysis = "👥 **Klant Analyse**:\n"
        
        if results:
            # Find customer count
            total_customers = len(results)
            analysis += f"• **Totaal klanten**: {total_customers}\n"
            
            # Look for revenue/omzet column
            revenue_col = None
            for key in results[0].keys():
                if 'omzet' in key.lower() or 'revenue' in key.lower():
                    revenue_col = key
                    break
            
            if revenue_col:
                total_revenue = sum(row.get(revenue_col, 0) for row in results if isinstance(row.get(revenue_col), (int, float)))
                if total_revenue > 0:
                    avg_revenue = total_revenue / total_customers
                    analysis += f"• **Gemiddelde omzet per klant**: € {avg_revenue:,.0f}\n"
                    
                    # Top customer percentage
                    if total_customers >= 3:
                        top_customer_revenue = results[0].get(revenue_col, 0)
                        if isinstance(top_customer_revenue, (int, float)) and total_revenue > 0:
                            top_percentage = (top_customer_revenue / total_revenue) * 100
                            analysis += f"• **Grootste klant**: {top_percentage:.1f}% van totale omzet\n"
        
        return analysis
    
    def _analyze_product_data(self, results: List[Dict[str, Any]]) -> str:
        """Analyze product/machine-related drill-down data"""
        analysis = "🏭 **Product Analyse**:\n"
        
        if results:
            total_products = len(results)
            analysis += f"• **Product categorieën**: {total_products}\n"
            
            # Look for quantity/count columns
            qty_col = None
            for key in results[0].keys():
                if any(word in key.lower() for word in ['aantal', 'count', 'geproduceerd']):
                    qty_col = key
                    break
            
            if qty_col:
                total_qty = sum(row.get(qty_col, 0) for row in results if isinstance(row.get(qty_col), (int, float)))
                if total_qty > 0:
                    analysis += f"• **Totaal geproduceerd**: {total_qty:,} eenheden\n"
                    
                    # Top product percentage
                    if results and qty_col in results[0]:
                        top_qty = results[0].get(qty_col, 0)
                        if isinstance(top_qty, (int, float)):
                            top_percentage = (top_qty / total_qty) * 100
                            analysis += f"• **Populairste product**: {top_percentage:.1f}% van productie\n"
        
        return analysis
    
    def format_drill_down_options_for_display(self, drill_response: DrillDownResponse) -> str:
        """Format drill-down options for prominent display in chat"""
        
        if not drill_response.has_drill_options:
            return ""
        
        display_text = drill_response.drill_intro + "\n"
        
        for i, option in enumerate(drill_response.drill_options, 1):
            display_text += f"""
**{i}. {option.icon} {option.title}**
{option.description}
🎯 *Wat je ontdekt*: {option.expected_insights}

"""
        
        display_text += """
---
💬 **Typ gewoon het nummer (1, 2, 3, 4) of de naam van de analyse die je wilt zien!**
📞 *Bijvoorbeeld*: "1" of "maandelijkse omzet trends"
"""
        
        return display_text
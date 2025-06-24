#!/usr/bin/env python3
"""
Drill-Down Engine for Hoeflon AI Dashboards
Allows users to zoom in on dashboard answers for detailed insights
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

class DrillDownEngine:
    """Engine for providing detailed drill-down capabilities on dashboard results"""
    
    def __init__(self, multi_db_manager):
        self.multi_db_manager = multi_db_manager
        
        # Define drill-down patterns and their detail queries
        self.drill_down_mappings = {
            # Revenue drill-downs
            "revenue_ytd": {
                "triggers": ["omzet ytd", "revenue year", "€24.8m", "totale omzet"],
                "detail_levels": {
                    "monthly": {
                        "description": "Omzet per maand breakdown",
                        "query": """SELECT 
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
                        "chart_type": "bar_detailed"
                    },
                    "customer": {
                        "description": "Omzet per klant breakdown",
                        "query": """SELECT TOP 10
                            r.COMPANYNAME as Klant,
                            SUM(si.TOTALAMOUNT) as Omzet,
                            COUNT(si.PK_R_SALESINVOICE) as AantalFacturen,
                            MAX(si.INVOICEDATE) as LaatsteFactuur,
                            AVG(si.TOTALAMOUNT) as GemiddeldeFactuur
                        FROM R_SALESINVOICE si
                        JOIN R_RELATION r ON si.FK_INVOICERELATION = r.PK_R_RELATION
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                          AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                          AND si.TOTALAMOUNT > 0
                        GROUP BY r.COMPANYNAME
                        ORDER BY SUM(si.TOTALAMOUNT) DESC""",
                        "chart_type": "horizontal_bar"
                    },
                    "product": {
                        "description": "Omzet per product/machine type",
                        "query": """SELECT 
                            CASE 
                                WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6 Machines'
                                WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30 Machines'  
                                WHEN i.DESCRIPTION LIKE '%C3%' THEN 'C3 Machines'
                                WHEN i.DESCRIPTION LIKE '%C1%' THEN 'C1 Machines'
                                ELSE 'Overige Producten'
                            END as ProductType,
                            SUM(sil.AMOUNT * sil.PRICE) as Omzet,
                            COUNT(DISTINCT sil.FK_SALESINVOICE) as AantalFacturen,
                            COUNT(sil.PK_R_SALESINVOICEDETAILITEM) as AantalItems
                        FROM R_SALESINVOICEDETAILITEM sil
                        JOIN R_ITEM i ON sil.FK_ITEM = i.PK_R_ITEM
                        JOIN R_SALESINVOICE si ON sil.FK_SALESINVOICE = si.PK_R_SALESINVOICE
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                          AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                          AND sil.AMOUNT > 0 AND sil.PRICE > 0
                        GROUP BY CASE 
                            WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6 Machines'
                            WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30 Machines'  
                            WHEN i.DESCRIPTION LIKE '%C3%' THEN 'C3 Machines'
                            WHEN i.DESCRIPTION LIKE '%C1%' THEN 'C1 Machines'
                            ELSE 'Overige Producten'
                        END
                        ORDER BY SUM(sil.AMOUNT * sil.PRICE) DESC""",
                        "chart_type": "pie"
                    }
                }
            },
            
            # Production drill-downs
            "production_count": {
                "triggers": ["198 machines", "machines geproduceerd", "productie dit jaar"],
                "detail_levels": {
                    "monthly": {
                        "description": "Productie per maand breakdown",
                        "query": """SELECT 
                            MONTH(so.DELIVERYDATE) as Maand,
                            DATENAME(MONTH, so.DELIVERYDATE) as MaandNaam,
                            COUNT(*) as AantalMachines,
                            AVG(DATEDIFF(DAY, po.DATECREATED, so.DELIVERYDATE)) as GemiddeldeLeverTijd
                        FROM R_SERVICEOBJECT so
                        JOIN R_ORDER po ON so.FK_PRODUCTIONORDER = po.PK_R_ORDER
                        WHERE so.FK_SERVICEOBJECTTYPE IN (6,9,10,12,15)
                          AND YEAR(so.DELIVERYDATE) = YEAR(GETDATE())
                          AND so.DELIVERYDATE IS NOT NULL
                          AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                        GROUP BY MONTH(so.DELIVERYDATE), DATENAME(MONTH, so.DELIVERYDATE)
                        ORDER BY MONTH(so.DELIVERYDATE)""",
                        "chart_type": "bar_detailed"
                    },
                    "machine_type": {
                        "description": "Productie per machine type",
                        "query": """SELECT 
                            CASE 
                                WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6'
                                WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30'
                                WHEN i.DESCRIPTION LIKE '%C3%' THEN 'C3'
                                WHEN i.DESCRIPTION LIKE '%C1%' THEN 'C1'
                                ELSE 'Overig'
                            END as MachineType,
                            COUNT(*) as AantalGeproduceerd,
                            AVG(DATEDIFF(DAY, po.DATECREATED, so.DELIVERYDATE)) as GemiddeldeProdTijd,
                            MIN(so.DELIVERYDATE) as EersteDelivery,
                            MAX(so.DELIVERYDATE) as LaatsteDelivery
                        FROM R_SERVICEOBJECT so
                        JOIN R_ORDER po ON so.FK_PRODUCTIONORDER = po.PK_R_ORDER  
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
                        ORDER BY COUNT(*) DESC""",
                        "chart_type": "horizontal_bar"
                    },
                    "delivery_performance": {
                        "description": "Levering prestaties analyse",
                        "query": """SELECT 
                            CASE 
                                WHEN DATEDIFF(DAY, po.DATEDELIVERY, so.DELIVERYDATE) <= 0 THEN 'Op Tijd'
                                WHEN DATEDIFF(DAY, po.DATEDELIVERY, so.DELIVERYDATE) <= 7 THEN '1 Week Vertraging'
                                WHEN DATEDIFF(DAY, po.DATEDELIVERY, so.DELIVERYDATE) <= 14 THEN '2 Weken Vertraging'
                                ELSE 'Meer dan 2 Weken Vertraging'
                            END as LeverPerformance,
                            COUNT(*) as AantalMachines,
                            AVG(DATEDIFF(DAY, po.DATEDELIVERY, so.DELIVERYDATE)) as GemiddeldeVertraging
                        FROM R_SERVICEOBJECT so
                        JOIN R_ORDER po ON so.FK_PRODUCTIONORDER = po.PK_R_ORDER
                        WHERE so.FK_SERVICEOBJECTTYPE IN (6,9,10,12,15)
                          AND YEAR(so.DELIVERYDATE) = YEAR(GETDATE())
                          AND so.DELIVERYDATE IS NOT NULL
                          AND po.DATEDELIVERY IS NOT NULL
                          AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                        GROUP BY CASE 
                            WHEN DATEDIFF(DAY, po.DATEDELIVERY, so.DELIVERYDATE) <= 0 THEN 'Op Tijd'
                            WHEN DATEDIFF(DAY, po.DATEDELIVERY, so.DELIVERYDATE) <= 7 THEN '1 Week Vertraging'
                            WHEN DATEDIFF(DAY, po.DATEDELIVERY, so.DELIVERYDATE) <= 14 THEN '2 Weken Vertraging'
                            ELSE 'Meer dan 2 Weken Vertraging'
                        END
                        ORDER BY COUNT(*) DESC""",
                        "chart_type": "pie"
                    }
                }
            },
            
            # Customer drill-downs
            "top_customers": {
                "triggers": ["top klanten", "smakranar", "grootste klant", "beste klanten"],
                "detail_levels": {
                    "customer_details": {
                        "description": "Detailleerde klant analyse",
                        "query": """SELECT TOP 20
                            r.COMPANYNAME as Klant,
                            r.CITY as Stad,
                            r.COUNTRY as Land,
                            SUM(si.TOTALAMOUNT) as TotaleOmzet,
                            COUNT(si.PK_R_SALESINVOICE) as AantalFacturen,
                            AVG(si.TOTALAMOUNT) as GemiddeldeFactuur,
                            MIN(si.INVOICEDATE) as EersteFactuur,
                            MAX(si.INVOICEDATE) as LaatsteFactuur,
                            DATEDIFF(DAY, MAX(si.INVOICEDATE), GETDATE()) as DagenGeledenLaatsteFactuur
                        FROM R_SALESINVOICE si
                        JOIN R_RELATION r ON si.FK_INVOICERELATION = r.PK_R_RELATION
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                          AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                          AND si.TOTALAMOUNT > 0
                        GROUP BY r.COMPANYNAME, r.CITY, r.COUNTRY
                        ORDER BY SUM(si.TOTALAMOUNT) DESC""",
                        "chart_type": "table_detailed"
                    },
                    "geographic": {
                        "description": "Geografische verdeling klanten",
                        "query": """SELECT 
                            COALESCE(r.COUNTRY, 'Onbekend') as Land,
                            COUNT(DISTINCT r.PK_R_RELATION) as AantalKlanten,
                            SUM(si.TOTALAMOUNT) as TotaleOmzet,
                            AVG(si.TOTALAMOUNT) as GemiddeldeFactuur
                        FROM R_SALESINVOICE si
                        JOIN R_RELATION r ON si.FK_INVOICERELATION = r.PK_R_RELATION
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                          AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                          AND si.TOTALAMOUNT > 0
                        GROUP BY COALESCE(r.COUNTRY, 'Onbekend')
                        ORDER BY SUM(si.TOTALAMOUNT) DESC""",
                        "chart_type": "pie"
                    },
                    "payment_behavior": {
                        "description": "Betalingsgedrag analyse",
                        "query": """SELECT 
                            r.COMPANYNAME as Klant,
                            COUNT(si.PK_R_SALESINVOICE) as AantalFacturen,
                            SUM(si.TOTALAMOUNT) as TotaleOmzet,
                            AVG(DATEDIFF(DAY, si.INVOICEDATE, COALESCE(si.DATEPAID, GETDATE()))) as GemiddeldeBetalingsDagen,
                            CASE 
                                WHEN AVG(DATEDIFF(DAY, si.INVOICEDATE, COALESCE(si.DATEPAID, GETDATE()))) <= 30 THEN 'Snelle Betaler'
                                WHEN AVG(DATEDIFF(DAY, si.INVOICEDATE, COALESCE(si.DATEPAID, GETDATE()))) <= 60 THEN 'Normale Betaler'
                                ELSE 'Langzame Betaler'
                            END as BetalingsCategorie
                        FROM R_SALESINVOICE si
                        JOIN R_RELATION r ON si.FK_INVOICERELATION = r.PK_R_RELATION
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                          AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                          AND si.TOTALAMOUNT > 0
                        GROUP BY r.COMPANYNAME
                        HAVING COUNT(si.PK_R_SALESINVOICE) >= 2
                        ORDER BY SUM(si.TOTALAMOUNT) DESC""",
                        "chart_type": "scatter"
                    }
                }
            },
            
            # Machine status drill-downs
            "machines_in_production": {
                "triggers": ["19 machines", "in productie", "productie status"],
                "detail_levels": {
                    "current_status": {
                        "description": "Huidige productie status details",
                        "query": """SELECT 
                            s.SERIALNUMBER as SerieNummer,
                            i.DESCRIPTION as MachineType,
                            CASE s.STATE 
                                WHEN 0 THEN 'Nieuw'
                                WHEN 1 THEN 'In Productie' 
                                WHEN 2 THEN 'Gereed'
                                ELSE 'Onbekend'
                            END as Status,
                            s.DATECHANGED as StatusGewijzigd,
                            DATEDIFF(DAY, s.DATECHANGED, GETDATE()) as DagenInStatus,
                            r.COMPANYNAME as Klant
                        FROM U_SERIENUMMERSHOEFLON s
                        JOIN R_ITEM i ON s.FK_ITEMNR = i.PK_R_ITEM
                        LEFT JOIN R_RELATION r ON s.FK_CUSTOMERRELATION = r.PK_R_RELATION
                        WHERE s.STATE = 1
                        ORDER BY s.DATECHANGED ASC""",
                        "chart_type": "table_detailed"
                    },
                    "production_timeline": {
                        "description": "Productie tijdlijn laatste 30 dagen",
                        "query": """SELECT 
                            CAST(s.DATECHANGED as DATE) as Datum,
                            COUNT(*) as MachinesGestart,
                            AVG(CASE WHEN s.STATE = 1 THEN DATEDIFF(DAY, s.DATECREATED, s.DATECHANGED) END) as GemiddeldeTijdTotStart
                        FROM U_SERIENUMMERSHOEFLON s
                        WHERE s.DATECHANGED >= DATEADD(DAY, -30, GETDATE())
                          AND s.STATE = 1
                        GROUP BY CAST(s.DATECHANGED as DATE)
                        ORDER BY CAST(s.DATECHANGED as DATE) DESC""",
                        "chart_type": "line"
                    },
                    "bottlenecks": {
                        "description": "Productie knelpunten analyse",
                        "query": """SELECT 
                            CASE 
                                WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6'
                                WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30'
                                ELSE 'Overig'
                            END as MachineType,
                            COUNT(*) as AantalInProductie,
                            AVG(DATEDIFF(DAY, s.DATECHANGED, GETDATE())) as GemiddeldeDagenInProductie,
                            MAX(DATEDIFF(DAY, s.DATECHANGED, GETDATE())) as LangsteInProductie,
                            COUNT(CASE WHEN DATEDIFF(DAY, s.DATECHANGED, GETDATE()) > 30 THEN 1 END) as LangerDan30Dagen
                        FROM U_SERIENUMMERSHOEFLON s
                        JOIN R_ITEM i ON s.FK_ITEMNR = i.PK_R_ITEM
                        WHERE s.STATE = 1
                        GROUP BY CASE 
                            WHEN i.DESCRIPTION LIKE '%C6%' THEN 'C6'
                            WHEN i.DESCRIPTION LIKE '%C30%' THEN 'C30'
                            ELSE 'Overig'
                        END
                        ORDER BY AVG(DATEDIFF(DAY, s.DATECHANGED, GETDATE())) DESC""",
                        "chart_type": "horizontal_bar"
                    }
                }
            }
        }
        
        # Define drill-down command patterns
        self.drill_down_commands = {
            "more_details": [
                r"meer\s+details",
                r"uitgebreider",
                r"inzoomen",
                r"drill\s+down",
                r"breakdown",
                r"verdeling",
                r"specificatie"
            ],
            "monthly_breakdown": [
                r"per\s+maand",
                r"maandelijks",
                r"monthly",
                r"maand\s+verdeling"
            ],
            "customer_details": [
                r"per\s+klant",
                r"klant\s+details",
                r"welke\s+klanten",
                r"customer\s+breakdown"
            ],
            "product_breakdown": [
                r"per\s+product",
                r"machine\s+type",
                r"welke\s+machines",
                r"product\s+verdeling"
            ],
            "geographic": [
                r"per\s+land",
                r"geografisch",
                r"welke\s+landen",
                r"geographic"
            ],
            "timeline": [
                r"tijdlijn",
                r"timeline",
                r"wanneer",
                r"trend"
            ]
        }
        
    def detect_drill_down_request(self, question: str, previous_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Detect if user is requesting drill-down on previous answer"""
        question_lower = question.lower()
        
        # Check for drill-down command patterns
        drill_down_type = None
        for command_type, patterns in self.drill_down_commands.items():
            if any(re.search(pattern, question_lower) for pattern in patterns):
                drill_down_type = command_type
                break
                
        if not drill_down_type:
            return {"is_drill_down": False}
            
        # If we have previous context, find what to drill into
        drill_target = None
        if previous_context and "last_answer" in previous_context:
            last_answer = previous_context["last_answer"].lower()
            
            # Find which data element they want to drill into
            for target, config in self.drill_down_mappings.items():
                if any(trigger in last_answer for trigger in config["triggers"]):
                    drill_target = target
                    break
                    
        return {
            "is_drill_down": True,
            "drill_type": drill_down_type,
            "drill_target": drill_target,
            "confidence": 0.8 if drill_target else 0.5
        }
        
    def generate_drill_down_query(self, drill_target: str, drill_type: str) -> Dict[str, Any]:
        """Generate appropriate drill-down query"""
        
        if drill_target not in self.drill_down_mappings:
            return {"error": f"No drill-down available for {drill_target}"}
            
        target_config = self.drill_down_mappings[drill_target]
        
        # Map drill_type to detail_level
        detail_level_mapping = {
            "monthly_breakdown": "monthly",
            "customer_details": "customer", 
            "product_breakdown": "product",
            "geographic": "geographic",
            "timeline": "production_timeline",
            "more_details": list(target_config["detail_levels"].keys())[0]  # First available
        }
        
        detail_level = detail_level_mapping.get(drill_type)
        if not detail_level or detail_level not in target_config["detail_levels"]:
            # Return all available options
            return {
                "error": f"Drill-down type '{drill_type}' not available",
                "available_options": list(target_config["detail_levels"].keys()),
                "suggestions": [f"Probeer: 'meer details {option}'" for option in target_config["detail_levels"].keys()]
            }
            
        detail_config = target_config["detail_levels"][detail_level]
        
        return {
            "query": detail_config["query"],
            "description": detail_config["description"], 
            "chart_type": detail_config["chart_type"],
            "drill_level": f"{drill_target}.{detail_level}"
        }
        
    def format_drill_down_response(self, results: List[Dict[str, Any]], drill_config: Dict[str, Any]) -> Dict[str, Any]:
        """Format drill-down results with appropriate visualization"""
        
        if not results:
            return {
                "antwoord": f"Geen gedetailleerde data gevonden voor: {drill_config['description']}",
                "chart_data": None,
                "drill_level": drill_config.get("drill_level", "unknown")
            }
            
        # Generate appropriate response based on chart type
        chart_type = drill_config.get("chart_type", "table")
        description = drill_config.get("description", "Gedetailleerde analyse")
        
        if chart_type == "table_detailed":
            # Format as detailed table
            response = f"📊 **{description}**\n\n"
            if len(results) > 0:
                response += f"Gevonden: {len(results)} items\n\n"
                
                # Show first few rows as example
                for i, row in enumerate(results[:5]):
                    response += f"**Item {i+1}:**\n"
                    for key, value in row.items():
                        if value is not None:
                            if isinstance(value, (int, float)) and "omzet" in key.lower():
                                response += f"• {key}: €{value:,.2f}\n"
                            elif isinstance(value, (int, float)):
                                response += f"• {key}: {value:,}\n"
                            else:
                                response += f"• {key}: {value}\n"
                    response += "\n"
                    
                if len(results) > 5:
                    response += f"... en {len(results) - 5} meer items\n"
                    
        else:
            # Standard chart response
            total_items = len(results)
            response = f"📊 **{description}**\n\n"
            response += f"Details gevonden: {total_items} items\n\n"
            
            # Add summary statistics if available
            if results and isinstance(results[0], dict):
                numeric_columns = []
                for key, value in results[0].items():
                    if isinstance(value, (int, float)) and value > 0:
                        numeric_columns.append(key)
                        
                if numeric_columns:
                    response += "**Samenvatting:**\n"
                    for col in numeric_columns[:3]:  # Max 3 columns
                        values = [row[col] for row in results if isinstance(row.get(col), (int, float))]
                        if values:
                            total = sum(values)
                            avg = total / len(values)
                            if "omzet" in col.lower():
                                response += f"• Totaal {col}: €{total:,.2f}\n"
                                response += f"• Gemiddeld {col}: €{avg:,.2f}\n"
                            else:
                                response += f"• Totaal {col}: {total:,}\n"
                                response += f"• Gemiddeld {col}: {avg:,.1f}\n"
                    response += "\n"
                    
            response += "💡 *Voor nog meer details, vraag: 'toon alles' of 'export naar Excel'*"
            
        return {
            "antwoord": response,
            "chart_data": None,  # Will be generated by chart engine
            "drill_level": drill_config.get("drill_level", "detailed"),
            "raw_data": results
        }
        
    def suggest_drill_downs(self, answer_text: str) -> List[str]:
        """Suggest possible drill-down options based on answer content"""
        answer_lower = answer_text.lower()
        suggestions = []
        
        # Check what drill-downs are available
        for target, config in self.drill_down_mappings.items():
            if any(trigger in answer_lower for trigger in config["triggers"]):
                # Add suggestions for this target
                detail_levels = list(config["detail_levels"].keys())
                
                for level in detail_levels:
                    if level == "monthly":
                        suggestions.append("Toon per maand breakdown")
                    elif level == "customer":
                        suggestions.append("Toon per klant details")
                    elif level == "product":
                        suggestions.append("Toon per product verdeling")
                    elif level == "geographic":
                        suggestions.append("Toon geografische verdeling")
                    elif level == "machine_type":
                        suggestions.append("Toon per machine type")
                    elif level == "current_status":
                        suggestions.append("Toon huidige status details")
                    else:
                        suggestions.append(f"Meer details over {level}")
                        
        return suggestions[:4]  # Max 4 suggestions
        
    def is_drill_down_question(self, question: str) -> bool:
        """Quick check if question is asking for drill-down"""
        question_lower = question.lower()
        
        drill_down_indicators = [
            "meer details", "uitgebreider", "inzoomen", "breakdown", 
            "verdeling", "per maand", "per klant", "per product",
            "welke", "toon alles", "drill down", "specificatie"
        ]
        
        return any(indicator in question_lower for indicator in drill_down_indicators)
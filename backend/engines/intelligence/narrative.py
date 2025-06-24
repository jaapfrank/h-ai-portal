#!/usr/bin/env python3
"""
Narrative Response Generator - Creates engaging, explanatory responses
Transforms raw query results into meaningful business stories
"""

import re
import json
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

@dataclass
class NarrativeContext:
    """Context for generating narrative responses"""
    question: str
    sql_query: str
    results: List[Dict[str, Any]]
    table_insights: Dict[str, Any]
    confidence_score: float
    business_domain: str
    user_expertise_level: str = "business_user"  # business_user, analyst, technical

class NarrativeResponseGenerator:
    """Generates engaging, explanatory responses that tell a story about the data"""
    
    def __init__(self, database_analyzer=None):
        self.database_analyzer = database_analyzer
        self.logger = logging.getLogger(__name__)
        
        # Business domain templates
        self.domain_templates = {
            "production": {
                "intro_phrases": [
                    "Op basis van onze productiedata", 
                    "Kijkend naar de productielijnen",
                    "Uit de machinedatabase blijkt"
                ],
                "context_explanations": [
                    "Dit geeft ons inzicht in de productieprestaties",
                    "Deze cijfers tonen de effectiviteit van onze fabriek",
                    "Dit helpt ons de productiecapaciteit te begrijpen"
                ]
            },
            "sales": {
                "intro_phrases": [
                    "Uit onze verkoopgegevens", 
                    "De omzetcijfers laten zien",
                    "Op basis van facturatiedata"
                ],
                "context_explanations": [
                    "Dit geeft inzicht in onze commerciële prestaties",
                    "Deze trend toont de gezondheid van onze verkoop",
                    "Dit helpt ons marktpositie te begrijpen"
                ]
            },
            "inventory": {
                "intro_phrases": [
                    "Vanuit onze voorraadgegevens", 
                    "De inventarisdata toont",
                    "Kijkend naar onze magazijnstatus"
                ],
                "context_explanations": [
                    "Dit geeft inzicht in onze supply chain",
                    "Deze informatie helpt bij voorraadoptimalisatie",
                    "Dit toont de efficiëntie van onze logistiek"
                ]
            }
        }
        
        # Confidence level narratives
        self.confidence_narratives = {
            "high": {
                "prefix": "✅ **Betrouwbaar resultaat**",
                "explanation": "Deze gegevens zijn gevalideerd en consistent met verwachtingen."
            },
            "medium": {
                "prefix": "🟡 **Goede betrouwbaarheid**", 
                "explanation": "Deze gegevens zijn waarschijnlijk correct, maar overweeg aanvullende verificatie."
            },
            "low": {
                "prefix": "🟠 **Voorzichtigheid geboden**",
                "explanation": "Deze gegevens vereisen nadere verificatie vanwege mogelijke inconsistenties."
            },
            "unreliable": {
                "prefix": "🔴 **Onbetrouwbare gegevens**",
                "explanation": "Deze resultaten zijn waarschijnlijk incorrect door data-kwaliteitsproblemen."
            }
        }
    
    def generate_narrative_response(self, context: NarrativeContext) -> str:
        """Generate a comprehensive narrative response"""
        
        # Determine business domain
        domain = self._classify_business_domain(context.question, context.sql_query)
        
        # Get confidence level
        confidence_level = self._get_confidence_level(context.confidence_score)
        
        # Build narrative components
        narrative_parts = []
        
        # 1. Confidence and reliability intro
        narrative_parts.append(self._create_confidence_intro(confidence_level, context.confidence_score))
        
        # 2. Business context introduction
        narrative_parts.append(self._create_business_intro(domain, context))
        
        # 3. Main result presentation
        narrative_parts.append(self._create_result_presentation(context))
        
        # 4. Data context and meaning
        narrative_parts.append(self._create_data_context(context, domain))
        
        # 5. Business implications
        narrative_parts.append(self._create_business_implications(context, domain))
        
        # 6. Additional insights (if available)
        additional_insights = self._create_additional_insights(context)
        if additional_insights:
            narrative_parts.append(additional_insights)
        
        # 7. Next steps or related questions
        narrative_parts.append(self._create_next_steps(context, domain))
        
        return "\n\n".join(filter(None, narrative_parts))
    
    def _classify_business_domain(self, question: str, sql_query: str) -> str:
        """Classify the business domain based on question and query"""
        question_lower = question.lower()
        query_lower = sql_query.lower()
        
        # Production indicators
        if any(keyword in question_lower for keyword in ["machine", "productie", "geproduceerd", "gebouwd"]):
            return "production"
        
        # Sales indicators  
        if any(keyword in question_lower for keyword in ["omzet", "verkoop", "factuur", "klant", "revenue"]):
            return "sales"
        
        # Inventory indicators
        if any(keyword in question_lower for keyword in ["voorraad", "stock", "magazijn", "inventory"]):
            return "inventory"
        
        # Table-based classification
        if any(table in query_lower for table in ["u_serienummershoeflon", "u_hoeflonproductiestatus"]):
            return "production"
        elif any(table in query_lower for table in ["r_salesinvoice", "r_relation"]):
            return "sales"
        elif any(table in query_lower for table in ["r_stockinfo", "r_stockin", "r_stockout"]):
            return "inventory"
        
        return "general"
    
    def _get_confidence_level(self, confidence_score: float) -> str:
        """Convert confidence score to level"""
        if confidence_score >= 0.90:
            return "high"
        elif confidence_score >= 0.75:
            return "medium"
        elif confidence_score >= 0.60:
            return "low"
        else:
            return "unreliable"
    
    def _create_confidence_intro(self, confidence_level: str, confidence_score: float) -> str:
        """Create confidence-based introduction"""
        confidence_info = self.confidence_narratives.get(confidence_level, self.confidence_narratives["medium"])
        
        intro = f"{confidence_info['prefix']} ({confidence_score:.0%})\n"
        intro += confidence_info['explanation']
        
        if confidence_level in ["low", "unreliable"]:
            intro += "\n\n⚠️ **Let op**: Gebruik deze informatie met voorzichtigheid en overweeg aanvullende verificatie."
        
        return intro
    
    def _create_business_intro(self, domain: str, context: NarrativeContext) -> str:
        """Create business context introduction"""
        domain_info = self.domain_templates.get(domain, self.domain_templates["production"])
        
        # Choose intro phrase based on domain
        intro_phrase = domain_info["intro_phrases"][0]  # Could be randomized
        
        # Analyze time context
        time_context = self._extract_time_context(context.question, context.sql_query)
        
        business_intro = f"📊 **Uw vraag**: {context.question}\n\n"
        business_intro += f"{intro_phrase}"
        
        if time_context:
            business_intro += f" {time_context}"
        
        business_intro += ":"
        
        return business_intro
    
    def _extract_time_context(self, question: str, sql_query: str) -> str:
        """Extract and explain time context"""
        question_lower = question.lower()
        query_lower = sql_query.lower()
        
        if "dit jaar" in question_lower or "year(getdate())" in query_lower:
            return "voor het huidige jaar (2025)"
        elif "vorig jaar" in question_lower or "2024" in query_lower:
            return "voor vorig jaar (2024)"
        elif "deze maand" in question_lower or "month(getdate())" in query_lower:
            return "voor de huidige maand"
        elif "afgelopen maand" in question_lower:
            return "voor de afgelopen maand"
        
        return ""
    
    def _create_result_presentation(self, context: NarrativeContext) -> str:
        """Create engaging presentation of results"""
        results = context.results
        
        if not results:
            return "🔍 **Resultaat**: Geen gegevens gevonden die voldoen aan uw criteria."
        
        # Single numeric result
        if len(results) == 1 and len(results[0]) == 1:
            value = list(results[0].values())[0]
            
            if isinstance(value, (int, float)):
                # Format based on question type
                formatted_value = self._format_value_with_context(value, context.question)
                
                result_text = f"🎯 **Resultaat**: {formatted_value}"
                
                # Add context about the magnitude
                context_note = self._add_magnitude_context(value, context.question)
                if context_note:
                    result_text += f"\n\n💡 {context_note}"
                
                return result_text
            else:
                return f"🎯 **Resultaat**: {value}"
        
        # Multiple results
        elif len(results) > 1:
            result_text = f"🎯 **Resultaat**: {len(results)} records gevonden"
            
            # Show sample of results with explanation
            if len(results) <= 5:
                result_text += "\n\n**Overzicht:**"
                for i, result in enumerate(results, 1):
                    result_text += f"\n{i}. {self._format_result_row(result)}"
            else:
                result_text += "\n\n**Top resultaten:**"
                for i, result in enumerate(results[:3], 1):
                    result_text += f"\n{i}. {self._format_result_row(result)}"
                result_text += f"\n... en nog {len(results) - 3} records"
            
            return result_text
        
        return "🎯 **Resultaat**: Onverwacht resultaatformaat"
    
    def _format_value_with_context(self, value: float, question: str) -> str:
        """Format value based on question context"""
        question_lower = question.lower()
        
        # Money values
        if any(word in question_lower for word in ["omzet", "revenue", "bedrag", "winst", "profit", "kosten"]):
            return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        # Percentages
        elif any(word in question_lower for word in ["percentage", "procent", "%", "marge"]):
            return f"{value:.1f}%"
        
        # Counts/quantities
        elif any(word in question_lower for word in ["aantal", "hoeveel", "count", "machines", "klanten"]):
            if value >= 1000:
                return f"{int(value):,}".replace(",", ".")
            else:
                return str(int(value))
        
        # Default formatting
        else:
            if value >= 1000:
                return f"{value:,.0f}".replace(",", ".")
            else:
                return f"{value:.1f}" if value != int(value) else str(int(value))
    
    def _add_magnitude_context(self, value: float, question: str) -> Optional[str]:
        """Add context about the magnitude of the result"""
        question_lower = question.lower()
        
        # Machine/production context
        if any(word in question_lower for word in ["machines", "geproduceerd", "productie"]):
            if value > 200:
                return "Dit is een hoog productieniveau voor Hoeflon"
            elif value > 100:
                return "Dit ligt binnen normale productiecapaciteit"
            elif value > 50:
                return "Dit is een gemiddeld productieniveau"
            else:
                return "Dit is lager dan gebruikelijk"
        
        # Revenue context
        elif any(word in question_lower for word in ["omzet", "revenue"]):
            if value > 10000000:  # > 10M
                return "Dit vertegenwoordigt een sterke omzetprestatie"
            elif value > 1000000:  # > 1M
                return "Dit ligt binnen verwachte omzetcijfers"
            else:
                return "Dit omzetniveau vereist mogelijk aandacht"
        
        return None
    
    def _format_result_row(self, result: Dict[str, Any]) -> str:
        """Format a single result row for display"""
        formatted_items = []
        
        for key, value in result.items():
            if key.startswith('confidence') or key.startswith('accuracy'):
                continue  # Skip internal metadata
            
            if isinstance(value, (int, float)):
                if value >= 1000:
                    formatted_value = f"{value:,.0f}".replace(",", ".")
                else:
                    formatted_value = str(value)
            elif isinstance(value, (datetime, date)):
                formatted_value = value.strftime("%d-%m-%Y")
            else:
                formatted_value = str(value)
            
            formatted_items.append(f"{key}: {formatted_value}")
        
        return " | ".join(formatted_items[:3])  # Show first 3 fields
    
    def _create_data_context(self, context: NarrativeContext, domain: str) -> str:
        """Create explanation of data sources and methodology"""
        data_context = "📋 **Data Context**:\n"
        
        # Explain which tables were used
        tables_used = self._extract_tables_from_query(context.sql_query)
        if tables_used:
            data_context += f"• Data afkomstig uit: {', '.join(tables_used)}\n"
        
        # Explain filters applied
        filters = self._extract_filters_from_query(context.sql_query)
        if filters:
            data_context += f"• Filters toegepast: {filters}\n"
        
        # Explain data freshness
        if self.database_analyzer:
            freshness_info = self._get_data_freshness_info(tables_used)
            if freshness_info:
                data_context += f"• Data actualiteit: {freshness_info}\n"
        
        # Add domain-specific context
        domain_info = self.domain_templates.get(domain, {})
        context_explanations = domain_info.get("context_explanations", [])
        if context_explanations:
            data_context += f"• {context_explanations[0]}"
        
        return data_context
    
    def _extract_tables_from_query(self, sql_query: str) -> List[str]:
        """Extract table names from SQL query"""
        # Simple regex to find table names after FROM and JOIN
        tables = []
        
        # Find FROM clauses
        from_matches = re.findall(r'FROM\s+(\w+)', sql_query, re.IGNORECASE)
        tables.extend(from_matches)
        
        # Find JOIN clauses
        join_matches = re.findall(r'JOIN\s+(\w+)', sql_query, re.IGNORECASE)
        tables.extend(join_matches)
        
        # Clean up table names (remove aliases)
        clean_tables = []
        for table in tables:
            clean_table = table.split()[0]  # Remove alias
            if clean_table.upper() not in ['SELECT', 'WHERE', 'AND', 'OR']:
                clean_tables.append(clean_table)
        
        return list(set(clean_tables))  # Remove duplicates
    
    def _extract_filters_from_query(self, sql_query: str) -> str:
        """Extract and explain filters from SQL query"""
        filters = []
        
        # Date filters
        if "YEAR(GETDATE())" in sql_query:
            filters.append("huidig jaar")
        elif "YEAR(" in sql_query:
            filters.append("specifiek jaar")
        
        # State filters
        if "STATE = 2" in sql_query:
            filters.append("gereed/verkocht status")
        elif "STATE = 1" in sql_query:
            filters.append("in productie status")
        
        # External sales filter
        if "FK_INVOICERELATION NOT IN" in sql_query:
            filters.append("alleen externe verkoop")
        
        # Product filters
        if "LIKE '%C6%'" in sql_query:
            filters.append("C6 machines")
        elif "LIKE '%C30%'" in sql_query:
            filters.append("C30 machines")
        
        return ", ".join(filters) if filters else "geen specifieke filters"
    
    def _get_data_freshness_info(self, tables: List[str]) -> Optional[str]:
        """Get data freshness information"""
        if not self.database_analyzer or not tables:
            return None
        
        try:
            # Get freshness info from first table
            table_name = tables[0]
            insight = self.database_analyzer.get_table_insight(table_name)
            
            if insight and hasattr(insight, 'business_meaning'):
                if 'Latest data:' in insight.business_meaning:
                    freshness_line = [line for line in insight.business_meaning.split('\n') if 'Latest data:' in line][0]
                    return freshness_line.replace('Latest data: ', '')
            
        except Exception as e:
            self.logger.debug(f"Could not get freshness info: {e}")
        
        return None
    
    def _create_business_implications(self, context: NarrativeContext, domain: str) -> str:
        """Create business implications and insights"""
        implications = "💼 **Business Implicaties**:\n"
        
        if not context.results:
            implications += "• Geen data gevonden kan duiden op een probleem met de zoekcriteria of data-beschikbaarheid"
            return implications
        
        # Single numeric result implications
        if len(context.results) == 1 and len(context.results[0]) == 1:
            value = list(context.results[0].values())[0]
            
            if isinstance(value, (int, float)):
                # Domain-specific implications
                if domain == "production":
                    implications += self._get_production_implications(value, context.question)
                elif domain == "sales":
                    implications += self._get_sales_implications(value, context.question)
                else:
                    implications += f"• Dit cijfer geeft inzicht in de {domain} prestaties van Hoeflon"
        else:
            implications += f"• De {len(context.results)} gevonden records bieden detailinzicht voor verdere analyse"
        
        return implications
    
    def _get_production_implications(self, value: float, question: str) -> str:
        """Get production-specific business implications"""
        question_lower = question.lower()
        
        if "machines" in question_lower and "geproduceerd" in question_lower:
            if value > 150:
                return "• Sterke productieprestatie die wijst op efficiënte fabriekprocessen\n• Mogelijk kansen voor uitbreiding of optimalisatie van capaciteit"
            elif value > 50:
                return "• Normale productievolumes binnen verwachte bandbreedte\n• Monitoring van trends kan inzicht geven in seizoenspatronen"
            else:
                return "• Lage productie kan wijzen op uitdagingen of geplande onderhoudsstops\n• Analyse van oorzaken en planning herstelacties wordt aanbevolen"
        
        return "• Deze productiedata helpt bij capaciteitsplanning en efficiëntie-optimalisatie"
    
    def _get_sales_implications(self, value: float, question: str) -> str:
        """Get sales-specific business implications"""
        question_lower = question.lower()
        
        if "omzet" in question_lower:
            if value > 5000000:  # > 5M
                return "• Uitstekende omzetprestatie die groei en marktpositie bevestigt\n• Mogelijkheden voor verdere expansie en investeringen"
            elif value > 1000000:  # > 1M
                return "• Solide omzetcijfers binnen verwachte commerciële doelstellingen\n• Focus op klanttevredenheid en retention wordt aanbevolen"
            else:
                return "• Omzet onder verwachting vereist analyse van marktfactoren\n• Evaluatie van verkoop- en marketingstrategieën wordt aanbevolen"
        
        return "• Deze verkoopdata ondersteunt strategische besluitvorming en forecasting"
    
    def _create_additional_insights(self, context: NarrativeContext) -> Optional[str]:
        """Create additional insights if available"""
        insights = []
        
        # Query complexity insight
        if "JOIN" in context.sql_query.upper():
            insights.append("• Deze analyse combineert gegevens uit meerdere databronnen voor een compleet beeld")
        
        # Time-based insight
        if any(word in context.question.lower() for word in ["dit jaar", "vorig jaar", "maand"]):
            insights.append("• Tijdgebonden analyse helpt bij het identificeren van trends en seizoenspatronen")
        
        # Confidence-based insight
        if context.confidence_score < 0.8:
            insights.append("• Aanvullende datavalidatie kan de betrouwbaarheid van deze analyse verbeteren")
        
        if insights:
            return "🔍 **Aanvullende Inzichten**:\n" + "\n".join(insights)
        
        return None
    
    def _create_next_steps(self, context: NarrativeContext, domain: str) -> str:
        """Create suggestions for next steps or related questions"""
        next_steps = "🚀 **Vervolgvragen die u zou kunnen stellen**:\n"
        
        question_lower = context.question.lower()
        
        if domain == "production":
            if "machines" in question_lower:
                next_steps += "• \"Vergelijk productie dit jaar met vorig jaar\"\n"
                next_steps += "• \"Wat is de gemiddelde productietijd per machine?\"\n"
                next_steps += "• \"Toon productie per maand voor dit jaar\""
            else:
                next_steps += "• \"Hoeveel machines zijn er dit jaar geproduceerd?\"\n"
                next_steps += "• \"Wat is de productiestatus van alle machines?\""
        
        elif domain == "sales":
            if "omzet" in question_lower:
                next_steps += "• \"Toon omzet per klant voor dit jaar\"\n"
                next_steps += "• \"Vergelijk omzet per maand\"\n"
                next_steps += "• \"Wat is de gemiddelde factuurwaarde?\""
            else:
                next_steps += "• \"Wat is de omzet dit jaar?\"\n"
                next_steps += "• \"Hoeveel facturen zijn er uitgestuurd?\""
        
        else:
            next_steps += "• \"Meer details\" - voor uitgebreidere informatie\n"
            next_steps += "• \"Per maand\" - voor maandelijkse uitsplitsing\n"
            next_steps += "• \"Vergelijking\" - voor periode-vergelijkingen"
        
        # Add drill-down hint
        next_steps += "\n\n💡 **Tip**: Typ \"meer details\" of \"breakdown\" voor diepere analyse van deze resultaten."
        
        return next_steps
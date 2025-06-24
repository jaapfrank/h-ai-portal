#!/usr/bin/env python3
"""
AI Clarification Engine for Hoeflon AI
Detects ambiguous questions and generates intelligent clarifying questions
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

class ClarificationEngine:
    """Engine for detecting ambiguous queries and generating clarifying questions"""
    
    def __init__(self):
        # Ambiguity patterns that require clarification
        self.ambiguity_patterns = {
            "time_period_missing": {
                "keywords": ["omzet", "verkoop", "productie", "machines", "facturen"],
                "missing_indicators": ["dit jaar", "vorig jaar", "maand", "week", "periode", "2024", "2025"],
                "question_template": "Voor welke periode wilt u dit weten? (bijvoorbeeld: dit jaar, vorig jaar, deze maand, of een specifiek jaar zoals 2024)"
            },
            
            "product_specification": {
                "keywords": ["product", "machine", "artikel", "item"],
                "missing_indicators": ["C6", "C3", "specifiek", "type", "model"],
                "question_template": "Welke specifieke producten of machines bedoelt u? (bijvoorbeeld: alle machines, alleen C6 machines, of een specifiek producttype)"
            },
            
            "customer_scope": {
                "keywords": ["klant", "customer", "relatie"],
                "missing_indicators": ["top", "beste", "grootste", "specifiek", "naam"],
                "question_template": "Welke klanten bedoelt u? (bijvoorbeeld: alle klanten, top 10 klanten, of een specifieke klant)"
            },
            
            "financial_metric": {
                "keywords": ["omzet", "winst", "kosten", "financieel"],
                "missing_indicators": ["bruto", "netto", "exclusief", "inclusief", "btw"],
                "question_template": "Welke financiële maatstaf bedoelt u precies? (bijvoorbeeld: bruto omzet, netto winst, inclusief of exclusief BTW)"
            },
            
            "comparison_baseline": {
                "keywords": ["vergelijk", "tegenover", "versus", "vs"],
                "missing_indicators": ["met", "tegen", "vorig", "jaar", "maand"],
                "question_template": "Waarmee wilt u dit vergelijken? (bijvoorbeeld: vorig jaar, vorige maand, of een andere periode/waarde)"
            },
            
            "database_source": {
                "keywords": ["gegevens", "data", "informatie"],
                "missing_indicators": ["erp", "accountview", "financieel", "operationeel"],
                "question_template": "Uit welke bron wilt u de gegevens? (ERP voor operationele data, AccountView voor financiële data, of beide)"
            }
        }
        
        # Confidence thresholds
        self.confidence_thresholds = {
            "high": 0.9,      # Execute query directly
            "medium": 0.75,   # Ask for clarification
            "low": 0.5        # Ask detailed clarifying questions
        }
        
        # Context-specific clarifications
        self.context_clarifications = {
            "hoeflon_specific": {
                "machines": ["C6 machines", "C3 machines", "alle machines", "machines in productie"],
                "companies": ["Hoeflon B.V.", "Hoeflon International", "beide bedrijven", "gecombineerd"],
                "periods": ["dit jaar (2025)", "vorig jaar (2024)", "deze maand", "dit kwartaal"],
                "financial_types": ["operationele omzet (ERP)", "financiële data (AccountView)", "gecombineerde analyse"]
            }
        }
        
        # Business logic rules for data source selection
        self.business_rules = {
            "omzet_source_priority": {
                "description": "Voor omzetvragen: Hoeflon International heeft de echte externe verkoop",
                "primary_source": "hoeflon_international",
                "secondary_source": "hoeflon_bv", 
                "fallback_source": "erp",
                "reasoning": "Hoeflon International verkoopt extern, Hoeflon B.V. is meer intern"
            },
            "production_source": {
                "description": "Voor productievragen: ERP heeft operationele data",
                "primary_source": "erp",
                "reasoning": "Machine productie en serienummers zitten in ERP"
            }
        }
    
    def analyze_question_clarity(self, question: str) -> Dict[str, Any]:
        """Analyze if a question needs clarification"""
        question_lower = question.lower()
        
        analysis = {
            "needs_clarification": False,
            "confidence_score": 1.0,
            "ambiguity_type": None,
            "missing_elements": [],
            "suggested_clarifications": [],
            "question_complexity": "simple"
        }
        
        # Check for ambiguity patterns
        ambiguities_found = []
        
        for ambiguity_type, pattern in self.ambiguity_patterns.items():
            # Check if keywords are present
            has_keywords = any(keyword in question_lower for keyword in pattern["keywords"])
            
            if has_keywords:
                # Check if clarifying indicators are missing
                missing_indicators = not any(indicator in question_lower for indicator in pattern["missing_indicators"])
                
                if missing_indicators:
                    ambiguities_found.append({
                        "type": ambiguity_type,
                        "template": pattern["question_template"],
                        "severity": self._calculate_ambiguity_severity(question_lower, pattern)
                    })
        
        # Calculate overall confidence
        if ambiguities_found:
            # Reduce confidence based on number and severity of ambiguities
            severity_sum = sum(amb["severity"] for amb in ambiguities_found)
            confidence_reduction = min(severity_sum * 0.4, 0.8)  # Max 80% reduction, more aggressive
            analysis["confidence_score"] = max(1.0 - confidence_reduction, 0.1)
            
            # Sort by severity (highest first)
            ambiguities_found.sort(key=lambda x: x["severity"], reverse=True)
            
            analysis["needs_clarification"] = analysis["confidence_score"] < self.confidence_thresholds["medium"]
            analysis["ambiguity_type"] = ambiguities_found[0]["type"]
            analysis["missing_elements"] = [amb["type"] for amb in ambiguities_found]
            analysis["suggested_clarifications"] = [amb["template"] for amb in ambiguities_found[:2]]  # Top 2
        
        # Determine complexity
        if len(ambiguities_found) > 2:
            analysis["question_complexity"] = "complex"
        elif len(ambiguities_found) > 0:
            analysis["question_complexity"] = "medium"
        
        return analysis
    
    def _calculate_ambiguity_severity(self, question: str, pattern: Dict[str, Any]) -> float:
        """Calculate severity of ambiguity (0.0 = not ambiguous, 1.0 = very ambiguous)"""
        severity = 0.0
        
        # Count matching keywords
        keyword_matches = sum(1 for keyword in pattern["keywords"] if keyword in question)
        if keyword_matches > 0:
            severity += 0.3  # Base severity for keyword match
            
        # Check for vague terms
        vague_terms = ["dit", "dat", "deze", "die", "sommige", "veel", "weinig", "beter", "slechter"]
        vague_count = sum(1 for term in vague_terms if term in question)
        severity += min(vague_count * 0.15, 0.4)
        
        # Check for question length (very short questions are often ambiguous)
        word_count = len(question.split())
        if word_count < 4:
            severity += 0.3
        elif word_count < 6:
            severity += 0.15
        
        return min(severity, 1.0)
    
    def generate_clarifying_question(self, question: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a clarifying question based on analysis"""
        
        if not analysis["needs_clarification"]:
            return {
                "has_clarification": False,
                "original_question": question,
                "confidence": analysis["confidence_score"]
            }
        
        # Primary clarifying question
        primary_clarification = analysis["suggested_clarifications"][0] if analysis["suggested_clarifications"] else None
        
        # Generate context-specific options
        options = self._generate_context_options(question, analysis["ambiguity_type"])
        
        # Create clarifying response
        clarification_response = {
            "has_clarification": True,
            "original_question": question,
            "confidence": analysis["confidence_score"],
            "ambiguity_type": analysis["ambiguity_type"],
            "clarifying_question": primary_clarification,
            "suggested_options": options,
            "follow_up_questions": analysis["suggested_clarifications"][1:] if len(analysis["suggested_clarifications"]) > 1 else []
        }
        
        return clarification_response
    
    def _generate_context_options(self, question: str, ambiguity_type: str) -> List[str]:
        """Generate context-specific options for clarification"""
        question_lower = question.lower()
        options = []
        
        # Time period options
        if ambiguity_type == "time_period_missing":
            options = [
                "Dit jaar (2025)",
                "Vorig jaar (2024)", 
                "Deze maand",
                "Dit kwartaal",
                "Laatste 12 maanden"
            ]
        
        # Product/machine options
        elif ambiguity_type == "product_specification":
            if "machine" in question_lower:
                options = [
                    "Alle machines",
                    "Alleen C6 machines",
                    "Alleen C3 machines", 
                    "Machines in productie",
                    "Gereed gemelde machines"
                ]
            else:
                options = [
                    "Alle producten",
                    "Top 10 producten",
                    "Specifiek product (geef naam)",
                    "Productgroep"
                ]
        
        # Customer options
        elif ambiguity_type == "customer_scope":
            options = [
                "Alle klanten",
                "Top 10 klanten",
                "Externe klanten (excl. Hoeflon intern)",
                "Specifieke klant (geef naam)"
            ]
        
        # Financial metric options
        elif ambiguity_type == "financial_metric":
            options = [
                "Bruto omzet",
                "Netto omzet", 
                "Inclusief BTW",
                "Exclusief BTW",
                "Alleen externe omzet"
            ]
        
        # Comparison options
        elif ambiguity_type == "comparison_baseline":
            options = [
                "Vergelijk met vorig jaar",
                "Vergelijk met vorige maand",
                "Vergelijk met budget",
                "Vergelijk met benchmark"
            ]
        
        # Database source options
        elif ambiguity_type == "database_source":
            options = [
                "ERP data (operationeel)",
                "AccountView data (financieel)",
                "Gecombineerde analyse",
                "Hoeflon B.V. alleen",
                "Hoeflon International alleen"
            ]
        
        return options
    
    def format_clarification_response(self, clarification: Dict[str, Any]) -> str:
        """Format clarification as user-friendly response"""
        
        if not clarification["has_clarification"]:
            return ""
        
        response = f"🤔 **Ik heb een verduidelijking nodig voor een nauwkeurig antwoord:**\n\n"
        response += f"**Vraag:** {clarification['clarifying_question']}\n\n"
        
        if clarification["suggested_options"]:
            response += "**Opties:**\n"
            for i, option in enumerate(clarification["suggested_options"], 1):
                response += f"{i}. {option}\n"
            response += "\n"
        
        if clarification["follow_up_questions"]:
            response += "**Aanvullende vragen:**\n"
            for question in clarification["follow_up_questions"]:
                response += f"• {question}\n"
            response += "\n"
        
        response += "💡 *Kunt u uw vraag specifieker maken? Dit zorgt voor een veel nauwkeuriger antwoord.*"
        
        return response
    
    def process_clarification_response(self, original_question: str, clarification_answer: str) -> str:
        """Process user's response to clarification and create refined question"""
        
        # Combine original question with clarification
        refined_question = f"{original_question}"
        
        # Add clarification context
        clarification_lower = clarification_answer.lower()
        
        # Parse common clarification patterns
        if any(word in clarification_lower for word in ["dit jaar", "2025"]):
            refined_question += " voor dit jaar (2025)"
        elif any(word in clarification_lower for word in ["vorig jaar", "2024"]):
            refined_question += " voor vorig jaar (2024)"
        elif "maand" in clarification_lower:
            refined_question += " voor deze maand"
        
        if "c6" in clarification_lower:
            refined_question += ", alleen C6 machines"
        elif "c3" in clarification_lower:
            refined_question += ", alleen C3 machines"
        
        if any(word in clarification_lower for word in ["top", "beste"]):
            refined_question += ", top 10"
        
        if "extern" in clarification_lower or "exclusief" in clarification_lower:
            refined_question += ", exclusief interne verkoop"
        
        if "bruto" in clarification_lower:
            refined_question += ", bruto bedragen"
        elif "netto" in clarification_lower:
            refined_question += ", netto bedragen"
        
        return refined_question
    
    def should_ask_clarification(self, question: str, confidence_threshold: float = 0.6) -> bool:
        """Quick check if question needs clarification"""
        analysis = self.analyze_question_clarity(question)
        return analysis["needs_clarification"] and analysis["confidence_score"] < confidence_threshold
    
    def generate_error_clarification(self, error_type: str, error_message: str, user_question: str) -> Dict[str, Any]:
        """Generate clarifying questions for specific error types instead of showing technical errors"""
        
        error_clarifications = {
            "database_connection": {
                "user_message": "🔌 **Ik heb problemen met de database verbinding**",
                "clarifying_question": "Welke gegevens wilt u precies ophalen? Ik kan u helpen door de juiste database te selecteren.",
                "options": [
                    "ERP gegevens (machines, producten, facturen)",
                    "Financiële gegevens (AccountView)",
                    "Operationele gegevens (productie, voorraad)",
                    "Klantgegevens",
                    "Rapportage data"
                ],
                "suggestion": "Laat me weten wat voor informatie u zoekt, dan kan ik de juiste database verbinding opzetten."
            },
            
            "sql_execution": {
                "user_message": "🔍 **Ik heb moeite met het ophalen van de juiste gegevens**",
                "clarifying_question": "Kunt u uw vraag specifieker maken? Dit helpt mij om de juiste gegevens te vinden.",
                "options": [
                    "Geef een tijdsperiode aan (dit jaar, vorig jaar, deze maand)",
                    "Specificeer welke producten/machines (C6, C3, alle machines)",
                    "Geef aan welke klanten (alle, top 10, externe klanten)",
                    "Verduidelijk welke financiële gegevens (omzet, winst, kosten)",
                    "Geef aan welke database (ERP, AccountView, beide)"
                ],
                "suggestion": "Hoe specifieker uw vraag, hoe nauwkeuriger mijn antwoord kan zijn."
            },
            
            "ai_generation": {
                "user_message": "🤖 **Ik heb hulp nodig om uw vraag te begrijpen**",
                "clarifying_question": "Kunt u uw vraag op een andere manier stellen? Ik wil er zeker van zijn dat ik u het juiste antwoord geef.",
                "options": [
                    "Gebruik eenvoudigere bewoordingen",
                    "Geef een voorbeeld van wat u verwacht",
                    "Splits complexe vragen op in kleinere delen",
                    "Vermeld specifieke namen, datums of bedragen",
                    "Geef context over waarom u deze informatie nodig heeft"
                ],
                "suggestion": "Stel uw vraag alsof u tegen een collega praat die uw bedrijf goed kent."
            },
            
            "schema_loading": {
                "user_message": "📊 **Ik heb beperkte toegang tot database informatie**",
                "clarifying_question": "Welke type gegevens zoekt u? Ik kan u helpen binnen de beschikbare data.",
                "options": [
                    "Machine productie gegevens",
                    "Verkoop en factuur gegevens",
                    "Klant informatie",
                    "Product gegevens",
                    "Financiële overzichten"
                ],
                "suggestion": "Ik werk met de beschikbare data en kan u helpen de juiste informatie te vinden."
            },
            
            "chart_creation": {
                "user_message": "📈 **Ik kan een grafiek maken als u aangeeft wat u wilt zien**",
                "clarifying_question": "Welke soort visualisatie zou u het meest helpen?",
                "options": [
                    "Tabel met de ruwe gegevens",
                    "Eenvoudige staafgrafiek",
                    "Lijn grafiek voor trends over tijd",
                    "Vergelijking tussen verschillende periodes",
                    "Alleen de belangrijkste cijfers"
                ],
                "suggestion": "Ik kan de gegevens op verschillende manieren presenteren."
            },
            
            "data_not_found": {
                "user_message": "🔍 **Ik kan geen gegevens vinden die precies overeenkomen met uw vraag**",
                "clarifying_question": "Zou u uw vraag kunnen aanpassen of verduidelijken?",
                "options": [
                    "Probeer een bredere zoekopdracht",
                    "Controleer de spelling van namen/producten",
                    "Gebruik andere tijdsperiodes",
                    "Zoek in andere databases",
                    "Vraag naar verwante informatie"
                ],
                "suggestion": "Soms kan ik wel vergelijkbare gegevens vinden die nuttig zijn."
            },
            
            "access_denied": {
                "user_message": "🔒 **Ik heb beperkte toegang tot sommige gegevens**",
                "clarifying_question": "Welke openbare gegevens kan ik voor u ophalen?",
                "options": [
                    "Algemene statistieken",
                    "Niet-vertrouwelijke bedrijfsinformatie",
                    "Publieke gegevens",
                    "Historische trends",
                    "Samengevatte cijfers"
                ],
                "suggestion": "Ik kan u helpen met toegankelijke informatie."
            }
        }
        
        # Get clarification template for this error type
        template = error_clarifications.get(error_type, {
            "user_message": "❓ **Ik heb hulp nodig om uw vraag te beantwoorden**",
            "clarifying_question": "Kunt u uw vraag verduidelijken?",
            "options": [
                "Geef meer context",
                "Gebruik andere bewoordingen",
                "Splits de vraag op in kleinere delen"
            ],
            "suggestion": "Hoe specifieker uw vraag, hoe beter ik kan helpen."
        })
        
        # Create clarification response
        clarification = {
            "has_clarification": True,
            "original_question": user_question,
            "error_type": error_type,
            "error_message": error_message,
            "user_message": template["user_message"],
            "clarifying_question": template["clarifying_question"],
            "suggested_options": template["options"],
            "suggestion": template["suggestion"],
            "confidence": 0.2  # Low confidence due to error
        }
        
        return clarification
    
    def format_error_clarification_response(self, clarification: Dict[str, Any]) -> str:
        """Format error-based clarification as user-friendly response"""
        
        if not clarification["has_clarification"]:
            return ""
        
        response = f"{clarification['user_message']}\n\n"
        response += f"**{clarification['clarifying_question']}**\n\n"
        
        if clarification["suggested_options"]:
            response += "**Ik kan u helpen met:**\n"
            for i, option in enumerate(clarification["suggested_options"], 1):
                response += f"{i}. {option}\n"
            response += "\n"
        
        response += f"💡 *{clarification['suggestion']}*"
        
        return response
    
    def classify_error_for_clarification(self, error_message: str, context: Dict[str, Any] = None) -> str:
        """Classify error type to determine appropriate clarification"""
        
        error_lower = error_message.lower()
        context = context or {}
        
        # AI generation errors (check first for specific API errors)
        if any(keyword in error_lower for keyword in [
            "claude api", "api error", "anthropic", "500 -", "internal server"
        ]):
            return "ai_generation"
        
        # Data not found (check early to avoid conflicts)
        elif any(keyword in error_lower for keyword in [
            "no data found", "geen resultaten", "no results", "geen gegevens"
        ]):
            return "data_not_found"
        
        # Database connection errors
        elif any(keyword in error_lower for keyword in [
            "connection", "verbinding", "timeout", "server", "database", 
            "pyodbc", "odbc", "sql server", "login", "authentication"
        ]):
            return "database_connection"
        
        # Schema loading errors
        elif any(keyword in error_lower for keyword in [
            "schema", "table_analyses", "json", "file not found",
            "schema_full", "loading", "parse"
        ]):
            return "schema_loading"
        
        # Chart creation errors
        elif any(keyword in error_lower for keyword in [
            "chart", "matplotlib", "plot", "visualization", "graph",
            "image", "base64", "figure"
        ]):
            return "chart_creation"
        
        # SQL execution errors (check after more specific errors)
        elif any(keyword in error_lower for keyword in [
            "invalid column", "table", "syntax", "invalid object", 
            "column name", "query", "select", "from", "where"
        ]):
            return "sql_execution"
        
        # Access denied
        elif any(keyword in error_lower for keyword in [
            "access", "permission", "denied", "forbidden", "unauthorized",
            "toegang", "rechten"
        ]):
            return "access_denied"
        
        # Default to generic error
        else:
            return "generic"
    
    def should_use_clarification_for_error(self, error_type: str, user_question: str) -> bool:
        """Determine if an error should trigger clarification instead of technical error message"""
        
        # Always use clarification for these user-facing errors
        clarification_errors = [
            "database_connection", "sql_execution", "ai_generation",
            "data_not_found", "schema_loading", "chart_creation"
        ]
        
        if error_type in clarification_errors:
            return True
        
        # Check if the question seems like a business question (not technical)
        business_keywords = [
            "omzet", "machines", "klanten", "productie", "verkoop",
            "facturen", "winst", "revenue", "orders", "hoeveel",
            "wat is", "toon", "laat zien"
        ]
        
        # Technical indicators that suggest this is NOT a business question
        technical_keywords = [
            "select *", "from sys.", "database schema", "check database",
            "debug", "error log", "sys.tables"
        ]
        
        question_lower = user_question.lower()
        is_business_question = any(keyword in question_lower for keyword in business_keywords)
        is_technical_question = any(keyword in question_lower for keyword in technical_keywords)
        
        # If it's clearly technical, don't use clarification
        if is_technical_question:
            return False
            
        return is_business_question
    
    def generate_interactive_clarification(self, question: str) -> Dict[str, Any]:
        """Generate interactive clarification form with checkboxes and dropdowns"""
        
        # Detect question type to provide specific options
        is_revenue_question = any(word in question.lower() for word in ['omzet', 'revenue', 'verkocht'])
        is_production_question = any(word in question.lower() for word in ['productie', 'geproduceerd', 'gebouwd', 'machines', 'kranen'])
        
        clarification_options = {
            "question_analysis": {
                "original_question": question,
                "detected_type": "revenue" if is_revenue_question else "production" if is_production_question else "general"
            },
            "interactive_form": {
                "tijd_periode": {
                    "label": "Welke tijdsperiode?",
                    "type": "radio",
                    "options": [
                        {"value": "dit_jaar", "label": "Dit jaar (2025)", "default": True},
                        {"value": "vorig_jaar", "label": "Vorig jaar (2024)"},
                        {"value": "deze_maand", "label": "Deze maand"},
                        {"value": "afgelopen_maand", "label": "Afgelopen maand"},
                        {"value": "vergelijking", "label": "Vergelijking dit jaar vs vorig jaar"}
                    ]
                },
                "product_type": {
                    "label": "Welke producten?",
                    "type": "checkbox",
                    "options": [
                        {"value": "alle_kranen", "label": "Alle kranen", "default": True},
                        {"value": "c6_kranen", "label": "Alleen C6 kranen"},
                        {"value": "c30_kranen", "label": "Alleen C30 kranen"},
                        {"value": "alle_machines", "label": "Alle machines (inclusief non-kranen)"}
                    ]
                },
                "data_scope": {
                    "label": "Welke data?",
                    "type": "radio",
                    "options": [
                        {"value": "externe_alleen", "label": "Alleen externe klanten (geen interne Hoeflon verkopen)", "default": True},
                        {"value": "alle_data", "label": "Alle data inclusief interne verkopen"}
                    ]
                }
            }
        }
        
        # Add specific options based on question type
        if is_production_question:
            clarification_options["interactive_form"]["definitie"] = {
                "label": "Wat bedoel je met 'geproduceerd'?",
                "type": "radio",
                "options": [
                    {"value": "gereed_gemeld", "label": "Gereed gemeld (productie voltooid)", "default": True},
                    {"value": "gefactureerd", "label": "Gefactureerd aan klant"},
                    {"value": "geleverd", "label": "Daadwerkelijk geleverd bij klant"}
                ]
            }
        
        if is_revenue_question:
            clarification_options["interactive_form"]["revenue_type"] = {
                "label": "Welke omzet informatie?",
                "type": "radio", 
                "options": [
                    {"value": "totale_omzet", "label": "Totale omzet in euro", "default": True},
                    {"value": "gemiddelde_per_product", "label": "Gemiddelde omzet per product"},
                    {"value": "aantal_verkopen", "label": "Aantal verkopen/facturen"}
                ]
            }
        
        # Add visualization options for comparison questions
        if any(word in question.lower() for word in ['vergelijk', 'vs', 'tegenover', 'grafiek', 'chart']):
            clarification_options["interactive_form"]["visualisatie"] = {
                "label": "Gewenste output?",
                "type": "checkbox",
                "options": [
                    {"value": "tabel", "label": "Tabel met cijfers", "default": True},
                    {"value": "grafiek", "label": "Grafiek/chart", "default": True},
                    {"value": "dashboard", "label": "Volledig dashboard in nieuw tabblad"}
                ]
            }
        
        return clarification_options
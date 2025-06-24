#!/usr/bin/env python3
"""
Intelligent Query Preprocessor - Smart Intent Detection & Clarification
Solves the user's feedback: "niet echt een slim systeem aan het bouwen dat zichzelf aanpast"
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class QueryIntent(Enum):
    DATABASE_QUERY = "database_query"
    COMPANY_INFO = "company_info"
    HR_POLICY = "hr_policy"
    CONTACT_INFO = "contact_info"
    CLARIFICATION_NEEDED = "clarification_needed"
    GREETING = "greeting"
    UNKNOWN = "unknown"

@dataclass
class ClarificationOption:
    id: str
    text: str
    intent: QueryIntent
    additional_context: Dict = None

@dataclass
class QueryAnalysis:
    original_query: str
    detected_intent: QueryIntent
    confidence: float
    needs_clarification: bool
    clarification_options: List[ClarificationOption] = None
    enhanced_query: str = None
    metadata: Dict = None

class IntelligentQueryPreprocessor:
    """
    Smart query preprocessor that understands user intent and generates
    interactive clarification when needed - addressing user feedback about
    non-technical users needing guidance.
    """
    
    def __init__(self):
        # Intent detection patterns with multiple language variations
        self.intent_patterns = {
            QueryIntent.DATABASE_QUERY: [
                # Quantity questions
                r"\b(hoeveel|aantal|tel|count)\b.*\b(machines?|kranen?|facturen?|klanten?)\b",
                r"\b(top\s*\d*|beste|grootste|meeste)\b.*\b(klanten?|producten?|verkoop)\b",
                r"\b(omzet|revenue|verkoop|inkomsten?)\b",
                r"\b(dit jaar|vorig jaar|deze maand|dit kwartaal)\b",
                r"\b(vergelijk|verschil|groei)\b.*\b(jaar|maand|periode)\b",
                r"\b(totaal|som|gemiddeld)\b",
                r"\b(rapport|overzicht|statistiek|dashboard)\b",
            ],
            
            QueryIntent.COMPANY_INFO: [
                r"\b(wie is|wat is)\b.*\b(directeur|baas|ceo|manager)\b",
                r"\b(organisatie|organigram|structuur|hiërarchie)\b",
                r"\b(afdelingen?|teams?|medewerkers?)\b",
                r"\b(bedrijf|hoeflon|organisatie)\b.*\b(informatie|gegevens)\b",
            ],
            
            QueryIntent.HR_POLICY: [
                r"\b(verlof|vakantie|ziek|zwanger)\b",
                r"\b(ouderschapsverlof|geboorteverlof|zwangerschapsverlof)\b",
                r"\b(beleid|procedure|regels|voorwaarden)\b",
                r"\b(HR|personeelszaken|human resources)\b",
                r"\b(aanvragen?|aanmelding|formulier)\b.*\b(verlof|vakantie)\b",
            ],
            
            QueryIntent.CONTACT_INFO: [
                r"\b(telefoon|nummer|bereikbaar|contact)\b",
                r"\b(email|mail|adres)\b",
                r"\b(waar vind ik|hoe bereik ik)\b",
                r"\b(service|onderhoud|support|hulp)\b.*\b(contact|telefoon)\b",
            ],
            
            QueryIntent.GREETING: [
                r"\b(hallo|hoi|dag|goedemorgen|goedemiddag|goedenavond)\b",
                r"\b(dank je|bedankt|thanks)\b",
                r"\b(help|hulp|wat kun je|wat doe je)\b",
                r"\b(hoe gaat het|alles goed)\b",
            ]
        }
        
        # Ambiguity patterns that require clarification
        self.ambiguity_patterns = [
            {
                "pattern": r"\b(klanten?)\b(?!.*\b(top|beste|omzet|aantal|hoeveel)\b)",
                "clarifications": [
                    ClarificationOption("customer_revenue", "🏆 Top klanten op omzet", QueryIntent.DATABASE_QUERY),
                    ClarificationOption("customer_count", "📊 Aantal klanten totaal", QueryIntent.DATABASE_QUERY),
                    ClarificationOption("customer_info", "📋 Klant contactgegevens", QueryIntent.CONTACT_INFO),
                    ClarificationOption("customer_new", "🆕 Nieuwe klanten dit jaar", QueryIntent.DATABASE_QUERY),
                ]
            },
            {
                "pattern": r"\b(machines?|kranen?)\b(?!.*\b(hoeveel|aantal|verkocht|geproduceerd)\b)",
                "clarifications": [
                    ClarificationOption("machine_production", "🏭 Aantal geproduceerde machines", QueryIntent.DATABASE_QUERY),
                    ClarificationOption("machine_sales", "💰 Verkochte machines & omzet", QueryIntent.DATABASE_QUERY),
                    ClarificationOption("machine_types", "🔧 Verschillende machine types", QueryIntent.DATABASE_QUERY),
                    ClarificationOption("machine_service", "⚙️ Service & onderhoud contact", QueryIntent.CONTACT_INFO),
                ]
            },
            {
                "pattern": r"\b(verkoop|omzet)\b(?!.*\b(dit jaar|vorig jaar|maand)\b)",
                "clarifications": [
                    ClarificationOption("sales_year", "📈 Omzet dit jaar", QueryIntent.DATABASE_QUERY),
                    ClarificationOption("sales_month", "📊 Omzet deze maand", QueryIntent.DATABASE_QUERY),
                    ClarificationOption("sales_comparison", "⚖️ Vergelijking met vorig jaar", QueryIntent.DATABASE_QUERY),
                    ClarificationOption("sales_breakdown", "🔍 Omzet per product/klant", QueryIntent.DATABASE_QUERY),
                ]
            }
        ]
        
        # Non-technical user friendly suggestions
        self.user_friendly_suggestions = {
            "vague_query": [
                "💡 **Probeer bijvoorbeeld**: 'Hoeveel machines hebben we dit jaar verkocht?'",
                "📊 **Of vraag naar**: 'Wie is de directeur van Hoeflon?'",
                "📞 **Contact vragen**: 'Wie kan ik bellen voor service?'",
                "💼 **HR vragen**: 'Hoe vraag ik verlof aan?'"
            ],
            "database_help": [
                "🔢 **Aantallen**: 'Hoeveel C6 machines dit jaar?'",
                "💰 **Omzet**: 'Wat is de omzet van dit jaar?'",
                "🏆 **Top lijsten**: 'Top 5 klanten op omzet'",
                "📈 **Vergelijkingen**: 'Vergelijk dit jaar met vorig jaar'"
            ]
        }
    
    def analyze_query(self, user_query: str) -> QueryAnalysis:
        """
        Analyzes user query for intent and determines if clarification is needed.
        This addresses user feedback about the system not being smart enough.
        """
        user_query_lower = user_query.lower().strip()
        
        # Step 1: Detect primary intent
        detected_intent, confidence = self._detect_intent(user_query_lower)
        
        # Step 2: Check if clarification is needed
        needs_clarification, clarification_options = self._check_ambiguity(user_query_lower)
        
        # Step 3: Generate enhanced query if possible
        enhanced_query = self._enhance_query(user_query, detected_intent)
        
        # Step 4: Create metadata for context
        metadata = {
            "original_length": len(user_query),
            "word_count": len(user_query.split()),
            "has_specific_timeframe": bool(re.search(r"\b(dit jaar|vorig jaar|\d{4}|deze maand)\b", user_query_lower)),
            "has_numbers": bool(re.search(r"\d+", user_query)),
            "question_type": self._determine_question_type(user_query_lower)
        }
        
        return QueryAnalysis(
            original_query=user_query,
            detected_intent=detected_intent,
            confidence=confidence,
            needs_clarification=needs_clarification,
            clarification_options=clarification_options,
            enhanced_query=enhanced_query,
            metadata=metadata
        )
    
    def _detect_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Detect the primary intent with confidence scoring."""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    score += 1
            
            if score > 0:
                # Normalize score based on number of patterns
                intent_scores[intent] = score / len(patterns)
        
        if not intent_scores:
            return QueryIntent.UNKNOWN, 0.0
        
        # Get highest scoring intent
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent[0], min(best_intent[1], 1.0)
    
    def _check_ambiguity(self, query: str) -> Tuple[bool, List[ClarificationOption]]:
        """Check if query is ambiguous and needs clarification."""
        for ambiguity in self.ambiguity_patterns:
            if re.search(ambiguity["pattern"], query, re.IGNORECASE):
                return True, ambiguity["clarifications"]
        
        # Check for very vague queries
        vague_indicators = ["help", "info", "informatie", "vertel", "wat", "hoe"]
        if any(word in query for word in vague_indicators) and len(query.split()) < 4:
            return True, self._generate_general_clarifications()
        
        return False, []
    
    def _generate_general_clarifications(self) -> List[ClarificationOption]:
        """Generate general clarification options for very vague queries."""
        return [
            ClarificationOption("db_query", "📊 Ik wil cijfers/data uit de database", QueryIntent.DATABASE_QUERY),
            ClarificationOption("company_info", "🏢 Ik zoek bedrijfsinformatie", QueryIntent.COMPANY_INFO),
            ClarificationOption("contact", "📞 Ik zoek contactgegevens", QueryIntent.CONTACT_INFO),
            ClarificationOption("hr_info", "💼 Ik heb een HR/personeelsvraag", QueryIntent.HR_POLICY),
        ]
    
    def _enhance_query(self, original_query: str, intent: QueryIntent) -> str:
        """Enhance query with context for better processing."""
        if intent == QueryIntent.DATABASE_QUERY:
            # Add database context
            return f"DATABASE_QUERY: {original_query}"
        elif intent == QueryIntent.COMPANY_INFO:
            return f"COMPANY_INFO: {original_query}"
        elif intent == QueryIntent.HR_POLICY:
            return f"HR_POLICY: {original_query}"
        elif intent == QueryIntent.CONTACT_INFO:
            return f"CONTACT_INFO: {original_query}"
        
        return original_query
    
    def _determine_question_type(self, query: str) -> str:
        """Determine the type of question being asked."""
        if re.search(r"\b(hoeveel|aantal)\b", query):
            return "quantity"
        elif re.search(r"\b(wie is|wie)\b", query):
            return "person_identification"
        elif re.search(r"\b(wat is|wat)\b", query):
            return "information_request"
        elif re.search(r"\b(hoe|waarom)\b", query):
            return "process_explanation"
        elif re.search(r"\b(waar|wanneer)\b", query):
            return "location_time"
        else:
            return "general"
    
    def generate_clarification_response(self, analysis: QueryAnalysis) -> Dict:
        """
        Generate user-friendly clarification response with clickable options.
        Addresses user feedback about non-technical users needing guidance.
        """
        if not analysis.needs_clarification:
            return {"needs_clarification": False}
        
        response = {
            "needs_clarification": True,
            "message": "🤔 **Ik begrijp uw vraag, maar kan u helpen het specifieker te maken?**\n\n📝 **Kies hieronder wat u zoekt:**",
            "options": []
        }
        
        for option in analysis.clarification_options:
            response["options"].append({
                "id": option.id,
                "text": option.text,
                "intent": option.intent.value,
                "action_type": "select_option"
            })
        
        # Add helpful suggestions for non-technical users
        if analysis.detected_intent == QueryIntent.UNKNOWN:
            response["suggestions"] = self.user_friendly_suggestions["vague_query"]
        elif analysis.detected_intent == QueryIntent.DATABASE_QUERY:
            response["suggestions"] = self.user_friendly_suggestions["database_help"]
        
        return response
    
    def process_clarification_choice(self, choice_id: str, original_query: str) -> str:
        """Process user's clarification choice and return enhanced query."""
        
        # Find the clarification option
        for ambiguity in self.ambiguity_patterns:
            for option in ambiguity["clarifications"]:
                if option.id == choice_id:
                    # Generate specific query based on choice
                    if choice_id == "customer_revenue":
                        return "Geef me de top 5 klanten op omzet van dit jaar"
                    elif choice_id == "customer_count":
                        return "Hoeveel klanten hebben we in totaal?"
                    elif choice_id == "machine_production":
                        return "Hoeveel machines hebben we dit jaar geproduceerd?"
                    elif choice_id == "sales_year":
                        return "Wat is de totale omzet van dit jaar?"
                    # Add more specific mappings as needed
        
        # General fallback
        return f"{original_query} - CLARIFIED: {choice_id}"


# Example usage and testing
if __name__ == "__main__":
    preprocessor = IntelligentQueryPreprocessor()
    
    # Test cases representing user's feedback scenarios
    test_queries = [
        "Geef me de top 5 klanten van dit jaar",  # Original problematic query
        "klanten",  # Vague query needing clarification
        "machines",  # Another vague query
        "omzet",  # Ambiguous financial query
        "help",  # Very vague
        "Wie is de directeur?",  # Clear company info
        "Hoeveel C6 machines hebben we verkocht?",  # Clear database query
    ]
    
    print("🧠 INTELLIGENT QUERY PREPROCESSOR TEST")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        analysis = preprocessor.analyze_query(query)
        
        print(f"   Intent: {analysis.detected_intent.value} ({analysis.confidence:.2f})")
        print(f"   Needs clarification: {analysis.needs_clarification}")
        
        if analysis.needs_clarification:
            clarification = preprocessor.generate_clarification_response(analysis)
            print(f"   Clarification options: {len(clarification.get('options', []))}")
            for option in clarification.get('options', []):
                print(f"     - {option['text']}")
        
        if analysis.enhanced_query != analysis.original_query:
            print(f"   Enhanced: '{analysis.enhanced_query}'")
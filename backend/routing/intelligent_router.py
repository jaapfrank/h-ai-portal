#!/usr/bin/env python3
"""
Intelligent Query Router - AI-Powered Dynamic Question Routing
This replaces static mappings with intelligent AI decision making
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio

class IntelligentQueryRouter:
    """AI-powered router that dynamically determines how to handle any question"""
    
    def __init__(self):
        self.database_capabilities = {
            "ERP": {
                "description": "Production, machines, sales invoices, customers, suppliers",
                "keywords": ["machine", "productie", "verkoop", "factuur", "klant", "leverancier", "omzet", "order"],
                "tables": ["V_R_SERVICEOBJECT", "V_R_SALESINVOICE", "V_R_RELATION", "V_R_PURCHASEORDER"],
                "confidence_boost": 0.2
            },
            "ACCOUNTVIEW": {
                "description": "Financial data, accounting, cash flow, revenue analysis", 
                "keywords": ["financieel", "boekhouding", "cash", "stroom", "analyse", "kosten"],
                "tables": ["DAILY", "LEDGER", "TRANSACT"],
                "confidence_boost": 0.15
            },
            "COMPANY_KNOWLEDGE": {
                "description": "Employee info, organization, HR policies, contacts",
                "keywords": ["directeur", "telefoonnummer", "verlof", "hr", "werknemers", "organisatie"],
                "tables": ["hoeflon_company.db"],
                "confidence_boost": 0.3
            }
        }
        
        self.learning_history = []
        self.query_patterns = {}
        
    async def route_question_intelligently(self, user_question: str, session_id: str = None) -> Dict[str, Any]:
        """Main intelligent routing function - decides how to handle any question"""
        
        print(f"🧠 INTELLIGENT ROUTING: '{user_question}'")
        
        # Step 1: Analyze question intent using AI
        intent_analysis = await self._analyze_question_intent(user_question)
        
        # Step 2: Determine best database(s) to query
        database_routing = self._determine_database_routing(user_question, intent_analysis)
        
        # Step 3: Choose query generation method
        query_method = self._choose_query_method(user_question, database_routing)
        
        # Step 4: Generate intelligent response strategy
        response_strategy = self._create_response_strategy(user_question, database_routing, query_method)
        
        result = {
            "question": user_question,
            "intent": intent_analysis,
            "routing": database_routing,
            "method": query_method,
            "strategy": response_strategy,
            "confidence": self._calculate_routing_confidence(intent_analysis, database_routing),
            "timestamp": datetime.now().isoformat()
        }
        
        # Learn from this routing decision
        self._learn_from_routing(result)
        
        print(f"🎯 ROUTING DECISION: {database_routing['primary_database']} ({database_routing['confidence']:.1%})")
        print(f"⚡ QUERY METHOD: {query_method['type']} ({query_method['confidence']:.1%})")
        
        return result
    
    async def _analyze_question_intent(self, question: str) -> Dict[str, Any]:
        """Use AI to understand what the user really wants to know"""
        
        question_lower = question.lower()
        
        # Intent categories
        intent_patterns = {
            "COUNT_QUERY": {
                "patterns": [r"hoeveel", r"aantal", r"count", r"tel"],
                "confidence_base": 0.8,
                "description": "User wants to count something"
            },
            "FINANCIAL_QUERY": {
                "patterns": [r"omzet", r"€", r"euro", r"kosten", r"prijs", r"waarde", r"factuur"],
                "confidence_base": 0.9,
                "description": "User wants financial information"
            },
            "PRODUCTION_QUERY": {
                "patterns": [r"machine", r"productie", r"gebouwd", r"geproduceerd", r"gereed"],
                "confidence_base": 0.85,
                "description": "User wants production information"
            },
            "PERSON_QUERY": {
                "patterns": [r"directeur", r"telefoonnummer", r"manager", r"werknemer"],
                "confidence_base": 0.95,
                "description": "User wants employee/contact information"
            },
            "PERFORMANCE_QUERY": {
                "patterns": [r"performance", r"prestatie", r"delivery", r"beste", r"slechtste"],
                "confidence_base": 0.8,
                "description": "User wants performance analysis"
            },
            "COMPARISON_QUERY": {
                "patterns": [r"vergelijk", r"vs", r"tegen", r"verschil"],
                "confidence_base": 0.7,
                "description": "User wants to compare things"
            }
        }
        
        detected_intents = {}
        for intent_name, intent_info in intent_patterns.items():
            confidence = 0.0
            matches = []
            
            for pattern in intent_info["patterns"]:
                if re.search(pattern, question_lower):
                    confidence = intent_info["confidence_base"]
                    matches.append(pattern)
            
            if confidence > 0:
                detected_intents[intent_name] = {
                    "confidence": confidence,
                    "matches": matches,
                    "description": intent_info["description"]
                }
        
        # Determine primary intent
        primary_intent = None
        if detected_intents:
            primary_intent = max(detected_intents.keys(), 
                               key=lambda x: detected_intents[x]["confidence"])
        
        return {
            "primary_intent": primary_intent,
            "all_intents": detected_intents,
            "question_complexity": len(detected_intents),
            "analysis_confidence": max([i["confidence"] for i in detected_intents.values()]) if detected_intents else 0.0
        }
    
    def _determine_database_routing(self, question: str, intent_analysis: Dict) -> Dict[str, Any]:
        """Intelligently determine which database(s) should handle this question"""
        
        question_lower = question.lower()
        database_scores = {}
        
        # Score each database based on keywords and intent
        for db_name, db_info in self.database_capabilities.items():
            score = 0.0
            matched_keywords = []
            
            # Keyword matching
            for keyword in db_info["keywords"]:
                if keyword in question_lower:
                    score += 0.2
                    matched_keywords.append(keyword)
            
            # Intent-based boosting
            primary_intent = intent_analysis.get("primary_intent")
            if primary_intent:
                if primary_intent == "PERSON_QUERY" and db_name == "COMPANY_KNOWLEDGE":
                    score += 0.5
                elif primary_intent in ["FINANCIAL_QUERY"] and db_name == "ACCOUNTVIEW":
                    score += 0.4
                elif primary_intent in ["PRODUCTION_QUERY", "COUNT_QUERY"] and db_name == "ERP":
                    score += 0.4
                elif primary_intent == "PERFORMANCE_QUERY" and db_name == "ERP":
                    score += 0.3
            
            # Apply confidence boost
            score += db_info.get("confidence_boost", 0.0)
            
            if score > 0:
                database_scores[db_name] = {
                    "score": min(1.0, score),
                    "matched_keywords": matched_keywords,
                    "reasoning": f"Matched {len(matched_keywords)} keywords, intent: {primary_intent}"
                }
        
        # Determine primary and secondary databases
        primary_db = None
        secondary_dbs = []
        
        if database_scores:
            sorted_dbs = sorted(database_scores.items(), key=lambda x: x[1]["score"], reverse=True)
            primary_db = sorted_dbs[0][0]
            
            # Secondary databases (if scores are close)
            for db_name, db_info in sorted_dbs[1:]:
                if db_info["score"] > 0.3:  # Threshold for secondary consideration
                    secondary_dbs.append(db_name)
        
        return {
            "primary_database": primary_db,
            "secondary_databases": secondary_dbs,
            "database_scores": database_scores,
            "confidence": database_scores.get(primary_db, {}).get("score", 0.0) if primary_db else 0.0,
            "multi_database_needed": len(secondary_dbs) > 0
        }
    
    def _choose_query_method(self, question: str, database_routing: Dict) -> Dict[str, Any]:
        """Choose the best method to generate and execute the query"""
        
        primary_db = database_routing.get("primary_database")
        confidence = database_routing.get("confidence", 0.0)
        
        # Method selection logic
        if primary_db == "COMPANY_KNOWLEDGE":
            return {
                "type": "COMPANY_DATABASE_LOOKUP",
                "confidence": 0.95,
                "reasoning": "Direct company database search",
                "fallback": None
            }
        
        elif primary_db in ["ERP", "ACCOUNTVIEW"]:
            if confidence > 0.8:
                return {
                    "type": "AI_SQL_GENERATION", 
                    "confidence": 0.85,
                    "reasoning": "High confidence AI SQL generation",
                    "fallback": "INTELLIGENT_TABLE_ANALYSIS"
                }
            else:
                return {
                    "type": "INTELLIGENT_TABLE_ANALYSIS",
                    "confidence": 0.75,
                    "reasoning": "Medium confidence, use intelligent analysis",
                    "fallback": "AI_SQL_GENERATION"
                }
        
        else:
            return {
                "type": "CLARIFICATION_REQUEST",
                "confidence": 0.6,
                "reasoning": "Unclear intent, request clarification",
                "fallback": None
            }
    
    def _create_response_strategy(self, question: str, database_routing: Dict, query_method: Dict) -> Dict[str, Any]:
        """Create a comprehensive strategy for responding to the question"""
        
        strategy = {
            "approach": query_method["type"],
            "databases_to_query": [database_routing["primary_database"]],
            "expected_response_time": "2-5 seconds",
            "confidence_threshold": 0.7,
            "fallback_plan": query_method.get("fallback"),
            "enhancement_suggestions": []
        }
        
        # Add secondary databases if needed
        if database_routing.get("multi_database_needed"):
            strategy["databases_to_query"].extend(database_routing["secondary_databases"])
            strategy["approach"] = "MULTI_DATABASE_QUERY"
            strategy["expected_response_time"] = "5-10 seconds"
        
        # Add enhancement suggestions
        primary_intent = database_routing.get("primary_intent")
        if primary_intent == "COMPARISON_QUERY":
            strategy["enhancement_suggestions"].append("Offer drill-down options for detailed comparison")
        elif primary_intent == "PERFORMANCE_QUERY":
            strategy["enhancement_suggestions"].append("Suggest trend analysis and benchmarking")
        
        return strategy
    
    def _calculate_routing_confidence(self, intent_analysis: Dict, database_routing: Dict) -> float:
        """Calculate overall confidence in the routing decision"""
        
        intent_confidence = intent_analysis.get("analysis_confidence", 0.0)
        routing_confidence = database_routing.get("confidence", 0.0)
        
        # Weighted average with intent having higher weight
        overall_confidence = (intent_confidence * 0.6) + (routing_confidence * 0.4)
        
        return min(1.0, overall_confidence)
    
    def _learn_from_routing(self, routing_result: Dict):
        """Learn from routing decisions to improve future routing"""
        
        # Store successful routing patterns
        question = routing_result["question"].lower()
        primary_db = routing_result["routing"]["primary_database"]
        confidence = routing_result["confidence"]
        
        # Simple learning: store high-confidence patterns
        if confidence > 0.8:
            question_words = set(question.split())
            
            if primary_db not in self.query_patterns:
                self.query_patterns[primary_db] = {"successful_words": set(), "count": 0}
            
            self.query_patterns[primary_db]["successful_words"].update(question_words)
            self.query_patterns[primary_db]["count"] += 1
        
        # Keep learning history
        self.learning_history.append({
            "timestamp": routing_result["timestamp"],
            "question_hash": hash(question),
            "routing": primary_db,
            "confidence": confidence
        })
        
        # Limit history size
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-500:]
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get statistics about routing performance and learning"""
        
        total_routes = len(self.learning_history)
        if total_routes == 0:
            return {"status": "No routing history yet"}
        
        # Database usage statistics
        db_usage = {}
        confidence_scores = []
        
        for entry in self.learning_history:
            db = entry["routing"]
            if db:
                db_usage[db] = db_usage.get(db, 0) + 1
            confidence_scores.append(entry["confidence"])
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            "total_questions_routed": total_routes,
            "average_confidence": avg_confidence,
            "database_usage": db_usage,
            "learned_patterns": {db: len(patterns["successful_words"]) 
                              for db, patterns in self.query_patterns.items()},
            "high_confidence_rate": len([c for c in confidence_scores if c > 0.8]) / total_routes * 100
        }

# Factory function
def get_intelligent_router() -> IntelligentQueryRouter:
    """Get singleton intelligent router instance"""
    if not hasattr(get_intelligent_router, "_instance"):
        get_intelligent_router._instance = IntelligentQueryRouter()
    return get_intelligent_router._instance

# Test the intelligent router
async def test_intelligent_routing():
    """Test the intelligent routing system"""
    
    router = get_intelligent_router()
    
    test_questions = [
        "Hoeveel machines hebben we dit jaar geproduceerd?",
        "Wat is het telefoonnummer van Jaap Frank?", 
        "Wat is onze omzet dit jaar?",
        "Wie zijn de beste leveranciers op delivery performance?",
        "Vergelijk productie dit jaar met vorig jaar"
    ]
    
    print("🧪 TESTING INTELLIGENT QUERY ROUTING\n")
    
    for question in test_questions:
        print(f"❓ Question: '{question}'")
        result = await router.route_question_intelligently(question)
        
        print(f"   🎯 Database: {result['routing']['primary_database']}")
        print(f"   ⚡ Method: {result['method']['type']}")
        print(f"   📊 Confidence: {result['confidence']:.1%}")
        print(f"   💭 Intent: {result['intent']['primary_intent']}")
        print()
    
    # Show learning statistics
    stats = router.get_routing_statistics()
    print("📈 ROUTING STATISTICS:")
    print(f"   • Questions processed: {stats['total_questions_routed']}")
    print(f"   • Average confidence: {stats['average_confidence']:.1%}")
    print(f"   • Database usage: {stats['database_usage']}")

if __name__ == "__main__":
    asyncio.run(test_intelligent_routing())
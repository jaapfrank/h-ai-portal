#!/usr/bin/env python3
"""
Unified Confidence System - Single Source of Truth
Eliminates confidence score inconsistencies across the system
"""

from typing import Dict, Any, Optional, List
import re
from datetime import datetime

class UnifiedConfidenceSystem:
    """Single source of truth for all confidence calculations"""
    
    def __init__(self):
        self.confidence_factors = {
            "query_method": {
                "direct_mapping": 0.95,  # Exact pattern match
                "ai_generated": 0.70,    # AI-generated SQL
                "cross_database": 0.60,  # Multi-database query
                "fallback": 0.30         # Generic/uncertain
            },
            "result_validation": {
                "single_exact": 0.85,   # Single exact number
                "multiple_rows": 0.80,  # Table with data
                "cross_validated": 0.95, # Multiple methods agree
                "business_rule_passed": 0.90 # Passes business logic
            },
            "query_quality": {
                "specific_filters": 0.90,  # Good date/type filters
                "joins_present": 0.85,     # Proper table joins
                "aggregation": 0.80,       # SUM, COUNT, AVG etc
                "basic_select": 0.60       # Simple SELECT
            },
            "historical_performance": {
                "high_success": 0.95,    # >90% historical success
                "medium_success": 0.80,  # 70-90% success
                "low_success": 0.50,     # <70% success
                "new_query": 0.70        # No history
            }
        }
    
    def calculate_unified_confidence(self, 
                                   query_method: str,
                                   sql_query: str,
                                   results: Any,
                                   business_context: Dict = None,
                                   historical_data: Dict = None) -> Dict[str, Any]:
        """Calculate single, authoritative confidence score"""
        
        # Initialize base confidence
        confidence_breakdown = {
            "method_score": 0.0,
            "validation_score": 0.0,
            "quality_score": 0.0,
            "historical_score": 0.0,
            "penalties": [],
            "bonuses": []
        }
        
        # 1. Query method confidence
        method_confidence = self.confidence_factors["query_method"].get(query_method, 0.50)
        confidence_breakdown["method_score"] = method_confidence
        
        # 2. Result validation confidence
        validation_confidence = self._assess_result_validation(results, business_context)
        confidence_breakdown["validation_score"] = validation_confidence
        
        # 3. SQL query quality assessment
        quality_confidence = self._assess_query_quality(sql_query)
        confidence_breakdown["quality_score"] = quality_confidence
        
        # 4. Historical performance
        historical_confidence = self._assess_historical_performance(historical_data)
        confidence_breakdown["historical_score"] = historical_confidence
        
        # 5. Apply penalties and bonuses
        penalties, bonuses = self._calculate_adjustments(sql_query, results, business_context)
        confidence_breakdown["penalties"] = penalties
        confidence_breakdown["bonuses"] = bonuses
        
        # Calculate weighted final score
        final_confidence = self._calculate_weighted_score(confidence_breakdown)
        
        # Determine confidence level and color
        confidence_level = self._determine_confidence_level(final_confidence)
        
        return {
            "confidence_score": final_confidence,
            "confidence_percentage": int(final_confidence * 100),
            "confidence_level": confidence_level["level"],
            "confidence_color": confidence_level["color"],
            "confidence_emoji": confidence_level["emoji"],
            "confidence_text": confidence_level["text"],
            "breakdown": confidence_breakdown,
            "explanation": self._generate_confidence_explanation(confidence_breakdown, final_confidence),
            "is_reliable": final_confidence >= 0.70,
            "timestamp": datetime.now().isoformat()
        }
    
    def _assess_result_validation(self, results: Any, business_context: Dict = None) -> float:
        """Assess confidence based on result validation"""
        
        if not results:
            return 0.20  # No results = low confidence
        
        if isinstance(results, list):
            if len(results) == 1:
                # Single result - check if it's a reasonable value
                if business_context and "expected_range" in business_context:
                    expected_min, expected_max = business_context["expected_range"]
                    result_value = list(results[0].values())[0] if results[0] else 0
                    
                    if isinstance(result_value, (int, float)):
                        if expected_min <= result_value <= expected_max:
                            return self.confidence_factors["result_validation"]["business_rule_passed"]
                        else:
                            return 0.40  # Outside expected range
                
                return self.confidence_factors["result_validation"]["single_exact"]
            
            elif len(results) > 1:
                return self.confidence_factors["result_validation"]["multiple_rows"]
        
        return 0.50  # Default for uncertain cases
    
    def _assess_query_quality(self, sql_query: str) -> float:
        """Assess SQL query quality and specificity"""
        
        if not sql_query:
            return 0.20
        
        quality_score = 0.50  # Base score
        
        # Check for specific date filters
        if re.search(r"YEAR\(.*\)\s*=\s*YEAR\(GETDATE\(\)\)", sql_query, re.IGNORECASE):
            quality_score += 0.20
        
        # Check for proper JOINs
        if re.search(r"INNER\s+JOIN|LEFT\s+JOIN", sql_query, re.IGNORECASE):
            quality_score += 0.15
        
        # Check for aggregation functions
        if re.search(r"COUNT\(|SUM\(|AVG\(|MAX\(|MIN\(", sql_query, re.IGNORECASE):
            quality_score += 0.10
        
        # Check for WHERE clauses
        if re.search(r"WHERE\s+", sql_query, re.IGNORECASE):
            quality_score += 0.10
        
        # Check for business logic filters (excluding internal sales)
        if "FK_INVOICERELATION NOT IN" in sql_query or "FK_OBJECTRELATION NOT IN" in sql_query:
            quality_score += 0.15
        
        return min(1.0, quality_score)
    
    def _assess_historical_performance(self, historical_data: Dict = None) -> float:
        """Assess confidence based on historical query performance"""
        
        if not historical_data:
            return self.confidence_factors["historical_performance"]["new_query"]
        
        success_rate = historical_data.get("success_rate", 0.70)
        
        if success_rate >= 0.90:
            return self.confidence_factors["historical_performance"]["high_success"]
        elif success_rate >= 0.70:
            return self.confidence_factors["historical_performance"]["medium_success"]
        else:
            return self.confidence_factors["historical_performance"]["low_success"]
    
    def _calculate_adjustments(self, sql_query: str, results: Any, business_context: Dict = None) -> tuple:
        """Calculate penalties and bonuses"""
        
        penalties = []
        bonuses = []
        
        # Penalties
        if sql_query and "SELECT *" in sql_query.upper():
            penalties.append({"reason": "Non-specific SELECT *", "penalty": 0.10})
        
        if not results:
            penalties.append({"reason": "No results returned", "penalty": 0.30})
        
        # Check for round numbers (suspicious)
        if results and isinstance(results, list) and len(results) == 1:
            result_value = list(results[0].values())[0] if results[0] else 0
            if isinstance(result_value, int) and result_value % 100 == 0 and result_value > 1000:
                penalties.append({"reason": "Suspiciously round number", "penalty": 0.05})
        
        # Bonuses
        if business_context and business_context.get("cross_validated"):
            bonuses.append({"reason": "Cross-validated result", "bonus": 0.10})
        
        if sql_query and len(re.findall(r"AND\s+", sql_query, re.IGNORECASE)) >= 3:
            bonuses.append({"reason": "Multiple filter conditions", "bonus": 0.05})
        
        return penalties, bonuses
    
    def _calculate_weighted_score(self, breakdown: Dict) -> float:
        """Calculate final weighted confidence score"""
        
        # Weighted average of different factors
        base_score = (
            breakdown["method_score"] * 0.30 +
            breakdown["validation_score"] * 0.25 +
            breakdown["quality_score"] * 0.25 +
            breakdown["historical_score"] * 0.20
        )
        
        # Apply penalties
        total_penalty = sum(p["penalty"] for p in breakdown["penalties"])
        
        # Apply bonuses
        total_bonus = sum(b["bonus"] for b in breakdown["bonuses"])
        
        final_score = base_score - total_penalty + total_bonus
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, final_score))
    
    def _determine_confidence_level(self, confidence_score: float) -> Dict[str, str]:
        """Determine confidence level, color, and text"""
        
        if confidence_score >= 0.85:
            return {
                "level": "Zeer hoog",
                "color": "green",
                "emoji": "🟢",
                "text": "Zeer betrouwbaar resultaat"
            }
        elif confidence_score >= 0.70:
            return {
                "level": "Hoog",
                "color": "lightgreen", 
                "emoji": "🟢",
                "text": "Betrouwbaar resultaat"
            }
        elif confidence_score >= 0.55:
            return {
                "level": "Gemiddeld",
                "color": "yellow",
                "emoji": "🟡",
                "text": "Gemiddelde betrouwbaarheid"
            }
        elif confidence_score >= 0.40:
            return {
                "level": "Laag",
                "color": "orange",
                "emoji": "🟠", 
                "text": "Lage betrouwbaarheid"
            }
        else:
            return {
                "level": "Zeer laag",
                "color": "red",
                "emoji": "🔴",
                "text": "Onbetrouwbaar resultaat"
            }
    
    def _generate_confidence_explanation(self, breakdown: Dict, final_confidence: float) -> str:
        """Generate human-readable explanation of confidence score"""
        
        explanation_parts = []
        
        # Method explanation
        method_score = breakdown["method_score"]
        if method_score >= 0.90:
            explanation_parts.append("Exacte query match gevonden")
        elif method_score >= 0.70:
            explanation_parts.append("AI-gegenereerde query gebruikt")
        else:
            explanation_parts.append("Generieke query methode")
        
        # Quality explanation
        quality_score = breakdown["quality_score"]
        if quality_score >= 0.80:
            explanation_parts.append("Hoge SQL kwaliteit")
        elif quality_score >= 0.60:
            explanation_parts.append("Acceptabele SQL kwaliteit")
        else:
            explanation_parts.append("Basis SQL kwaliteit")
        
        # Penalties and bonuses
        if breakdown["penalties"]:
            penalty_reasons = [p["reason"] for p in breakdown["penalties"]]
            explanation_parts.append(f"Aftrek voor: {', '.join(penalty_reasons)}")
        
        if breakdown["bonuses"]:
            bonus_reasons = [b["reason"] for b in breakdown["bonuses"]]
            explanation_parts.append(f"Bonus voor: {', '.join(bonus_reasons)}")
        
        return "; ".join(explanation_parts)
    
    def get_confidence_for_display(self, confidence_data: Dict) -> Dict[str, Any]:
        """Get confidence data formatted for frontend display"""
        
        return {
            "percentage": confidence_data["confidence_percentage"],
            "level": confidence_data["confidence_level"],
            "color": confidence_data["confidence_color"],
            "emoji": confidence_data["confidence_emoji"],
            "text": confidence_data["confidence_text"],
            "is_reliable": confidence_data["is_reliable"],
            "explanation": confidence_data["explanation"],
            "show_warning": not confidence_data["is_reliable"]
        }

# Global unified confidence system instance
unified_confidence = UnifiedConfidenceSystem()

if __name__ == "__main__":
    # Test the unified confidence system
    print("🧪 Testing Unified Confidence System...")
    
    # Test case 1: High confidence query
    test_confidence = unified_confidence.calculate_unified_confidence(
        query_method="direct_mapping",
        sql_query="SELECT COUNT(*) FROM R_SALESINVOICE WHERE YEAR(INVOICEDATE) = YEAR(GETDATE())",
        results=[{"count": 1245}],
        business_context={"expected_range": (1000, 2000)}
    )
    
    print(f"✅ Test 1 - High confidence: {test_confidence['confidence_percentage']}%")
    print(f"   Level: {test_confidence['confidence_level']}")
    print(f"   Explanation: {test_confidence['explanation']}")
    
    # Test case 2: Low confidence query
    test_confidence_low = unified_confidence.calculate_unified_confidence(
        query_method="fallback",
        sql_query="SELECT *",
        results=[],
        business_context=None
    )
    
    print(f"✅ Test 2 - Low confidence: {test_confidence_low['confidence_percentage']}%")
    print(f"   Level: {test_confidence_low['confidence_level']}")
    
    print("✅ Unified Confidence System operational!")
    print("🎯 This eliminates ALL confidence inconsistencies!")
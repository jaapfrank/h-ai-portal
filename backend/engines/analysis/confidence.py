#!/usr/bin/env python3
"""
Improved Confidence Calculator - More Realistic Confidence Scoring
Addresses the issue where single results were getting 100% confidence inappropriately
"""

import re
import statistics
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
import logging

class ImprovedConfidenceCalculator:
    """Calculate more realistic confidence scores based on multiple sophisticated factors"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Confidence caps based on scenario
        self.confidence_caps = {
            "single_result_simple": 0.85,     # Single result from simple query
            "single_result_complex": 0.90,    # Single result from complex query  
            "multiple_results": 0.92,         # Multiple related results
            "cross_validated": 0.95,          # Cross-validated results
            "manual_verified": 0.98           # Manually verified results
        }
        
        # Base confidence by query method
        self.method_confidence = {
            "direct_mapping": 0.75,           # Direct mapping has known limitations
            "ai_generated": 0.65,             # AI can hallucinate or misinterpret
            "hybrid": 0.70,                   # Hybrid adds complexity
            "drill_down": 0.80,               # Context helps but depends on previous query
            "cross_database": 0.60,           # Cross-database adds complexity risks
            "unknown": 0.50                   # Unknown method gets low confidence
        }
        
        # Penalty factors for common issues
        self.penalty_factors = {
            "round_number": 0.95,             # Suspiciously round numbers
            "no_time_filter": 0.90,           # Missing expected time filters
            "overly_broad": 0.85,             # Query too broad for question
            "data_inconsistency": 0.70,       # Data inconsistencies detected
            "empty_result": 0.20,             # No results found
            "unreasonable_value": 0.40        # Unreasonable values detected
        }
    
    def calculate_improved_confidence(self, question: str, query: str, results: List[Dict[str, Any]], 
                                    query_method: str, cross_validation_result=None) -> float:
        """Calculate improved confidence score with more realistic expectations"""
        
        # Start with method-based confidence
        base_confidence = self.method_confidence.get(query_method, 0.50)
        
        # Apply result-based adjustments
        result_confidence = self._assess_result_confidence(results, question)
        base_confidence = (base_confidence + result_confidence) / 2
        
        # Apply query quality assessment
        query_quality = self._assess_query_quality(query, question)
        base_confidence *= query_quality
        
        # Apply business logic validation
        business_validation = self._assess_business_logic(question, results)
        base_confidence *= business_validation
        
        # Apply cross-validation adjustment
        if cross_validation_result:
            cross_val_adjustment = self._assess_cross_validation(cross_validation_result)
            base_confidence *= cross_val_adjustment
        
        # Apply scenario-based caps
        scenario_cap = self._determine_scenario_cap(results, query, cross_validation_result)
        base_confidence = min(base_confidence, scenario_cap)
        
        # Apply penalties for detected issues
        penalty_multiplier = self._calculate_penalty_multiplier(question, query, results)
        base_confidence *= penalty_multiplier
        
        # Final bounds: never below 10% or above 95%
        return max(0.10, min(0.95, base_confidence))
    
    def _assess_result_confidence(self, results: List[Dict[str, Any]], question: str) -> float:
        """Assess confidence based on result characteristics"""
        if not results:
            return 0.1  # Very low confidence for no results
        
        result_confidence = 0.6  # Base confidence for having results
        
        # Single result analysis
        if len(results) == 1:
            result = results[0]
            
            # Single value result gets moderate confidence at best
            if len(result) == 1:
                value = list(result.values())[0]
                
                if isinstance(value, (int, float)):
                    # Check value reasonableness
                    if self._is_reasonable_value(value, question):
                        result_confidence = 0.75  # Reasonable single value
                    else:
                        result_confidence = 0.45  # Unreasonable single value
                    
                    # Penalty for suspiciously round numbers
                    if self._is_suspiciously_round(value):
                        result_confidence *= 0.90
                
                else:
                    result_confidence = 0.65  # Non-numeric single result
            
            # Single record with multiple fields
            else:
                result_confidence = 0.70  # Richer single result
        
        # Multiple results
        else:
            if len(results) <= 10:
                result_confidence = 0.80  # Good number of results
            elif len(results) <= 100:
                result_confidence = 0.75  # Manageable result set
            else:
                result_confidence = 0.65  # Large result set may be too broad
        
        return result_confidence
    
    def _is_reasonable_value(self, value: float, question: str) -> bool:
        """Check if a value is reasonable given the question context"""
        question_lower = question.lower()
        
        # Machine/production reasonableness
        if any(word in question_lower for word in ["machines", "geproduceerd", "kranen", "productie"]):
            return 0 <= value <= 2000  # Reasonable range for Hoeflon production
        
        # Revenue reasonableness
        elif any(word in question_lower for word in ["omzet", "revenue", "verkoop"]):
            return 0 <= value <= 200000000  # Reasonable range for Hoeflon revenue (0-200M)
        
        # Count reasonableness
        elif any(word in question_lower for word in ["aantal", "hoeveel", "count"]):
            return value >= 0  # Counts should be non-negative
        
        # Default reasonableness
        return True
    
    def _is_suspiciously_round(self, value: float) -> bool:
        """Check if a number is suspiciously round (might indicate estimation)"""
        if value <= 0:
            return False
        
        # Check for round thousands, ten-thousands, etc.
        if value >= 1000 and value % 1000 == 0:
            return True
        if value >= 100 and value % 100 == 0 and value >= 1000:
            return True
        
        return False
    
    def _assess_query_quality(self, query: str, question: str) -> float:
        """Assess the quality and appropriateness of the query"""
        query_upper = query.upper()
        question_lower = question.lower()
        
        quality_score = 0.8  # Base quality score
        
        # Positive indicators
        if "WHERE" in query_upper:
            quality_score += 0.05  # Filtering is good
        
        if "JOIN" in query_upper:
            quality_score += 0.05  # Joins show data relationships
        
        # Time filter alignment
        time_mentioned = any(word in question_lower for word in ["jaar", "maand", "dit", "vorig", "year", "month"])
        time_filtered = any(func in query_upper for func in ["YEAR(", "MONTH(", "DATEADD"])
        
        if time_mentioned and time_filtered:
            quality_score += 0.08  # Good time alignment
        elif time_mentioned and not time_filtered:
            quality_score -= 0.15  # Missing expected time filter
        
        # Product filter alignment
        product_mentioned = any(word in question_lower for word in ["c6", "c30", "machines", "kranen"])
        product_filtered = "DESCRIPTION LIKE" in query_upper or "ITEM" in query_upper
        
        if product_mentioned and product_filtered:
            quality_score += 0.05  # Good product filtering
        elif product_mentioned and not product_filtered:
            quality_score -= 0.10  # Missing expected product filter
        
        # External sales filter (good practice for Hoeflon)
        if "INVOICERELATION NOT IN" in query_upper:
            quality_score += 0.05  # Excluding internal sales is good
        
        # Complexity penalty (overly complex queries can introduce errors)
        complexity_indicators = [
            "SUBQUERY" in query_upper,
            "UNION" in query_upper,
            "CASE WHEN" in query_upper,
            "HAVING" in query_upper
        ]
        complexity_count = sum(complexity_indicators)
        if complexity_count > 2:
            quality_score *= 0.9  # Penalty for over-complexity
        
        return max(0.4, min(1.0, quality_score))
    
    def _assess_business_logic(self, question: str, results: List[Dict[str, Any]]) -> float:
        """Assess business logic compliance"""
        if not results:
            return 0.5  # Neutral for no results
        
        business_score = 0.9  # Start optimistic
        
        # Check for impossible business scenarios
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    
                    # Negative counts are impossible
                    if any(word in key.lower() for word in ["count", "aantal"]) and value < 0:
                        business_score *= 0.3  # Severe penalty
                    
                    # Machine production limits
                    if any(word in question.lower() for word in ["machines", "productie"]):
                        if value > 1000:  # Unrealistically high production
                            business_score *= 0.6
                        elif value == 0 and "dit jaar" in question.lower():
                            business_score *= 0.7  # Zero production this year is suspicious
                    
                    # Revenue reasonableness
                    if any(word in question.lower() for word in ["omzet", "revenue"]):
                        if value > 100000000:  # > 100M might be suspicious
                            business_score *= 0.8
                        elif value < 0:  # Negative revenue
                            business_score *= 0.4
        
        return business_score
    
    def _assess_cross_validation(self, cross_validation_result) -> float:
        """Assess cross-validation results"""
        if not cross_validation_result:
            return 1.0  # No penalty if no cross-validation
        
        if hasattr(cross_validation_result, 'is_consistent') and hasattr(cross_validation_result, 'confidence_score'):
            if cross_validation_result.is_consistent:
                return min(1.2, 1.0 + (cross_validation_result.confidence_score - 0.8) * 0.5)  # Boost for consistency
            else:
                # Check for critical inconsistencies
                if hasattr(cross_validation_result, 'discrepancies'):
                    for discrepancy in cross_validation_result.discrepancies:
                        if discrepancy.get("severity") == "critical":
                            return 0.25  # Severe penalty for critical inconsistencies
                
                return 0.7  # Normal penalty for inconsistency
        
        return 0.8  # Default moderate penalty
    
    def _determine_scenario_cap(self, results: List[Dict[str, Any]], query: str, cross_validation_result) -> float:
        """Determine the maximum confidence cap based on scenario"""
        
        # Cross-validated results can have higher caps
        if cross_validation_result and hasattr(cross_validation_result, 'is_consistent') and cross_validation_result.is_consistent:
            return self.confidence_caps["cross_validated"]
        
        # Multiple results generally more reliable than single
        if len(results) > 1:
            return self.confidence_caps["multiple_results"]
        
        # Single result scenarios
        if len(results) == 1:
            query_upper = query.upper()
            
            # Complex queries with joins and filters get higher cap
            if "JOIN" in query_upper and "WHERE" in query_upper:
                return self.confidence_caps["single_result_complex"]
            else:
                return self.confidence_caps["single_result_simple"]
        
        # No results
        return 0.3
    
    def _calculate_penalty_multiplier(self, question: str, query: str, results: List[Dict[str, Any]]) -> float:
        """Calculate penalty multiplier for detected issues"""
        penalty_multiplier = 1.0
        
        # No results penalty
        if not results:
            penalty_multiplier *= self.penalty_factors["empty_result"]
        
        # Suspiciously round numbers
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)) and self._is_suspiciously_round(value):
                    penalty_multiplier *= self.penalty_factors["round_number"]
                    break  # Only apply penalty once per result set
        
        # Missing time filter when expected
        question_lower = question.lower()
        query_upper = query.upper()
        
        time_mentioned = any(word in question_lower for word in ["jaar", "maand", "dit", "vorig"])
        time_filtered = any(func in query_upper for func in ["YEAR(", "MONTH(", "DATEADD"])
        
        if time_mentioned and not time_filtered:
            penalty_multiplier *= self.penalty_factors["no_time_filter"]
        
        # Overly broad queries (no WHERE clause when one would be expected)
        if "WHERE" not in query_upper and any(word in question_lower for word in ["dit jaar", "c6", "specifiek"]):
            penalty_multiplier *= self.penalty_factors["overly_broad"]
        
        return penalty_multiplier
    
    def get_confidence_explanation(self, confidence_score: float) -> Dict[str, str]:
        """Get human-readable explanation of confidence score"""
        
        if confidence_score >= 0.85:
            level = "Hoog"
            emoji = "🟢"
            explanation = "Deze gegevens zijn zeer betrouwbaar en kunnen vertrouwd worden voor besluitvorming."
        elif confidence_score >= 0.70:
            level = "Goed"
            emoji = "🟡"
            explanation = "Deze gegevens zijn waarschijnlijk correct, maar overweeg aanvullende verificatie voor kritieke beslissingen."
        elif confidence_score >= 0.55:
            level = "Matig"
            emoji = "🟠"
            explanation = "Deze gegevens vereisen voorzichtigheid en zouden geverifieerd moeten worden."
        else:
            level = "Laag"
            emoji = "🔴"
            explanation = "Deze gegevens zijn onbetrouwbaar en moeten met grote voorzichtigheid gebruikt worden."
        
        return {
            "level": level,
            "emoji": emoji,
            "explanation": explanation,
            "percentage": f"{confidence_score:.0%}"
        }
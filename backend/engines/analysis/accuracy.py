#!/usr/bin/env python3
"""
Comprehensive Accuracy Engine for Hoeflon AI
Orchestrates all accuracy improvement systems for maximum reliability
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import logging

from enhanced_result_validator import EnhancedResultValidator, ValidationResult
from multi_query_validator import MultiQueryValidator, CrossValidationResult

@dataclass
class AccuracyAssessment:
    """Comprehensive accuracy assessment"""
    overall_confidence: float
    is_reliable: bool
    validation_result: ValidationResult
    cross_validation_result: Optional[CrossValidationResult]
    accuracy_score: float
    reliability_factors: Dict[str, float]
    recommendations: List[str]
    accuracy_report: str

class AccuracyEngine:
    """Central engine for managing all accuracy improvements"""
    
    def __init__(self, execute_query_func: Callable, config_path: str = None):
        self.execute_query = execute_query_func
        self.config_path = config_path
        
        # Initialize validation systems
        self.result_validator = EnhancedResultValidator(config_path)
        self.cross_validator = MultiQueryValidator(execute_query_func)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Accuracy weights for different factors
        self.accuracy_weights = {
            "business_rules": 0.25,
            "cross_validation": 0.30,
            "data_quality": 0.20,
            "pattern_matching": 0.15,
            "historical_consistency": 0.10
        }
        
        # Confidence thresholds - LOWERED for better user experience
        self.confidence_thresholds = {
            "high": 0.85,      # High confidence - display result with minimal warnings
            "medium": 0.65,    # Medium confidence - display with caveats
            "low": 0.40,       # Low confidence - require user confirmation (LOWERED from 0.60)
            "unreliable": 0.25 # Unreliable - suggest alternative approach (LOWERED from 0.40)
        }
    
    def assess_accuracy(self, question: str, query: str, results: List[Dict[str, Any]], 
                       query_method: str = "unknown", enable_cross_validation: bool = True) -> AccuracyAssessment:
        """Comprehensive accuracy assessment using all validation systems"""
        
        self.logger.info(f"Starting accuracy assessment for question: {question[:50]}...")
        
        # 1. Enhanced Result Validation
        validation_result = self.result_validator.validate_result(
            question, query, results, query_method
        )
        
        # 2. Cross-Validation (if enabled and appropriate)
        cross_validation_result = None
        if enable_cross_validation and self._should_cross_validate(question, results):
            try:
                cross_validation_result = self.cross_validator.cross_validate_result(
                    question, query, results
                )
            except Exception as e:
                self.logger.warning(f"Cross-validation failed: {e}")
        
        # 3. Calculate comprehensive accuracy metrics
        accuracy_metrics = self._calculate_accuracy_metrics(
            validation_result, cross_validation_result, question, results
        )
        
        # 4. Determine reliability factors
        reliability_factors = self._analyze_reliability_factors(
            validation_result, cross_validation_result, accuracy_metrics
        )
        
        # 5. Generate overall confidence score
        overall_confidence = self._calculate_overall_confidence(
            validation_result, cross_validation_result, reliability_factors
        )
        
        # 6. Determine if result is reliable
        is_reliable = self._determine_reliability(overall_confidence, validation_result)
        
        # 7. Generate recommendations
        recommendations = self._generate_comprehensive_recommendations(
            validation_result, cross_validation_result, overall_confidence, question
        )
        
        # 8. Generate accuracy report
        accuracy_report = self._generate_accuracy_report(
            validation_result, cross_validation_result, overall_confidence, 
            reliability_factors, recommendations
        )
        
        return AccuracyAssessment(
            overall_confidence=overall_confidence,
            is_reliable=is_reliable,
            validation_result=validation_result,
            cross_validation_result=cross_validation_result,
            accuracy_score=accuracy_metrics["overall_score"],
            reliability_factors=reliability_factors,
            recommendations=recommendations,
            accuracy_report=accuracy_report
        )
    
    def _should_cross_validate(self, question: str, results: List[Dict[str, Any]]) -> bool:
        """Determine if cross-validation should be performed"""
        
        # Skip cross-validation for very simple queries or empty results
        if not results or len(results) > 50:  # Too many results
            return False
        
        # Enable for important business metrics
        important_keywords = [
            "omzet", "revenue", "machines", "kranen", "productie", 
            "verkocht", "totaal", "aantal", "vergelijk"
        ]
        
        return any(keyword in question.lower() for keyword in important_keywords)
    
    def _calculate_accuracy_metrics(self, validation_result: ValidationResult, 
                                  cross_validation_result: Optional[CrossValidationResult],
                                  question: str, results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate comprehensive accuracy metrics"""
        
        metrics = {
            "validation_score": validation_result.confidence_score,
            "cross_validation_score": 1.0,  # Default if no cross-validation
            "data_completeness": self._assess_data_completeness(results),
            "result_reasonableness": self._assess_reasonableness(question, results),
            "pattern_consistency": self._assess_pattern_consistency(results),
            "overall_score": 0.0
        }
        
        if cross_validation_result:
            metrics["cross_validation_score"] = cross_validation_result.confidence_score
        
        # Calculate weighted overall score
        metrics["overall_score"] = (
            metrics["validation_score"] * 0.35 +
            metrics["cross_validation_score"] * 0.25 +
            metrics["data_completeness"] * 0.15 +
            metrics["result_reasonableness"] * 0.15 +
            metrics["pattern_consistency"] * 0.10
        )
        
        return metrics
    
    def _assess_data_completeness(self, results: List[Dict[str, Any]]) -> float:
        """Assess completeness of data in results"""
        if not results:
            return 0.0
        
        total_fields = 0
        non_null_fields = 0
        
        for result in results:
            for key, value in result.items():
                total_fields += 1
                if value is not None and value != "" and str(value).strip() != "":
                    non_null_fields += 1
        
        return non_null_fields / total_fields if total_fields > 0 else 1.0
    
    def _assess_reasonableness(self, question: str, results: List[Dict[str, Any]]) -> float:
        """Assess reasonableness of results"""
        if not results:
            return 0.5
        
        reasonableness_score = 1.0
        
        # Check for suspiciously round numbers
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)) and value > 1000:
                    if value % 1000 == 0:  # Round thousands
                        reasonableness_score *= 0.95
                    if value % 10000 == 0:  # Round ten-thousands
                        reasonableness_score *= 0.90
        
        # Check for negative values where inappropriate
        question_lower = question.lower()
        if any(word in question_lower for word in ["aantal", "count", "machines", "kranen"]):
            for result in results:
                for key, value in result.items():
                    if isinstance(value, (int, float)) and value < 0:
                        reasonableness_score *= 0.3  # Very suspicious
        
        return max(0.1, reasonableness_score)
    
    def _assess_pattern_consistency(self, results: List[Dict[str, Any]]) -> float:
        """Assess consistency of patterns in results"""
        if len(results) <= 1:
            return 1.0
        
        # Look for consistent data types and ranges
        consistency_score = 1.0
        
        # Check for consistent data types across rows
        field_types = {}
        for result in results:
            for key, value in result.items():
                value_type = type(value).__name__
                if key not in field_types:
                    field_types[key] = set()
                field_types[key].add(value_type)
        
        # Penalize inconsistent types
        for field, types in field_types.items():
            if len(types) > 1:
                consistency_score *= 0.9
        
        return max(0.5, consistency_score)
    
    def _analyze_reliability_factors(self, validation_result: ValidationResult,
                                   cross_validation_result: Optional[CrossValidationResult],
                                   accuracy_metrics: Dict[str, float]) -> Dict[str, float]:
        """Analyze factors affecting reliability"""
        
        factors = {
            "business_rule_compliance": validation_result.confidence_score,
            "data_quality": accuracy_metrics["data_completeness"],
            "cross_validation_consistency": 1.0,
            "pattern_validity": accuracy_metrics["pattern_consistency"],
            "result_reasonableness": accuracy_metrics["result_reasonableness"]
        }
        
        if cross_validation_result:
            factors["cross_validation_consistency"] = cross_validation_result.confidence_score
        
        return factors
    
    def _calculate_overall_confidence(self, validation_result: ValidationResult,
                                    cross_validation_result: Optional[CrossValidationResult],
                                    reliability_factors: Dict[str, float]) -> float:
        """Calculate overall confidence score"""
        
        # Base confidence from validation
        base_confidence = validation_result.confidence_score
        
        # Adjust based on cross-validation
        if cross_validation_result:
            if cross_validation_result.is_consistent:
                # Boost confidence for consistent cross-validation
                base_confidence = min(0.98, base_confidence * 1.15)
            else:
                # Check for critical logical inconsistencies
                critical_inconsistency = False
                if cross_validation_result.discrepancies:
                    for discrepancy in cross_validation_result.discrepancies:
                        if discrepancy.get("severity") == "critical" or "LOGICAL INCONSISTENCY" in str(discrepancy.get("discrepancy", "")):
                            critical_inconsistency = True
                            break
                
                if critical_inconsistency:
                    # Severe penalty for logical inconsistencies (e.g., C6 > Total)
                    base_confidence *= 0.2  # Reduce to 20% of original confidence
                else:
                    # Normal penalty for inconsistent cross-validation
                    base_confidence *= 0.75
        
        # Apply reliability factors
        weighted_confidence = base_confidence
        for factor, weight in self.accuracy_weights.items():
            if factor in reliability_factors:
                weighted_confidence *= (1 + (reliability_factors[factor] - 0.5) * weight)
        
        # Cap confidence between 0.1 and 0.98
        return max(0.1, min(0.98, weighted_confidence))
    
    def _determine_reliability(self, confidence: float, validation_result: ValidationResult) -> bool:
        """Determine if result is reliable enough to present"""
        
        # High confidence is always reliable
        if confidence >= self.confidence_thresholds["high"]:
            return True
        
        # Medium confidence is reliable if no critical errors
        if confidence >= self.confidence_thresholds["medium"]:
            critical_errors = [
                issue for issue in validation_result.issues_found
                if issue.get("severity") == "error"
            ]
            return len(critical_errors) == 0
        
        # Low confidence requires manual review
        return False
    
    def _generate_comprehensive_recommendations(self, validation_result: ValidationResult,
                                              cross_validation_result: Optional[CrossValidationResult],
                                              confidence: float, question: str) -> List[str]:
        """Generate comprehensive recommendations"""
        
        recommendations = []
        
        # Confidence-based recommendations
        if confidence >= self.confidence_thresholds["high"]:
            recommendations.append("✅ Hoge betrouwbaarheid - resultaat is zeer waarschijnlijk correct")
        elif confidence >= self.confidence_thresholds["medium"]:
            recommendations.append("🟡 Gemiddelde betrouwbaarheid - resultaat is waarschijnlijk correct")
            recommendations.append("💡 Overweeg om vraag te specificeren voor hogere betrouwbaarheid")
        elif confidence >= self.confidence_thresholds["low"]:
            recommendations.append("🟠 Lage betrouwbaarheid - controleer resultaat handmatig")
            recommendations.append("🔍 Verfijn uw vraag met meer specifieke criteria")
        else:
            recommendations.append("🔴 Onbetrouwbaar resultaat - alternative approach aanbevolen")
            recommendations.append("❓ Stel een meer specifieke vraag of controleer data kwaliteit")
        
        # Add validation-specific recommendations
        recommendations.extend(validation_result.suggestions[:2])
        
        # Add cross-validation recommendations
        if cross_validation_result and cross_validation_result.recommendations:
            recommendations.extend(cross_validation_result.recommendations[:1])
        
        return recommendations[:4]  # Limit to top 4 recommendations
    
    def _generate_accuracy_report(self, validation_result: ValidationResult,
                                cross_validation_result: Optional[CrossValidationResult],
                                confidence: float, reliability_factors: Dict[str, float],
                                recommendations: List[str]) -> str:
        """Generate comprehensive accuracy report"""
        
        # Determine confidence level
        if confidence >= self.confidence_thresholds["high"]:
            confidence_text = "🟢 **HOGE BETROUWBAARHEID**"
            confidence_desc = "Resultaat is zeer betrouwbaar"
        elif confidence >= self.confidence_thresholds["medium"]:
            confidence_text = "🟡 **GEMIDDELDE BETROUWBAARHEID**"
            confidence_desc = "Resultaat is waarschijnlijk correct"
        elif confidence >= self.confidence_thresholds["low"]:
            confidence_text = "🟠 **LAGE BETROUWBAARHEID**"
            confidence_desc = "Resultaat vereist verificatie"
        else:
            confidence_text = "🔴 **ONBETROUWBAAR**"
            confidence_desc = "Resultaat is mogelijk incorrect"
        
        report = f"""
{confidence_text} ({confidence:.0%})
{confidence_desc}

**Betrouwbaarheidsanalyse:**
• Validatie score: {validation_result.confidence_score:.0%}
• Data kwaliteit: {reliability_factors.get('data_quality', 0):.0%}
• Patroon consistentie: {reliability_factors.get('pattern_validity', 0):.0%}
"""
        
        if cross_validation_result:
            report += f"• Cross-validatie: {cross_validation_result.confidence_score:.0%}\n"
        
        # Add critical issues
        critical_issues = [
            issue for issue in validation_result.issues_found
            if issue.get("severity") == "error"
        ]
        
        if critical_issues:
            report += f"\n**⚠️ Kritieke problemen:** {len(critical_issues)}\n"
            for issue in critical_issues[:2]:
                report += f"• {issue.get('message', 'Onbekend probleem')}\n"
        
        # Add top recommendations
        if recommendations:
            report += "\n**📋 Aanbevelingen:**\n"
            for rec in recommendations[:2]:
                report += f"• {rec}\n"
        
        return report.strip()
    
    def get_confidence_level(self, confidence: float) -> str:
        """Get confidence level description"""
        if confidence >= self.confidence_thresholds["high"]:
            return "high"
        elif confidence >= self.confidence_thresholds["medium"]:
            return "medium"
        elif confidence >= self.confidence_thresholds["low"]:
            return "low"
        else:
            return "unreliable"
    
    def should_display_result(self, assessment: AccuracyAssessment) -> bool:
        """Determine if result should be displayed to user"""
        return assessment.is_reliable and assessment.overall_confidence >= self.confidence_thresholds["low"]
    
    def get_user_warning_message(self, assessment: AccuracyAssessment) -> Optional[str]:
        """Get warning message for user if needed"""
        confidence_level = self.get_confidence_level(assessment.overall_confidence)
        
        if confidence_level == "unreliable":
            return "⚠️ Dit resultaat is mogelijk onbetrouwbaar. Stel een meer specifieke vraag of controleer handmatig."
        elif confidence_level == "low":
            return "🔍 Let op: dit resultaat heeft lage betrouwbaarheid. Verifieer indien mogelijk."
        elif confidence_level == "medium":
            return "💡 Tip: voor hogere betrouwbaarheid, specificeer uw vraag verder."
        
        return None
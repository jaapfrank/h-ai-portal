#!/usr/bin/env python3
"""
Enhanced Result Validation Engine for Hoeflon AI
Validates query results against business rules, historical patterns, and reasonableness checks
"""

import re
import json
import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics
import logging

@dataclass
class ValidationRule:
    """Represents a business validation rule"""
    name: str
    rule_type: str  # 'range', 'pattern', 'business_logic', 'historical_comparison'
    description: str
    parameters: Dict[str, Any]
    severity: str  # 'error', 'warning', 'info'
    confidence_impact: float  # How much this rule affects confidence (0.0 to 1.0)

@dataclass
class ValidationResult:
    """Result of validation check"""
    is_valid: bool
    confidence_score: float
    issues_found: List[Dict[str, Any]]
    suggestions: List[str]
    validation_details: Dict[str, Any]

class EnhancedResultValidator:
    """Advanced result validation engine with business intelligence"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "..", "validation_rules.json")
        self.business_rules = self._load_business_rules()
        self.historical_patterns = {}
        self.data_quality_thresholds = self._get_data_quality_thresholds()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def _load_business_rules(self) -> List[ValidationRule]:
        """Load Hoeflon-specific business validation rules"""
        return [
            # Machine Production Rules
            ValidationRule(
                name="machine_production_range",
                rule_type="range",
                description="Machines produced per month should be within reasonable range",
                parameters={
                    "min_monthly": 5,
                    "max_monthly": 50,
                    "min_yearly": 60,
                    "max_yearly": 600
                },
                severity="warning",
                confidence_impact=0.3
            ),
            
            # C6-Specific Production Rules
            ValidationRule(
                name="c6_production_range",
                rule_type="range",
                description="C6 machines should align with known production capacity",
                parameters={
                    "max_c6_yearly": 200,  # Max ~200 C6 machines per year
                    "max_c6_monthly": 25,  # Max ~25 C6 machines per month
                    "expected_c6_total": 1403,  # Expected total C6 machines
                    "c6_percentage_of_total": 0.15  # C6 should be ~15% of total production
                },
                severity="error",
                confidence_impact=0.6
            ),
            
            # Revenue Rules
            ValidationRule(
                name="revenue_reasonableness",
                rule_type="business_logic",
                description="Revenue should align with historical patterns and business capacity",
                parameters={
                    "min_monthly_revenue": 100000,  # €100k minimum per month
                    "max_monthly_revenue": 5000000,  # €5M maximum per month
                    "growth_rate_threshold": 3.0,  # 300% growth is suspicious
                    "revenue_per_machine_min": 50000,  # €50k per machine minimum
                    "revenue_per_machine_max": 500000  # €500k per machine maximum
                },
                severity="error",
                confidence_impact=0.5
            ),
            
            # Data Consistency Rules
            ValidationRule(
                name="data_consistency",
                rule_type="pattern",
                description="Results should be consistent across different data sources",
                parameters={
                    "variance_threshold": 0.15,  # 15% variance allowed
                    "null_percentage_threshold": 0.05  # 5% null values max
                },
                severity="warning",
                confidence_impact=0.4
            ),
            
            # Time Period Rules
            ValidationRule(
                name="time_period_validation",
                rule_type="business_logic",
                description="Time-based queries should return realistic date ranges",
                parameters={
                    "earliest_valid_date": "2020-01-01",
                    "future_date_allowed": False,
                    "weekend_production_unlikely": True
                },
                severity="error",
                confidence_impact=0.6
            ),
            
            # Machine Type Rules
            ValidationRule(
                name="machine_type_validation",
                rule_type="business_logic",
                description="Machine counts should align with known Hoeflon models",
                parameters={
                    "valid_machine_types": ["C6", "C30", "C1", "C10", "JIB", "WLL"],
                    "c6_total_expected": 1403,
                    "c6_sold_expected": 1402,
                    "total_machines_expected": 9541
                },
                severity="warning",
                confidence_impact=0.3
            ),
            
            # Financial Rules
            ValidationRule(
                name="financial_validation",
                rule_type="range",
                description="Financial metrics should be within business reality",
                parameters={
                    "profit_margin_min": -0.1,  # -10% minimum (losses possible)
                    "profit_margin_max": 0.5,   # 50% maximum profit margin
                    "invoice_amount_min": 100,   # €100 minimum invoice
                    "invoice_amount_max": 1000000  # €1M maximum single invoice
                },
                severity="error",
                confidence_impact=0.5
            )
        ]
    
    def _get_data_quality_thresholds(self) -> Dict[str, float]:
        """Define data quality thresholds for validation"""
        return {
            "completeness_threshold": 0.95,  # 95% data completeness required
            "accuracy_threshold": 0.98,      # 98% accuracy required
            "consistency_threshold": 0.90,   # 90% consistency required
            "timeliness_threshold": 0.85      # 85% timeliness required
        }
    
    def validate_result(self, question: str, query: str, results: List[Dict[str, Any]], 
                       query_method: str = "unknown") -> ValidationResult:
        """Comprehensive validation of query results"""
        
        validation_issues = []
        confidence_score = 1.0
        suggestions = []
        
        # Skip validation for empty results
        if not results:
            return ValidationResult(
                is_valid=True,
                confidence_score=0.5,
                issues_found=[{"type": "no_data", "message": "No results returned"}],
                suggestions=["Verify query criteria", "Check data availability for specified period"],
                validation_details={"result_count": 0}
            )
        
        # 1. Business Rule Validation
        business_validation = self._validate_business_rules(question, results, query_method)
        validation_issues.extend(business_validation["issues"])
        confidence_score *= business_validation["confidence_multiplier"]
        suggestions.extend(business_validation["suggestions"])
        
        # 2. Data Quality Validation
        quality_validation = self._validate_data_quality(results)
        validation_issues.extend(quality_validation["issues"])
        confidence_score *= quality_validation["confidence_multiplier"]
        
        # 3. Reasonableness Checks
        reasonableness_validation = self._validate_reasonableness(question, results)
        validation_issues.extend(reasonableness_validation["issues"])
        confidence_score *= reasonableness_validation["confidence_multiplier"]
        
        # 4. Pattern Validation
        pattern_validation = self._validate_patterns(question, results)
        validation_issues.extend(pattern_validation["issues"])
        confidence_score *= pattern_validation["confidence_multiplier"]
        
        # 5. Cross-Reference Validation
        cross_ref_validation = self._validate_cross_references(question, results)
        validation_issues.extend(cross_ref_validation["issues"])
        confidence_score *= cross_ref_validation["confidence_multiplier"]
        
        # Determine overall validity
        error_count = len([issue for issue in validation_issues if issue.get("severity") == "error"])
        is_valid = error_count == 0 and confidence_score > 0.6
        
        # Cap confidence score
        confidence_score = max(0.1, min(1.0, confidence_score))
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence_score,
            issues_found=validation_issues,
            suggestions=suggestions,
            validation_details={
                "result_count": len(results),
                "validation_rules_checked": len(self.business_rules),
                "error_count": error_count,
                "warning_count": len([issue for issue in validation_issues if issue.get("severity") == "warning"])
            }
        )
    
    def _validate_business_rules(self, question: str, results: List[Dict[str, Any]], 
                                query_method: str) -> Dict[str, Any]:
        """Validate results against Hoeflon business rules"""
        issues = []
        confidence_multiplier = 1.0
        suggestions = []
        
        question_lower = question.lower()
        
        # Machine production validation
        if any(word in question_lower for word in ["machines", "kranen", "productie", "geproduceerd"]):
            machine_validation = self._validate_machine_rules(question, results)
            issues.extend(machine_validation["issues"])
            confidence_multiplier *= machine_validation["confidence_multiplier"]
            suggestions.extend(machine_validation["suggestions"])
        
        # Revenue validation
        if any(word in question_lower for word in ["omzet", "revenue", "verkocht", "factuur"]):
            revenue_validation = self._validate_revenue_rules(question, results)
            issues.extend(revenue_validation["issues"])
            confidence_multiplier *= revenue_validation["confidence_multiplier"]
            suggestions.extend(revenue_validation["suggestions"])
        
        return {
            "issues": issues,
            "confidence_multiplier": confidence_multiplier,
            "suggestions": suggestions
        }
    
    def _validate_machine_rules(self, question: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate machine-related results"""
        issues = []
        confidence_multiplier = 1.0
        suggestions = []
        
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    # Check machine counts - include unnamed columns and common patterns
                    is_count_field = (
                        "aantal" in key.lower() or 
                        "count" in key.lower() or 
                        key.strip() == "" or  # Unnamed columns from COUNT(*)
                        "machine" in key.lower() or
                        "kraan" in key.lower() or
                        ("productie" in question.lower() and isinstance(value, (int, float)))
                    )
                    
                    if is_count_field:
                        # Monthly production should be reasonable
                        if "maand" in question.lower() and (value < 3 or value > 50):
                            issues.append({
                                "type": "business_rule_violation",
                                "severity": "warning",
                                "message": f"Monthly production of {value} machines seems unusual",
                                "field": key,
                                "value": value,
                                "expected_range": "3-50 machines per month"
                            })
                            confidence_multiplier *= 0.8
                            suggestions.append("Verify production data for specified period")
                        
                        # Yearly production should be reasonable
                        if "jaar" in question.lower() and (value < 60 or value > 600):
                            issues.append({
                                "type": "business_rule_violation",
                                "severity": "warning",
                                "message": f"Yearly production of {value} machines is outside normal range",
                                "field": key,
                                "value": value,
                                "expected_range": "60-600 machines per year"
                            })
                            confidence_multiplier *= 0.7
                        
                        # C6-specific validation for yearly production
                        if "c6" in question.lower() and "jaar" in question.lower():
                            if value > 200:  # More than 200 C6 machines per year is unrealistic
                                issues.append({
                                    "type": "c6_business_rule_violation",
                                    "severity": "error",
                                    "message": f"C6 yearly production of {value} machines is unrealistically high",
                                    "field": key,
                                    "value": value,
                                    "expected_range": "Expected <200 C6 machines per year",
                                    "possible_cause": "Query may be counting total C6 machines instead of yearly production"
                                })
                                confidence_multiplier *= 0.2  # Heavy penalty for C6 overcount
                                suggestions.append("Check if query has proper yearly date filter")
                                suggestions.append("Verify C6 production vs total C6 machines")
                        
                        # C6-specific validation for monthly production  
                        if "c6" in question.lower() and "maand" in question.lower():
                            if value > 25:  # More than 25 C6 machines per month is unrealistic
                                issues.append({
                                    "type": "c6_business_rule_violation",
                                    "severity": "error", 
                                    "message": f"C6 monthly production of {value} machines is unrealistically high",
                                    "field": key,
                                    "value": value,
                                    "expected_range": "Expected <25 C6 machines per month"
                                })
                                confidence_multiplier *= 0.3
                        
                        # Total machine counts validation
                        if "totaal" in question.lower() or "total" in question.lower():
                            if "c6" in question.lower() and abs(value - 1403) > 50:
                                issues.append({
                                    "type": "data_inconsistency",
                                    "severity": "error",
                                    "message": f"C6 machine total ({value}) differs significantly from expected (~1403)",
                                    "field": key,
                                    "value": value,
                                    "expected_value": 1403
                                })
                                confidence_multiplier *= 0.5
                                suggestions.append("Verify C6 machine count against database integrity")
        
        return {
            "issues": issues,
            "confidence_multiplier": confidence_multiplier,
            "suggestions": suggestions
        }
    
    def _validate_revenue_rules(self, question: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate revenue-related results"""
        issues = []
        confidence_multiplier = 1.0
        suggestions = []
        
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)) and ("omzet" in key.lower() or "amount" in key.lower()):
                    # Monthly revenue validation
                    if "maand" in question.lower():
                        if value < 100000:  # Less than €100k per month
                            issues.append({
                                "type": "business_rule_violation",
                                "severity": "warning",
                                "message": f"Monthly revenue of €{value:,.0f} is below expected minimum",
                                "field": key,
                                "value": value,
                                "expected_minimum": 100000
                            })
                            confidence_multiplier *= 0.8
                        
                        if value > 5000000:  # More than €5M per month
                            issues.append({
                                "type": "business_rule_violation",
                                "severity": "warning",
                                "message": f"Monthly revenue of €{value:,.0f} is above expected maximum",
                                "field": key,
                                "value": value,
                                "expected_maximum": 5000000
                            })
                            confidence_multiplier *= 0.7
                    
                    # Yearly revenue validation
                    if "jaar" in question.lower():
                        if value < 1200000:  # Less than €1.2M per year
                            issues.append({
                                "type": "business_rule_violation",
                                "severity": "error",
                                "message": f"Yearly revenue of €{value:,.0f} is unrealistically low",
                                "field": key,
                                "value": value
                            })
                            confidence_multiplier *= 0.5
                        
                        if value > 60000000:  # More than €60M per year
                            issues.append({
                                "type": "business_rule_violation",
                                "severity": "warning",
                                "message": f"Yearly revenue of €{value:,.0f} is above expected range",
                                "field": key,
                                "value": value
                            })
                            confidence_multiplier *= 0.8
        
        return {
            "issues": issues,
            "confidence_multiplier": confidence_multiplier,
            "suggestions": suggestions
        }
    
    def _validate_data_quality(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate data quality metrics"""
        issues = []
        confidence_multiplier = 1.0
        
        if not results:
            return {"issues": issues, "confidence_multiplier": confidence_multiplier}
        
        # Check for null/missing values
        total_fields = 0
        null_fields = 0
        
        for result in results:
            for key, value in result.items():
                total_fields += 1
                if value is None or value == "" or (isinstance(value, str) and value.strip() == ""):
                    null_fields += 1
        
        null_percentage = null_fields / total_fields if total_fields > 0 else 0
        
        if null_percentage > 0.05:  # More than 5% null values
            issues.append({
                "type": "data_quality",
                "severity": "warning",
                "message": f"High percentage of missing data: {null_percentage:.1%}",
                "null_percentage": null_percentage
            })
            confidence_multiplier *= (1 - null_percentage)
        
        # Check for data consistency
        numeric_fields = {}
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)):
                    if key not in numeric_fields:
                        numeric_fields[key] = []
                    numeric_fields[key].append(value)
        
        # Validate numeric field consistency
        for field, values in numeric_fields.items():
            if len(values) > 1:
                mean_val = statistics.mean(values)
                if mean_val > 0:  # Avoid division by zero
                    for value in values:
                        deviation = abs(value - mean_val) / mean_val
                        if deviation > 3.0:  # More than 300% deviation
                            issues.append({
                                "type": "data_inconsistency",
                                "severity": "warning",
                                "message": f"Outlier detected in {field}: {value} (mean: {mean_val:.0f})",
                                "field": field,
                                "value": value,
                                "deviation": deviation
                            })
                            confidence_multiplier *= 0.9
        
        return {"issues": issues, "confidence_multiplier": confidence_multiplier}
    
    def _validate_reasonableness(self, question: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate result reasonableness"""
        issues = []
        confidence_multiplier = 1.0
        
        # Check for suspiciously round numbers (might indicate estimates)
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)) and value > 100:
                    # Check if number is suspiciously round
                    if value % 1000 == 0 and value > 10000:
                        issues.append({
                            "type": "suspicious_rounding",
                            "severity": "info",
                            "message": f"Suspiciously round number: {value} - might be estimated",
                            "field": key,
                            "value": value
                        })
                        confidence_multiplier *= 0.95
        
        # Check for negative values where they shouldn't exist
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)) and value < 0:
                    key_lower = key.lower()
                    if any(word in key_lower for word in ["aantal", "count", "machines", "kranen"]):
                        issues.append({
                            "type": "impossible_value",
                            "severity": "error",
                            "message": f"Negative count value: {value} for {key}",
                            "field": key,
                            "value": value
                        })
                        confidence_multiplier *= 0.3
        
        return {"issues": issues, "confidence_multiplier": confidence_multiplier}
    
    def _validate_patterns(self, question: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate against known patterns"""
        issues = []
        confidence_multiplier = 1.0
        
        # Time series pattern validation
        if len(results) > 1:
            # Check for time-based results
            time_fields = []
            for result in results:
                for key in result.keys():
                    if any(word in key.lower() for word in ["jaar", "maand", "dag", "year", "month", "day"]):
                        time_fields.append(key)
                        break
            
            if time_fields:
                # Validate chronological order
                time_values = []
                for result in results:
                    for time_field in time_fields:
                        if time_field in result:
                            time_values.append(result[time_field])
                            break
                
                if len(time_values) > 1:
                    sorted_times = sorted(time_values)
                    if time_values != sorted_times:
                        issues.append({
                            "type": "chronological_order",
                            "severity": "info",
                            "message": "Results are not in chronological order",
                            "suggestion": "Results should be sorted by time period"
                        })
                        confidence_multiplier *= 0.95
        
        return {"issues": issues, "confidence_multiplier": confidence_multiplier}
    
    def _validate_cross_references(self, question: str, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate cross-references and relationships"""
        issues = []
        confidence_multiplier = 1.0
        
        # Machine-revenue relationship validation
        if any(word in question.lower() for word in ["omzet", "revenue"]) and \
           any(word in question.lower() for word in ["machines", "kranen"]):
            
            # Look for both machine counts and revenue in results
            machine_count = None
            revenue_amount = None
            
            for result in results:
                for key, value in result.items():
                    if isinstance(value, (int, float)):
                        key_lower = key.lower()
                        if any(word in key_lower for word in ["aantal", "count"]) and \
                           any(word in key_lower for word in ["machine", "kraan"]):
                            machine_count = value
                        elif any(word in key_lower for word in ["omzet", "amount", "revenue"]):
                            revenue_amount = value
            
            # Validate revenue per machine ratio
            if machine_count and revenue_amount and machine_count > 0:
                revenue_per_machine = revenue_amount / machine_count
                
                if revenue_per_machine < 50000:  # Less than €50k per machine
                    issues.append({
                        "type": "cross_reference_validation",
                        "severity": "warning",
                        "message": f"Revenue per machine (€{revenue_per_machine:,.0f}) is below expected minimum",
                        "revenue_per_machine": revenue_per_machine,
                        "expected_minimum": 50000
                    })
                    confidence_multiplier *= 0.8
                
                if revenue_per_machine > 500000:  # More than €500k per machine
                    issues.append({
                        "type": "cross_reference_validation",
                        "severity": "warning",
                        "message": f"Revenue per machine (€{revenue_per_machine:,.0f}) is above expected maximum",
                        "revenue_per_machine": revenue_per_machine,
                        "expected_maximum": 500000
                    })
                    confidence_multiplier *= 0.8
        
        return {"issues": issues, "confidence_multiplier": confidence_multiplier}
    
    def generate_accuracy_report(self, validation_result: ValidationResult, question: str) -> str:
        """Generate human-readable accuracy report"""
        
        if validation_result.confidence_score >= 0.9:
            confidence_text = "🟢 **Hoge betrouwbaarheid**"
        elif validation_result.confidence_score >= 0.7:
            confidence_text = "🟡 **Gemiddelde betrouwbaarheid**"
        else:
            confidence_text = "🔴 **Lage betrouwbaarheid**"
        
        report = f"""
{confidence_text} ({validation_result.confidence_score:.1%})

**Validatie Resultaat:**
• Geldig: {'✅ Ja' if validation_result.is_valid else '❌ Nee'}
• Betrouwbaarheid: {validation_result.confidence_score:.1%}
• Problemen gevonden: {len(validation_result.issues_found)}
"""
        
        if validation_result.issues_found:
            report += "\n**Gedetecteerde Problemen:**\n"
            for issue in validation_result.issues_found[:3]:  # Show top 3 issues
                severity_icon = "🔴" if issue.get("severity") == "error" else "🟡" if issue.get("severity") == "warning" else "ℹ️"
                report += f"• {severity_icon} {issue.get('message', 'Onbekend probleem')}\n"
        
        if validation_result.suggestions:
            report += "\n**Aanbevelingen:**\n"
            for suggestion in validation_result.suggestions[:2]:  # Show top 2 suggestions
                report += f"• {suggestion}\n"
        
        return report.strip()
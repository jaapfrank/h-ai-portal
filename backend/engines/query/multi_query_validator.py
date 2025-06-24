#!/usr/bin/env python3
"""
Multi-Query Cross-Validation System for Hoeflon AI
Runs multiple alternative queries to verify and cross-validate results for maximum accuracy
"""

import re
import json
import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
import statistics
import logging

@dataclass
class AlternativeQuery:
    """Represents an alternative query for cross-validation"""
    name: str
    sql_query: str
    description: str
    validation_type: str  # 'exact_match', 'approximate_match', 'range_check', 'pattern_match'
    tolerance: float = 0.05  # 5% tolerance for approximate matches
    weight: float = 1.0  # Weight for confidence calculation

@dataclass
class CrossValidationResult:
    """Result of cross-validation across multiple queries"""
    is_consistent: bool
    confidence_score: float
    primary_result: Any
    alternative_results: List[Dict[str, Any]]
    discrepancies: List[Dict[str, Any]]
    recommendations: List[str]

class MultiQueryValidator:
    """Cross-validates results using multiple query approaches"""
    
    def __init__(self, execute_query_func: Callable):
        self.execute_query = execute_query_func
        self.logger = logging.getLogger(__name__)
        self.alternative_queries = self._define_alternative_queries()
        
    def _define_alternative_queries(self) -> Dict[str, List[AlternativeQuery]]:
        """Define alternative queries for cross-validation"""
        return {
            # C6 vs Total Crane Cross-Validation (CRITICAL FIX)
            "c6_vs_total_validation": [
                AlternativeQuery(
                    name="c6_via_serienummers",
                    sql_query="SELECT COUNT(*) as C6_Count FROM U_SERIENUMMERSHOEFLON s JOIN R_ITEM i ON s.FK_ITEMNR = i.PK_R_ITEM WHERE i.DESCRIPTION LIKE '%C6%' AND s.STATE = 2 AND YEAR(s.DATECHANGED) = YEAR(GETDATE())",
                    description="C6 machines dit jaar via SerieNummers",
                    validation_type="consistency_check",
                    tolerance=0.0,  # No tolerance for logical inconsistencies
                    weight=1.0
                ),
                AlternativeQuery(
                    name="total_cranes_via_serviceobject", 
                    sql_query="SELECT COUNT(*) as Total_Cranes FROM V_R_SERVICEOBJECT so WHERE so.FK_SERVICEOBJECTTYPE IN (10,6,15,12,29) AND YEAR(so.DATUMGEREED) = YEAR(GETDATE()) AND so.DATUMGEREED IS NOT NULL AND so.PRODUCTIESTATUS IN (5,6) AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)",
                    description="Totale kranen dit jaar via ServiceObject (exact matching met primary query)",
                    validation_type="exact_match", 
                    tolerance=0.0,
                    weight=1.0
                ),
                AlternativeQuery(
                    name="c6_via_serviceobject",
                    sql_query="SELECT COUNT(*) as C6_ServiceObject FROM V_R_SERVICEOBJECT so WHERE so.FK_SERVICEOBJECTTYPE = 10 AND YEAR(so.DATUMGEREED) = YEAR(GETDATE()) AND so.DATUMGEREED IS NOT NULL AND so.PRODUCTIESTATUS IN (5,6) AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)",
                    description="C6 machines dit jaar via ServiceObject (Type 10, Status 5+6)",
                    validation_type="consistency_check",
                    tolerance=0.10,  # 10% tolerance for different data sources
                    weight=0.8
                )
            ],
            
            # Machine production cross-validation
            "machine_production": [
                AlternativeQuery(
                    name="production_via_different_status",
                    sql_query="""
                        SELECT COUNT(*) as AantalMachines 
                        FROM V_R_SERVICEOBJECT so
                        WHERE so.FK_SERVICEOBJECTTYPE IN (10,6,15,12,29)
                        AND YEAR(so.DATUMGEREED) = YEAR(GETDATE())
                        AND so.DATUMGEREED IS NOT NULL
                        AND so.PRODUCTIESTATUS IN (4,5,6,7)
                        AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                    """,
                    description="Count cranes with broader status range (4-7 vs 5-6)",
                    validation_type="approximate_match",
                    tolerance=0.15
                ),
                AlternativeQuery(
                    name="production_via_serviceobject",
                    sql_query="""
                        SELECT COUNT(*) as AantalMachines
                        FROM V_R_SERVICEOBJECT so
                        WHERE so.FK_SERVICEOBJECTTYPE IN (10,6,15,12,29)
                        AND YEAR(so.DATUMGEREED) = YEAR(GETDATE())
                        AND so.DATUMGEREED IS NOT NULL
                        AND so.PRODUCTIESTATUS IN (5,6)
                        AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                    """,
                    description="Count machines via service objects (exact match)",
                    validation_type="exact_match",
                    tolerance=0.0
                )
            ],
            
            # Revenue cross-validation
            "revenue_validation": [
                AlternativeQuery(
                    name="revenue_via_invoices",
                    sql_query="""
                        SELECT SUM(TOTALAMOUNT) as TotaleOmzet
                        FROM R_SALESINVOICE si
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                        AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                        AND si.TOTALAMOUNT > 0
                    """,
                    description="Revenue via sales invoices",
                    validation_type="exact_match",
                    tolerance=0.02
                ),
                AlternativeQuery(
                    name="revenue_via_order_confirmation",
                    sql_query="""
                        SELECT SUM(sil.LINETOTAL) as TotaleOmzet
                        FROM R_SALESINVOICEDETAILITEM sil
                        JOIN R_SALESINVOICE si ON sil.FK_SALESINVOICE = si.PK_R_SALESINVOICE
                        WHERE YEAR(si.INVOICEDATE) = YEAR(GETDATE())
                        AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                        AND sil.LINETOTAL > 0
                    """,
                    description="Revenue via invoice line items",
                    validation_type="approximate_match",
                    tolerance=0.05
                )
            ],
            
            # Machine count validation
            "machine_counts": [
                AlternativeQuery(
                    name="c6_count_via_description",
                    sql_query="""
                        SELECT COUNT(*) as C6Count
                        FROM U_SERIENUMMERSHOEFLON s 
                        JOIN R_ITEM i ON s.FK_ITEMNR = i.PK_R_ITEM 
                        WHERE i.DESCRIPTION LIKE '%C6%'
                    """,
                    description="C6 count via item descriptions",
                    validation_type="exact_match",
                    weight=1.5
                ),
                AlternativeQuery(
                    name="total_machines_alternative",
                    sql_query="""
                        SELECT COUNT(*) as TotalMachines
                        FROM U_SERIENUMMERSHOEFLON
                        WHERE FK_ITEMNR IS NOT NULL
                    """,
                    description="Total machines alternative count",
                    validation_type="exact_match",
                    weight=1.0
                )
            ],
            
            # Time-based validation
            "monthly_comparison": [
                AlternativeQuery(
                    name="monthly_via_datepart",
                    sql_query="""
                        SELECT 
                            DATEPART(YEAR, so.DELIVERYDATE) as Jaar,
                            DATEPART(MONTH, so.DELIVERYDATE) as Maand,
                            COUNT(*) as Aantal
                        FROM R_SERVICEOBJECT so
                        WHERE so.FK_SERVICEOBJECTTYPE IN (6,9,10,12,15)
                        AND YEAR(so.DELIVERYDATE) IN (YEAR(GETDATE()), YEAR(GETDATE())-1)
                        AND so.DELIVERYDATE IS NOT NULL
                        AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                        GROUP BY DATEPART(YEAR, so.DELIVERYDATE), DATEPART(MONTH, so.DELIVERYDATE)
                        ORDER BY Jaar, Maand
                    """,
                    description="Monthly data via DATEPART function",
                    validation_type="pattern_match",
                    tolerance=0.1
                )
            ]
        }
    
    def cross_validate_result(self, question: str, original_query: str, 
                            original_results: List[Dict[str, Any]]) -> CrossValidationResult:
        """Cross-validate results using alternative queries"""
        
        # Determine validation category based on question
        validation_category = self._categorize_question(question)
        
        if validation_category not in self.alternative_queries:
            # No alternative queries available
            return CrossValidationResult(
                is_consistent=True,
                confidence_score=0.8,  # Medium confidence without cross-validation
                primary_result=original_results,
                alternative_results=[],
                discrepancies=[],
                recommendations=["No alternative validation queries available for this question type"]
            )
        
        alternative_results = []
        discrepancies = []
        consistency_scores = []
        
        # Execute alternative queries
        for alt_query in self.alternative_queries[validation_category]:
            try:
                # Adapt query for specific time periods if needed
                adapted_query = self._adapt_query_for_context(alt_query.sql_query, question)
                
                alt_result = self.execute_query(adapted_query, f"Cross-validation: {alt_query.name}")
                
                alternative_results.append({
                    "name": alt_query.name,
                    "description": alt_query.description,
                    "results": alt_result,
                    "query": adapted_query
                })
                
                # Compare with original results
                consistency = self._compare_results(
                    original_results, alt_result, alt_query.validation_type, alt_query.tolerance
                )
                
                consistency_scores.append(consistency["score"] * alt_query.weight)
                
                if not consistency["is_consistent"]:
                    discrepancies.append({
                        "alternative_query": alt_query.name,
                        "description": alt_query.description,
                        "discrepancy": consistency["discrepancy"],
                        "severity": consistency["severity"]
                    })
                
            except Exception as e:
                self.logger.warning(f"Failed to execute alternative query {alt_query.name}: {e}")
                alternative_results.append({
                    "name": alt_query.name,
                    "description": alt_query.description,
                    "error": str(e),
                    "query": alt_query.sql_query
                })
        
        # Calculate overall consistency and confidence
        if consistency_scores:
            avg_consistency = statistics.mean(consistency_scores)
            is_consistent = avg_consistency > 0.8
            confidence_score = min(0.95, max(0.5, avg_consistency))
        else:
            is_consistent = True  # No alternative queries succeeded
            confidence_score = 0.7  # Medium confidence
        
        # Generate recommendations
        recommendations = self._generate_validation_recommendations(
            discrepancies, consistency_scores, validation_category
        )
        
        return CrossValidationResult(
            is_consistent=is_consistent,
            confidence_score=confidence_score,
            primary_result=original_results,
            alternative_results=alternative_results,
            discrepancies=discrepancies,
            recommendations=recommendations
        )
    
    def _categorize_question(self, question: str) -> str:
        """Categorize question to determine appropriate validation queries"""
        question_lower = question.lower()
        
        # C6 vs Total validation (PRIORITY: Check for inconsistencies)
        if "c6" in question_lower and any(word in question_lower for word in ["machines", "kranen", "geproduceerd", "gebouwd", "dit jaar"]):
            return "c6_vs_total_validation"
        elif any(word in question_lower for word in ["omzet", "revenue", "verkocht", "factuur"]):
            return "revenue_validation"
        elif any(word in question_lower for word in ["machines", "kranen", "productie", "geproduceerd"]):
            if any(word in question_lower for word in ["c6", "c30"]):
                return "machine_counts"
            elif any(word in question_lower for word in ["maand", "month", "vergelijk", "vs"]):
                return "monthly_comparison"
            else:
                return "machine_production"
        elif any(word in question_lower for word in ["aantal", "count", "hoeveel"]):
            return "machine_counts"
        else:
            return "general"  # No specific validation category
    
    def _adapt_query_for_context(self, query: str, question: str) -> str:
        """Adapt alternative query based on question context"""
        question_lower = question.lower()
        
        # Adapt for specific time periods
        if "vorig jaar" in question_lower or "2024" in question_lower:
            query = query.replace("YEAR(GETDATE())", "2024")
        elif "deze maand" in question_lower:
            query = query.replace(
                "YEAR(si.INVOICEDATE) = YEAR(GETDATE())",
                "YEAR(si.INVOICEDATE) = YEAR(GETDATE()) AND MONTH(si.INVOICEDATE) = MONTH(GETDATE())"
            )
        elif "afgelopen maand" in question_lower:
            query = query.replace(
                "YEAR(si.INVOICEDATE) = YEAR(GETDATE())",
                "YEAR(si.INVOICEDATE) = YEAR(DATEADD(MONTH, -1, GETDATE())) AND MONTH(si.INVOICEDATE) = MONTH(DATEADD(MONTH, -1, GETDATE()))"
            )
        
        # Adapt for specific machine types
        if "c6" in question_lower and "WHERE" in query.upper():
            if "R_ITEM" in query.upper() or "DESCRIPTION" in query.upper():
                # Already has item filtering
                pass
            else:
                # Add C6 filtering
                query = query.replace(
                    "FROM U_SERIENUMMERSHOEFLON",
                    "FROM U_SERIENUMMERSHOEFLON s JOIN R_ITEM i ON s.FK_ITEMNR = i.PK_R_ITEM"
                )
                query = query.replace(
                    "WHERE",
                    "WHERE i.DESCRIPTION LIKE '%C6%' AND"
                )
        
        return query
    
    def _compare_results(self, original: List[Dict[str, Any]], alternative: List[Dict[str, Any]], 
                        validation_type: str, tolerance: float) -> Dict[str, Any]:
        """Compare original and alternative results"""
        
        if not original or not alternative:
            return {
                "is_consistent": False,
                "score": 0.0,
                "discrepancy": "One or both result sets are empty",
                "severity": "high"
            }
        
        if validation_type == "exact_match":
            return self._exact_match_comparison(original, alternative, tolerance)
        elif validation_type == "approximate_match":
            return self._approximate_match_comparison(original, alternative, tolerance)
        elif validation_type == "range_check":
            return self._range_check_comparison(original, alternative, tolerance)
        elif validation_type == "pattern_match":
            return self._pattern_match_comparison(original, alternative, tolerance)
        elif validation_type == "consistency_check":
            return self._consistency_check_comparison(original, alternative, tolerance)
        else:
            return {"is_consistent": True, "score": 0.8, "discrepancy": None, "severity": "low"}
    
    def _exact_match_comparison(self, original: List[Dict[str, Any]], 
                              alternative: List[Dict[str, Any]], tolerance: float) -> Dict[str, Any]:
        """Compare for exact or near-exact matches"""
        
        # Extract primary numeric values
        orig_values = self._extract_numeric_values(original)
        alt_values = self._extract_numeric_values(alternative)
        
        if not orig_values or not alt_values:
            return {"is_consistent": False, "score": 0.0, "discrepancy": "No numeric values to compare", "severity": "medium"}
        
        # Compare primary values
        orig_primary = orig_values[0] if orig_values else 0
        alt_primary = alt_values[0] if alt_values else 0
        
        if orig_primary == 0 and alt_primary == 0:
            return {"is_consistent": True, "score": 1.0, "discrepancy": None, "severity": "low"}
        
        if orig_primary == 0 or alt_primary == 0:
            return {"is_consistent": False, "score": 0.0, "discrepancy": f"One value is zero: {orig_primary} vs {alt_primary}", "severity": "high"}
        
        difference = abs(orig_primary - alt_primary) / max(orig_primary, alt_primary)
        
        if difference <= tolerance:
            return {"is_consistent": True, "score": 1.0 - difference, "discrepancy": None, "severity": "low"}
        else:
            return {
                "is_consistent": False,
                "score": max(0.0, 1.0 - difference),
                "discrepancy": f"Values differ by {difference:.1%}: {orig_primary:,.0f} vs {alt_primary:,.0f}",
                "severity": "high" if difference > 0.2 else "medium"
            }
    
    def _approximate_match_comparison(self, original: List[Dict[str, Any]], 
                                    alternative: List[Dict[str, Any]], tolerance: float) -> Dict[str, Any]:
        """Compare allowing for reasonable approximation"""
        
        orig_values = self._extract_numeric_values(original)
        alt_values = self._extract_numeric_values(alternative)
        
        if not orig_values or not alt_values:
            return {"is_consistent": False, "score": 0.0, "discrepancy": "No numeric values to compare", "severity": "medium"}
        
        # Use broader tolerance for approximate matching
        adjusted_tolerance = max(tolerance, 0.1)  # At least 10% tolerance
        
        return self._exact_match_comparison(original, alternative, adjusted_tolerance)
    
    def _pattern_match_comparison(self, original: List[Dict[str, Any]], 
                                alternative: List[Dict[str, Any]], tolerance: float) -> Dict[str, Any]:
        """Compare patterns in time series or multi-row data"""
        
        if len(original) != len(alternative):
            return {
                "is_consistent": False,
                "score": 0.5,
                "discrepancy": f"Different row counts: {len(original)} vs {len(alternative)}",
                "severity": "medium"
            }
        
        # Compare patterns in the data
        orig_values = self._extract_numeric_values(original)
        alt_values = self._extract_numeric_values(alternative)
        
        if len(orig_values) != len(alt_values):
            return {"is_consistent": False, "score": 0.3, "discrepancy": "Different value counts", "severity": "medium"}
        
        # Calculate correlation or pattern similarity
        differences = []
        for i in range(len(orig_values)):
            if orig_values[i] > 0 and alt_values[i] > 0:
                diff = abs(orig_values[i] - alt_values[i]) / max(orig_values[i], alt_values[i])
                differences.append(diff)
        
        if differences:
            avg_difference = statistics.mean(differences)
            is_consistent = avg_difference <= tolerance
            score = max(0.0, 1.0 - avg_difference)
            
            return {
                "is_consistent": is_consistent,
                "score": score,
                "discrepancy": f"Average pattern difference: {avg_difference:.1%}" if not is_consistent else None,
                "severity": "high" if avg_difference > 0.3 else "medium"
            }
        
        return {"is_consistent": True, "score": 0.8, "discrepancy": None, "severity": "low"}
    
    def _range_check_comparison(self, original: List[Dict[str, Any]], 
                              alternative: List[Dict[str, Any]], tolerance: float) -> Dict[str, Any]:
        """Check if values fall within expected ranges"""
        
        orig_values = self._extract_numeric_values(original)
        alt_values = self._extract_numeric_values(alternative)
        
        # Check if all values are within reasonable ranges of each other
        in_range_count = 0
        total_comparisons = 0
        
        for orig_val in orig_values:
            for alt_val in alt_values:
                total_comparisons += 1
                if orig_val > 0 and alt_val > 0:
                    ratio = min(orig_val, alt_val) / max(orig_val, alt_val)
                    if ratio >= (1 - tolerance):
                        in_range_count += 1
        
        if total_comparisons == 0:
            return {"is_consistent": True, "score": 0.8, "discrepancy": None, "severity": "low"}
        
        consistency_ratio = in_range_count / total_comparisons
        is_consistent = consistency_ratio >= 0.7
        
        return {
            "is_consistent": is_consistent,
            "score": consistency_ratio,
            "discrepancy": f"Only {consistency_ratio:.1%} of values within range" if not is_consistent else None,
            "severity": "high" if consistency_ratio < 0.5 else "medium"
        }
    
    def _consistency_check_comparison(self, original: List[Dict[str, Any]], 
                                    alternative: List[Dict[str, Any]], tolerance: float) -> Dict[str, Any]:
        """Check logical consistency between related queries (e.g., C6 vs Total)"""
        
        orig_values = self._extract_numeric_values(original)
        alt_values = self._extract_numeric_values(alternative)
        
        if not orig_values or not alt_values:
            return {"is_consistent": False, "score": 0.0, "discrepancy": "No numeric values to compare", "severity": "medium"}
        
        orig_primary = orig_values[0] if orig_values else 0
        alt_primary = alt_values[0] if alt_values else 0
        
        # Special logic for C6 vs Total validation
        # C6 count should never exceed total crane count
        if orig_primary > alt_primary:
            # This is a logical inconsistency - subset cannot be larger than total
            excess_percentage = ((orig_primary - alt_primary) / alt_primary) * 100 if alt_primary > 0 else float('inf')
            
            return {
                "is_consistent": False,
                "score": 0.1,  # Very low confidence for logical inconsistencies
                "discrepancy": f"🚨 LOGICAL INCONSISTENCY: C6 count ({orig_primary:,.0f}) exceeds total crane count ({alt_primary:,.0f}) by {excess_percentage:.0f}%",
                "severity": "critical",
                "inconsistency_type": "subset_exceeds_total",
                "recommendation": "Check if C6 query uses wrong table or missing date filters"
            }
        
        # Check if values are reasonably close
        if alt_primary > 0:
            ratio = orig_primary / alt_primary
            if ratio > 0.8:  # C6 is more than 80% of total - suspicious
                return {
                    "is_consistent": False,
                    "score": 0.3,
                    "discrepancy": f"⚠️ C6 count ({orig_primary:,.0f}) is {ratio:.1%} of total ({alt_primary:,.0f}) - unusually high proportion",
                    "severity": "high",
                    "inconsistency_type": "suspicious_ratio"
                }
            elif ratio <= 0.5:  # C6 is reasonable proportion of total
                return {
                    "is_consistent": True,
                    "score": 0.9,
                    "discrepancy": None,
                    "severity": "low"
                }
        
        # Default consistency check
        return self._exact_match_comparison(original, alternative, tolerance)
    
    def _extract_numeric_values(self, results: List[Dict[str, Any]]) -> List[float]:
        """Extract numeric values from results"""
        values = []
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    values.append(float(value))
        return values
    
    def _generate_validation_recommendations(self, discrepancies: List[Dict[str, Any]], 
                                           consistency_scores: List[float], 
                                           validation_category: str) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if discrepancies:
            high_severity_count = len([d for d in discrepancies if d.get("severity") == "high"])
            
            if high_severity_count > 0:
                recommendations.append("⚠️ Significante afwijkingen gedetecteerd - controleer data kwaliteit")
            
            if len(discrepancies) > 1:
                recommendations.append("🔍 Meerdere validatie checks faalden - mogelijke data inconsistentie")
        
        if consistency_scores:
            avg_score = statistics.mean(consistency_scores)
            if avg_score < 0.7:
                recommendations.append("📊 Lage consistentie tussen data bronnen - verifieer query logica")
            elif avg_score < 0.9:
                recommendations.append("✓ Redelijke consistentie - kleine afwijkingen gedetecteerd")
        
        # Category-specific recommendations
        if validation_category == "revenue_validation":
            recommendations.append("💰 Voor financiële data: controleer of alle externe verkopen zijn meegenomen")
        elif validation_category == "machine_production":
            recommendations.append("🏭 Voor productie data: verifieer of gereed-gemelde machines correct zijn geteld")
        elif validation_category == "machine_counts":
            recommendations.append("🔢 Voor machine aantallen: controleer of serienummer data up-to-date is")
        
        if not recommendations:
            recommendations.append("✅ Cross-validatie succesvol - resultaten zijn betrouwbaar")
        
        return recommendations
    
    def generate_cross_validation_report(self, validation_result: CrossValidationResult) -> str:
        """Generate human-readable cross-validation report"""
        
        confidence_text = "🟢 Hoog" if validation_result.confidence_score >= 0.9 else \
                         "🟡 Gemiddeld" if validation_result.confidence_score >= 0.7 else "🔴 Laag"
        
        report = f"""
**Cross-Validatie Resultaat:**
• Consistentie: {'✅ Consistent' if validation_result.is_consistent else '❌ Inconsistent'}
• Betrouwbaarheid: {confidence_text} ({validation_result.confidence_score:.1%})
• Alternatieve queries uitgevoerd: {len(validation_result.alternative_results)}
• Afwijkingen gevonden: {len(validation_result.discrepancies)}
"""
        
        if validation_result.discrepancies:
            report += "\n**Gevonden Afwijkingen:**\n"
            for discrepancy in validation_result.discrepancies[:2]:  # Show top 2
                severity_icon = "🔴" if discrepancy.get("severity") == "high" else "🟡"
                report += f"• {severity_icon} {discrepancy.get('description', '')}: {discrepancy.get('discrepancy', '')}\n"
        
        if validation_result.recommendations:
            report += "\n**Aanbevelingen:**\n"
            for rec in validation_result.recommendations[:2]:  # Show top 2
                report += f"• {rec}\n"
        
        return report.strip()
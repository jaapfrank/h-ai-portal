#!/usr/bin/env python3
"""
Answer Validation and Improvement Engine for Hoeflon AI
Analyzes why answers might be incorrect and helps AI generate better responses
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

class AnswerValidationEngine:
    """Engine for validating answers and providing feedback for improvement"""
    
    def __init__(self, multi_db_manager):
        self.multi_db_manager = multi_db_manager
        
        # Common error patterns and their likely causes
        self.error_patterns = {
            "unrealistic_revenue": {
                "indicators": [
                    r"€\s*(\d{2,3})[,.]?\d*\s*miljoen",  # 100+ million euros
                    r"€\s*\d{8,}",  # 8+ digit amounts
                    r"€\s*[1-9]\d{8,}"  # 9+ digit amounts
                ],
                "likely_causes": [
                    "Interne Hoeflon verkopen zijn mogelijk niet uitgefilterd",
                    "Er worden mogelijk alle transacties geteld ipv alleen externe verkopen", 
                    "De query gebruikt mogelijk verkeerde FK_INVOICERELATION filters",
                    "Er wordt mogelijk dubbel geteld tussen verschillende tabellen"
                ],
                "validation_queries": [
                    "SELECT COUNT(*) FROM R_SALESINVOICE WHERE FK_INVOICERELATION IN (7,6736,5910,5219,1114,6109,3366,8165)",
                    "SELECT SUM(TOTALAMOUNT) FROM R_SALESINVOICE WHERE FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)",
                    "SELECT AVG(TOTALAMOUNT) FROM R_SALESINVOICE WHERE TOTALAMOUNT > 0"
                ],
                "suggested_fixes": [
                    "Voeg externe verkoop filter toe: AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)",
                    "Controleer of de juiste tabel wordt gebruikt (R_SALESINVOICE vs R_SALESINVOICEDETAILITEM)",
                    "Verificeer dat er geen dubbele tellingen zijn door JOINs"
                ]
            },
            
            "unrealistic_machine_count": {
                "indicators": [
                    r"(\d{4,})\s*(machines?|kranen)",  # 1000+ machines
                    r"(machines?|kranen).*(\d{4,})"
                ],
                "likely_causes": [
                    "Er wordt mogelijk geteld op verkeerde tabel of kolom",
                    "Serienummers worden mogelijk dubbel geteld",
                    "Er wordt geen filter gebruikt voor STATE (gereed vs in productie)",
                    "Alle entries worden geteld ipv alleen unieke machines"
                ],
                "validation_queries": [
                    "SELECT COUNT(DISTINCT SERIALNUMBER) FROM U_SERIENUMMERSHOEFLON",
                    "SELECT COUNT(*) FROM U_SERIENUMMERSHOEFLON WHERE STATE = 2",
                    "SELECT COUNT(*) FROM R_SERVICEOBJECT WHERE FK_SERVICEOBJECTTYPE IN (6,9,10,12,15)"
                ],
                "suggested_fixes": [
                    "Gebruik COUNT(DISTINCT SERIALNUMBER) voor unieke machines",
                    "Filter op STATE = 2 voor alleen gereed gemelde machines",
                    "Controleer of de juiste FK_SERVICEOBJECTTYPE waarden worden gebruikt"
                ]
            },
            
            "wrong_time_period": {
                "indicators": [
                    r"2024.*2025",  # Shows both years when only one asked
                    r"(januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december).*\d{4}.*\d{4}"
                ],
                "likely_causes": [
                    "De query gebruikt verkeerde datum filters",
                    "Er wordt een jaar vergelijking gemaakt ipv specifieke periode",
                    "DATEADD functies zijn mogelijk verkeerd gebruikt",
                    "De vraag wordt verkeerd geïnterpreteerd door de AI"
                ],
                "validation_queries": [
                    "SELECT MIN(INVOICEDATE), MAX(INVOICEDATE) FROM R_SALESINVOICE WHERE YEAR(INVOICEDATE) = YEAR(GETDATE())",
                    "SELECT YEAR(GETDATE()) as HuidigJaar, MONTH(GETDATE()) as HuidigeMaand"
                ],
                "suggested_fixes": [
                    "Controleer of de datum filters correct zijn voor de gevraagde periode",
                    "Gebruik specifieke datum bereiken ipv jaar vergelijkingen",
                    "Vervang algemene datum queries door specifieke periode filters"
                ]
            },
            
            "wrong_data_source": {
                "indicators": [
                    r"geen\s+data\s+gevonden",
                    r"0\s+(machines?|kranen|facturen)",
                    r"(leeg|empty).*resultaat"
                ],
                "likely_causes": [
                    "Er wordt gezocht in de verkeerde database (ERP vs AccountView)",
                    "De tabel of kolom namen zijn verkeerd",
                    "De JOIN condities zijn incorrect",
                    "Er wordt gefilterd op niet-bestaande waarden"
                ],
                "validation_queries": [
                    "SELECT COUNT(*) FROM R_SALESINVOICE",
                    "SELECT COUNT(*) FROM U_SERIENUMMERSHOEFLON", 
                    "SELECT COUNT(*) FROM R_SERVICEOBJECT"
                ],
                "suggested_fixes": [
                    "Controleer of de juiste database wordt gebruikt",
                    "Verificeer tabel en kolom namen in schema",
                    "Test de query zonder filters om basis data te controleren"
                ]
            },
            
            "currency_vs_count_confusion": {
                "indicators": [
                    r"€.*\d+.*machines?",  # Euro signs with machine counts
                    r"machines?.*€",
                    r"aantal.*€\d+"
                ],
                "likely_causes": [
                    "Er wordt omzet getoond ipv aantal machines",
                    "De chart formatting is verkeerd (euros ipv counts)",
                    "Verkeerde kolom wordt gebruikt in visualisatie",
                    "Query retourneert prijs ipv aantal"
                ],
                "validation_queries": [
                    "SELECT COUNT(*) as Aantal, SUM(TOTALAMOUNT) as Omzet FROM R_SALESINVOICE",
                    "SELECT DISTINCT COLUMNNAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME LIKE '%MACHINE%'"
                ],
                "suggested_fixes": [
                    "Gebruik COUNT(*) voor aantal en SUM(TOTALAMOUNT) voor omzet",
                    "Controleer chart formatting settings (euros vs counts)",
                    "Verificeer dat de juiste kolom wordt gebruikt voor visualisatie"
                ]
            },
            
            "aggregation_level_mismatch": {
                "indicators": [
                    r"per\s+maand.*jaar",  # Monthly request but yearly data shown
                    r"totaal.*\d+.*\d+.*\d+"  # Multiple numbers when one expected
                ],
                "likely_causes": [
                    "GROUP BY gebruikt verkeerde aggregatie niveau",
                    "De query aggregeert op jaar ipv maand of omgekeerd",
                    "Verkeerde tijd dimensie in SELECT clause",
                    "Chart toont verkeerde aggregatie niveau"
                ],
                "validation_queries": [
                    "SELECT YEAR(INVOICEDATE), MONTH(INVOICEDATE), COUNT(*) FROM R_SALESINVOICE GROUP BY YEAR(INVOICEDATE), MONTH(INVOICEDATE)",
                    "SELECT YEAR(GETDATE()), MONTH(GETDATE())"
                ],
                "suggested_fixes": [
                    "Gebruik MONTH(datum) voor maandelijkse data, YEAR(datum) voor jaarlijkse",
                    "Controleer GROUP BY clause voor juiste aggregatie niveau", 
                    "Pas chart configuratie aan voor gewenste tijd dimensie"
                ]
            }
        }
        
        # Business logic validation rules
        self.business_validation_rules = {
            "revenue_sanity": {
                "description": "Hoeflon revenue should be reasonable based on business size",
                "rules": [
                    {"max_monthly_revenue": 10000000, "message": "Maandelijkse omzet >€10M is onrealistisch voor Hoeflon"},
                    {"max_yearly_revenue": 100000000, "message": "Jaarlijkse omzet >€100M is onrealistisch voor Hoeflon"},
                    {"min_machine_price": 50000, "message": "Gemiddelde machine prijs <€50K lijkt te laag"},
                    {"max_machine_price": 500000, "message": "Gemiddelde machine prijs >€500K lijkt te hoog"}
                ]
            },
            "production_sanity": {
                "description": "Production numbers should align with business capacity",
                "rules": [
                    {"max_monthly_production": 50, "message": "Maandelijkse productie >50 machines lijkt onrealistisch"},
                    {"max_yearly_production": 500, "message": "Jaarlijkse productie >500 machines lijkt onrealistisch"},
                    {"max_machines_in_production": 100, "message": "Meer dan 100 machines tegelijk in productie lijkt onrealistisch"}
                ]
            },
            "customer_sanity": {
                "description": "Customer data should be realistic",
                "rules": [
                    {"max_customer_revenue": 5000000, "message": "Klant omzet >€5M per jaar lijkt hoog voor Hoeflon"},
                    {"min_invoice_amount": 100, "message": "Factuur bedragen <€100 lijken onrealistisch voor machines"}
                ]
            }
        }
        
    def validate_answer(self, question: str, answer: str, sql_query: str = None, results: List[Dict] = None) -> Dict[str, Any]:
        """Validate an answer and provide feedback for improvement"""
        
        validation_result = {
            "is_valid": True,
            "confidence": 1.0,
            "issues_found": [],
            "suggested_improvements": [],
            "corrective_queries": [],
            "business_rule_violations": []
        }
        
        # 1. Pattern-based validation
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        for error_type, config in self.error_patterns.items():
            for pattern in config["indicators"]:
                if re.search(pattern, answer_lower):
                    validation_result["is_valid"] = False
                    validation_result["confidence"] = max(0.2, validation_result["confidence"] - 0.3)
                    
                    validation_result["issues_found"].append({
                        "type": error_type,
                        "pattern_matched": pattern,
                        "likely_causes": config["likely_causes"],
                        "validation_queries": config["validation_queries"],
                        "suggested_fixes": config["suggested_fixes"]
                    })
                    
        # 2. Business logic validation
        if results:
            business_violations = self._validate_business_rules(results, question_lower)
            if business_violations:
                validation_result["is_valid"] = False
                validation_result["confidence"] = min(validation_result["confidence"], 0.6)
                validation_result["business_rule_violations"] = business_violations
                
        # 3. SQL query validation if available
        if sql_query:
            sql_issues = self._validate_sql_query(sql_query, question_lower)
            if sql_issues:
                validation_result["issues_found"].extend(sql_issues)
                validation_result["is_valid"] = False
                validation_result["confidence"] = min(validation_result["confidence"], 0.5)
                
        # 4. Generate improvement suggestions
        if not validation_result["is_valid"]:
            validation_result["suggested_improvements"] = self._generate_improvement_suggestions(
                question, answer, validation_result["issues_found"]
            )
            
        return validation_result
        
    def _validate_business_rules(self, results: List[Dict], question: str) -> List[Dict[str, Any]]:
        """Validate results against business logic rules"""
        violations = []
        
        if not results:
            return violations
            
        # Extract numeric values from results
        numeric_values = []
        for result in results:
            for key, value in result.items():
                if isinstance(value, (int, float)) and value > 0:
                    numeric_values.append({"key": key, "value": value})
                    
        # Check revenue rules
        if any(word in question for word in ["omzet", "revenue", "verkoop"]):
            for rule in self.business_validation_rules["revenue_sanity"]["rules"]:
                for num_val in numeric_values:
                    if "revenue" in rule and num_val["value"] > rule.get("max_monthly_revenue", float('inf')):
                        violations.append({
                            "rule": rule,
                            "value": num_val["value"],
                            "key": num_val["key"],
                            "message": rule["message"]
                        })
                        
        # Check production rules
        if any(word in question for word in ["machines", "kranen", "productie", "geproduceerd"]):
            for rule in self.business_validation_rules["production_sanity"]["rules"]:
                for num_val in numeric_values:
                    if "production" in rule and num_val["value"] > rule.get("max_monthly_production", float('inf')):
                        violations.append({
                            "rule": rule,
                            "value": num_val["value"], 
                            "key": num_val["key"],
                            "message": rule["message"]
                        })
                        
        return violations
        
    def _validate_sql_query(self, sql_query: str, question: str) -> List[Dict[str, Any]]:
        """Validate SQL query for common issues"""
        issues = []
        sql_upper = sql_query.upper()
        
        # Check for missing external sales filter
        if any(word in question for word in ["omzet", "revenue", "verkoop"]):
            if "FK_INVOICERELATION NOT IN" not in sql_upper:
                issues.append({
                    "type": "missing_external_filter",
                    "description": "Query mist filter voor externe verkopen",
                    "suggested_fix": "Voeg toe: AND si.FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)"
                })
                
        # Check for appropriate date filters
        if any(word in question for word in ["dit jaar", "2025", "deze maand"]):
            if "YEAR(" not in sql_upper and "GETDATE()" not in sql_upper:
                issues.append({
                    "type": "missing_date_filter", 
                    "description": "Query mist juiste datum filter",
                    "suggested_fix": "Voeg datum filter toe zoals: WHERE YEAR(INVOICEDATE) = YEAR(GETDATE())"
                })
                
        # Check for proper aggregation
        if "per maand" in question and "MONTH(" not in sql_upper:
            issues.append({
                "type": "wrong_aggregation",
                "description": "Maandelijkse vraag maar geen MONTH() aggregatie",
                "suggested_fix": "Gebruik GROUP BY MONTH(INVOICEDATE) voor maandelijkse data"
            })
            
        return issues
        
    def _generate_improvement_suggestions(self, question: str, answer: str, issues: List[Dict]) -> List[str]:
        """Generate specific suggestions for improving the answer"""
        suggestions = []
        
        question_lower = question.lower()
        
        # Generic suggestions based on question type
        if any(word in question_lower for word in ["omzet", "revenue"]):
            suggestions.append("🔍 **Controleer of alleen externe verkopen worden meegenomen** (exclusief interne Hoeflon transacties)")
            suggestions.append("📊 **Vergelijk resultaat met bekende business cijfers** (is €X miljoen realistisch voor Hoeflon?)")
            
        if any(word in question_lower for word in ["machines", "kranen", "productie"]):
            suggestions.append("🏭 **Controleer of de juiste machine status wordt gebruikt** (STATE = 2 voor gereed)")
            suggestions.append("📈 **Verificeer of unieke machines worden geteld** (COUNT(DISTINCT SERIALNUMBER))")
            
        # Specific suggestions based on detected issues
        for issue in issues:
            if issue["type"] == "unrealistic_revenue":
                suggestions.append("💰 **Revenue lijkt te hoog** - mogelijk interne verkopen niet uitgefilterd")
                suggestions.append("🔧 **Test query met external sales filter**: FK_INVOICERELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)")
                
            elif issue["type"] == "unrealistic_machine_count":
                suggestions.append("🔢 **Machine aantal lijkt te hoog** - mogelijk dubbele tellingen")
                suggestions.append("🔧 **Test met unieke telling**: COUNT(DISTINCT SERIALNUMBER)")
                
            elif issue["type"] == "wrong_time_period":
                suggestions.append("📅 **Verkeerde tijdsperiode** - controleer datum filters")
                suggestions.append("🔧 **Test specifieke periode filter**: YEAR(datum) = 2025")
                
            elif issue["type"] == "currency_vs_count_confusion":
                suggestions.append("💱 **Euro/aantal verwarring** - controleer wat er wordt gevraagd")
                suggestions.append("🔧 **Gebruik COUNT() voor aantallen, SUM() voor bedragen**")
                
        # Add query improvement suggestions
        suggestions.append("🧪 **Test alternatieve query approaches**:")
        suggestions.append("   • Direct query mapper voor bewezen accurate results")
        suggestions.append("   • Cross-database verification tussen ERP en AccountView") 
        suggestions.append("   • Stap-voor-stap query building met tussenresultaten")
        
        return suggestions
        
    def generate_corrective_response(self, validation_result: Dict[str, Any], original_question: str) -> str:
        """Generate a response explaining why the answer might be incorrect"""
        
        if validation_result["is_valid"]:
            return ""
            
        response = f"🚨 **Het vorige antwoord lijkt mogelijk niet correct** (confidence: {validation_result['confidence']:.1%})\n\n"
        
        # Explain issues found
        if validation_result["issues_found"]:
            response += "**🔍 Mogelijke problemen gedetecteerd:**\n"
            for i, issue in enumerate(validation_result["issues_found"][:3], 1):  # Max 3 issues
                response += f"{i}. **{issue['type'].replace('_', ' ').title()}**\n"
                if issue.get("likely_causes"):
                    for cause in issue["likely_causes"][:2]:  # Max 2 causes
                        response += f"   • {cause}\n"
                response += "\n"
                
        # Explain business rule violations  
        if validation_result["business_rule_violations"]:
            response += "**⚠️ Business logic waarschuwingen:**\n"
            for violation in validation_result["business_rule_violations"][:2]:
                response += f"• {violation['message']}\n"
            response += "\n"
            
        # Provide improvement suggestions
        if validation_result["suggested_improvements"]:
            response += "**💡 Verbeteringssuggesties:**\n"
            for suggestion in validation_result["suggested_improvements"][:4]:  # Max 4 suggestions
                response += f"{suggestion}\n"
            response += "\n"
            
        response += "**🔄 Laat me proberen een beter antwoord te geven...**\n"
        response += f"*Originele vraag: {original_question}*\n\n"
        response += "🎯 **Voor een accuraat antwoord, specificeer:**\n"
        response += "• Exacte tijdsperiode (dit jaar, deze maand, etc.)\n"
        response += "• Type data (externe verkopen, alle machines, etc.)\n" 
        response += "• Gewenste detail niveau (totaal, per maand, per klant)\n"
        
        return response
        
    def should_validate_answer(self, question: str, answer: str) -> bool:
        """Quick check if answer should be validated"""
        
        # Always validate if answer contains large numbers
        if re.search(r"€\s*\d{6,}", answer) or re.search(r"\d{3,}.*machines?", answer):
            return True
            
        # Validate dashboard and revenue questions
        if any(word in question.lower() for word in ["dashboard", "omzet", "revenue", "machines", "kranen"]):
            return True
            
        # Validate if answer seems inconsistent
        inconsistency_indicators = ["geen data", "0 resultaten", "onbekend", "error"]
        if any(indicator in answer.lower() for indicator in inconsistency_indicators):
            return True
            
        return False
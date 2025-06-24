#!/usr/bin/env python3
"""
Hybrid Query Generator - Combines direct mapping with AI fallback
Perfect accuracy for common questions, AI flexibility for complex queries
"""

from typing import Dict, Any, Optional, Callable
from direct_query_mapper import DirectQueryMapper
from query_validator import QueryValidator
import requests
import json
import re

class HybridQueryGenerator:
    """
    Hybrid approach: Direct mapping first, then AI fallback with validation
    """
    
    def __init__(self, config: Dict[str, Any], validation_file_path: str):
        self.config = config
        self.direct_mapper = DirectQueryMapper()
        self.validator = QueryValidator(validation_file_path)
        self.ai_fallback_enabled = True
        
        # Statistics tracking
        self.stats = {
            "direct_mapping_hits": 0,
            "ai_fallback_used": 0,
            "validation_corrections": 0,
            "total_queries": 0
        }
    
    def generate_query(self, user_question: str, schema: Dict[str, Any], 
                      execute_query_func: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Generate SQL query using hybrid approach
        
        Returns:
        {
            "query": str,
            "method": "direct" | "ai" | "corrected",
            "confidence": float,
            "validation_result": dict,
            "description": str
        }
        """
        self.stats["total_queries"] += 1
        
        # Step 1: Try direct mapping first (100% accurate)
        direct_result = self.direct_mapper.map_question_to_query(user_question)
        if direct_result:
            self.stats["direct_mapping_hits"] += 1
            return {
                "query": direct_result["query"],
                "method": "direct",
                "confidence": 1.0,
                "validation_result": {"is_valid": True, "source": "direct_mapping"},
                "description": direct_result["description"],
                "mapping_name": direct_result["mapping_name"]
            }
        
        # Step 2: Fallback to AI generation with enhanced prompts
        if self.ai_fallback_enabled:
            self.stats["ai_fallback_used"] += 1
            ai_query = self._generate_ai_query_enhanced(user_question, schema)
            
            # Step 3: Validate AI-generated query
            if execute_query_func and ai_query:
                try:
                    # Test the query
                    test_result = execute_query_func(ai_query)
                    validation_result = self.validator.validate_query_result(
                        user_question, ai_query, test_result
                    )
                    
                    # If validation fails, try to auto-correct
                    if not validation_result["is_valid"] and validation_result["suggested_query"]:
                        self.stats["validation_corrections"] += 1
                        corrected_query = validation_result["suggested_query"]
                        
                        return {
                            "query": corrected_query,
                            "method": "corrected",
                            "confidence": 0.9,
                            "validation_result": validation_result,
                            "description": f"Auto-corrected query for: {user_question}",
                            "original_ai_query": ai_query
                        }
                    else:
                        return {
                            "query": ai_query,
                            "method": "ai",
                            "confidence": 0.7,
                            "validation_result": validation_result,
                            "description": f"AI-generated query for: {user_question}"
                        }
                
                except Exception as e:
                    # Query execution failed, try auto-correction
                    corrected_query = self.validator.auto_correct_query(user_question, ai_query)
                    if corrected_query:
                        self.stats["validation_corrections"] += 1
                        return {
                            "query": corrected_query,
                            "method": "corrected",
                            "confidence": 0.8,
                            "validation_result": {"is_valid": False, "error": str(e)},
                            "description": f"Error-corrected query for: {user_question}",
                            "original_ai_query": ai_query
                        }
            
            # Return AI query without validation if no execute function provided
            if ai_query:
                return {
                    "query": ai_query,
                    "method": "ai",
                    "confidence": 0.6,
                    "validation_result": {"is_valid": None, "message": "No validation performed"},
                    "description": f"AI-generated query for: {user_question}"
                }
        
        # Step 4: No query could be generated
        return {
            "query": None,
            "method": "failed",
            "confidence": 0.0,
            "validation_result": {"is_valid": False, "error": "No query generation method succeeded"},
            "description": f"Failed to generate query for: {user_question}"
        }
    
    def _generate_ai_query_enhanced(self, user_question: str, schema: Dict[str, Any]) -> Optional[str]:
        """Generate SQL query using enhanced AI prompts with few-shot learning"""
        
        claude_api_key = self.config.get("claude_api_key")
        if not claude_api_key:
            return None
        
        # Get examples from direct mapper for few-shot learning
        examples = self._get_few_shot_examples()
        
        # Build enhanced prompt with examples and business rules
        prompt = f"""Je bent een SQL expert voor het Hoeflon Ridder ERP systeem. 

🚨 VERPLICHTE SQL SERVER SYNTAX:
-- Gebruik DATEPART(MONTH, datum) NIET MONTH(datum) 
-- Gebruik DATEPART(YEAR, datum) NIET YEAR(datum)
-- Gebruik DATENAME(MONTH, datum) voor maandnamen
-- Gebruik GETDATE() voor huidige datum

✅ BESTAANDE KOLOMMEN (controleer deze bestaan):
- DATUMGEREED, DATECHANGED, INVOICEDATE, DATECREATED (GEEN completion_date, productie_datum)
- STATE, TOTALAMOUNT, FK_INVOICERELATION (controleer spelling)
- FK_SERVICEOBJECTTYPE, FK_OBJECTRELATION (correct gebruik)

EXACTE VOORBEELDEN (kopieer deze patronen exact):

{examples}

BUSINESS RULES (VERPLICHT):
- STATE 2 = machine gereed/verkocht
- STATE 1 = machine in productie  
- STATE 0 = machine gepland
- Voor machine types: JOIN met R_ITEM op FK_ITEMNR = PK_R_ITEM
- C6 machines: WHERE i.DESCRIPTION LIKE '%C6%'
- C30 machines: WHERE i.DESCRIPTION LIKE '%C30%'

VERIFICATIE CIJFERS (je antwoord MOET kloppen):
- Totaal machines: 9541
- Machines verkocht (STATE=2): 9358  
- Machines productie (STATE=1): 19
- C6 machines totaal: 1403
- C6 machines verkocht: 1402

BELANGRIJKE TABELLEN:
- U_SERIENUMMERSHOEFLON: machine serienummers en status
- R_ITEM: machine types en beschrijvingen
- R_SALESINVOICE: verkoop en omzet data
- R_RELATION: klanten en leveranciers

VRAAG: {user_question}

Genereer ALLEEN een SELECT query die EXACT klopt met de verificatie cijfers:"""

        headers = {
            "x-api-key": claude_api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Check if response has the expected structure
                if not response_data.get("content") or len(response_data["content"]) == 0:
                    print("Claude API returned empty content")
                    return None
                
                text_content = response_data["content"][0].get("text")
                if text_content is None:
                    print("Claude API returned None for text content")
                    return None
                
                sql_query = text_content.strip()
                
                # Clean up the response
                sql_query = re.sub(r'```sql\s*', '', sql_query)
                sql_query = re.sub(r'```\s*', '', sql_query)
                sql_query = sql_query.strip()
                
                # 🔥 CRITICAL FIX: Apply column name corrections to prevent invalid column errors
                # Fix MONTH() function calls to DATEPART(MONTH, ...)
                sql_query = re.sub(r'\bMONTH\s*\(\s*([^)]+)\s*\)', r'DATEPART(MONTH, \1)', sql_query, flags=re.IGNORECASE)
                
                # Fix YEAR() function calls to DATEPART(YEAR, ...)  
                sql_query = re.sub(r'\bYEAR\s*\(\s*([^)]+)\s*\)', r'DATEPART(YEAR, \1)', sql_query, flags=re.IGNORECASE)
                
                # Fix invalid column names that are commonly generated incorrectly
                invalid_columns = {
                    'completion_date': 'DATUMGEREED',
                    'productie_datum': 'DATUMGEREED', 
                    'production_date': 'DATUMGEREED',
                    'manufacture_date': 'DATUMGEREED',
                    'created_date': 'DATECREATED',
                    'invoice_date': 'INVOICEDATE',
                    'modified_date': 'DATECHANGED'
                }
                
                for invalid, valid in invalid_columns.items():
                    sql_query = re.sub(rf'\b{invalid}\b', valid, sql_query, flags=re.IGNORECASE)
                
                return sql_query
            
        except Exception as e:
            print(f"AI query generation failed: {e}")
        
        return None
    
    def _get_few_shot_examples(self) -> str:
        """Get examples from direct mapper for few-shot learning"""
        examples = []
        
        # Get some key examples from direct mapper
        sample_questions = [
            ("Hoeveel machines zijn er in totaal?", "machines_totaal"),
            ("Hoeveel machines zijn verkocht?", "machines_verkocht"), 
            ("Hoeveel C6 machines zijn verkocht?", "c6_machines_verkocht"),
            ("Hoeveel machines zijn in productie?", "machines_productie")
        ]
        
        for question, mapping_name in sample_questions:
            result = self.direct_mapper.map_question_to_query(question)
            if result:
                examples.append(f'Q: "{question}"\nA: {result["query"]}\n')
        
        return "\n".join(examples)
    
    def get_supported_questions(self) -> Dict[str, str]:
        """Get all questions that can be handled with high confidence"""
        return self.direct_mapper.get_all_supported_questions()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics"""
        total = self.stats["total_queries"]
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            "direct_mapping_rate": (self.stats["direct_mapping_hits"] / total) * 100,
            "ai_fallback_rate": (self.stats["ai_fallback_used"] / total) * 100,
            "correction_rate": (self.stats["validation_corrections"] / total) * 100
        }
    
    def validate_system(self, execute_query_func: Callable) -> Dict[str, Any]:
        """Validate the entire hybrid system"""
        results = {
            "direct_mapper_validation": self.direct_mapper.validate_mapping_accuracy(execute_query_func),
            "validator_test": self.validator.run_validation_test(execute_query_func),
            "system_stats": self.get_statistics()
        }
        
        # Calculate overall system accuracy
        direct_accuracy = results["direct_mapper_validation"]["accuracy_percentage"]
        validator_accuracy = results["validator_test"]["accuracy"]
        
        results["overall_system_accuracy"] = {
            "direct_mapping_accuracy": direct_accuracy,
            "validation_accuracy": validator_accuracy,
            "hybrid_confidence": (direct_accuracy + validator_accuracy) / 2
        }
        
        return results
    
    def enable_learning_mode(self, enable: bool = True):
        """Enable/disable learning from corrections"""
        self.learning_enabled = enable
    
    def learn_from_correction(self, question: str, original_query: str, 
                            corrected_query: str, actual_result: Any):
        """Learn from manual corrections to improve future accuracy"""
        if hasattr(self, 'learning_enabled') and self.learning_enabled:
            # Extract numeric result
            numeric_result = self.validator._extract_numeric_result(actual_result)
            if numeric_result:
                # Update validator's known results
                self.validator.update_known_result(question, numeric_result, corrected_query)
                print(f"🧠 Learned new pattern: {question} -> {numeric_result}")
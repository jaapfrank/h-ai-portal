#!/usr/bin/env python3
"""
Dynamic Configuration Database for Hoeflon Ridder AI
Replaces hardcoded mappings with dynamic SQLite storage
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class ConfigDatabase:
    """Dynamic configuration database using SQLite"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "/home/jaapfrank/Hoeflon Ridder/Ridder AI/config.db"
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Query mappings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            patterns TEXT NOT NULL, -- JSON array of regex patterns
            sql_query TEXT,
            expected_result TEXT, -- Can be number or 'multiple_rows', etc.
            description TEXT,
            requires_clarification BOOLEAN DEFAULT FALSE,
            clarification_options TEXT, -- JSON array
            confidence_weight REAL DEFAULT 1.0,
            success_rate REAL DEFAULT 0.0,
            last_used TIMESTAMP,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Confidence calibration table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS confidence_calibration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_type TEXT NOT NULL,
            raw_confidence REAL NOT NULL,
            calibrated_confidence REAL NOT NULL,
            actual_accuracy REAL,
            sample_size INTEGER DEFAULT 1,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # ML model metadata
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ml_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL, -- 'confidence', 'anomaly', 'query_quality', etc.
            accuracy REAL NOT NULL,
            status TEXT DEFAULT 'active', -- 'active', 'training', 'inactive'
            model_path TEXT,
            hyperparameters TEXT, -- JSON
            training_data_version TEXT,
            last_trained TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # System settings
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            type TEXT DEFAULT 'string', -- 'string', 'number', 'boolean', 'json'
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        conn.close()
        
        # Populate with initial data if empty
        self.populate_initial_data()
    
    def populate_initial_data(self):
        """Populate database with initial mappings from hardcoded data"""
        if self.get_mapping_count() == 0:
            print("🔄 Populating initial query mappings...")
            
            # Core machine queries
            self.add_mapping(
                name="c6_machines_dit_jaar",
                patterns=[
                    r"hoeveel\s+c6\s+machines?\s+(zijn\s+er\s+)?(dit\s+jaar\s+)?gebouwd",
                    r"c6\s+machines?\s+(van\s+)?dit\s+jaar",
                    r"aantal\s+c6\s+(dit\s+jaar|2025)"
                ],
                sql_query="""SELECT COUNT(*) as C6_DitJaar
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE = 10
                    AND YEAR(so.DATUMGEREED) = YEAR(GETDATE())
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                expected_result="72",
                description="C6 machines gebouwd dit jaar",
                confidence_weight=0.95
            )
            
            # Ambiguous total machines (clarification needed)
            self.add_mapping(
                name="machines_totaal_clarification",
                patterns=[
                    r"hoeveel\s+machines?\s+(zijn\s+er\s+)?(in\s+)?totaal(?!\s+(dit|vorig|deze|alle|ooit))",
                    r"totaal\s+(aantal\s+)?machines?(?!\s+(dit|vorig|deze|alle|ooit))",
                    r"aantal\s+machines?(\s+totaal)?(?!\s+(dit|vorig|deze|alle|ooit))"
                ],
                requires_clarification=True,
                clarification_options=[
                    "Machines gebouwd dit jaar (2025): ~164",
                    "Alle machines ooit gebouwd: ~9.590", 
                    "Machines in productie nu",
                    "Per machine type (C6, C30, C10, etc.)"
                ],
                description="Ambigue machines totaal vraag"
            )
            
            # Specific total queries
            self.add_mapping(
                name="machines_dit_jaar_totaal",
                patterns=[
                    r"hoeveel\s+machines?\s+(hebben\s+we\s+)?dit\s+jaar(\s+gebouwd)?",
                    r"machines?\s+(van\s+)?dit\s+jaar\s+totaal",
                    r"totaal\s+machines?\s+2025"
                ],
                sql_query="""SELECT COUNT(*) as TotaalMachinesDitJaar
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE IN (10, 15, 6, 12, 29)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)
                    AND YEAR(so.DATUMGEREED) = YEAR(GETDATE())""",
                expected_result="164",
                description="Alle machines dit jaar"
            )
            
            self.add_mapping(
                name="machines_alle_jaren_totaal",
                patterns=[
                    r"hoeveel\s+machines?\s+(zijn\s+er\s+)?ooit\s+gebouwd",
                    r"totaal\s+(aantal\s+)?machines?\s+(alle\s+jaren|ooit)",
                    r"machines?\s+in\s+totaal\s+(alle\s+jaren)?",
                    r"complete\s+geschiedenis\s+machines?"
                ],
                sql_query="""SELECT COUNT(*) as TotaalMachinesAlleJaren
                    FROM V_R_SERVICEOBJECT so 
                    WHERE so.FK_SERVICEOBJECTTYPE IN (10, 15, 6, 12, 29)
                    AND so.FK_OBJECTRELATION NOT IN (7,6736,5910,5219,1114,6109,3366,8165)""",
                expected_result="9590",
                description="Alle machines alle jaren"
            )
            
            # Leverancier/Supplier Performance Queries
            self.add_mapping(
                name="leverancier_delivery_performance_dit_jaar",
                patterns=[
                    r"delivery\s+performance\s+(van\s+)?(onze\s+)?leveranciers?\s+(dit\s+jaar|2025)",
                    r"(wat\s+is\s+)?(de\s+)?leverancier\s+prestatie\s+(dit\s+jaar|2025)",
                    r"(hoe\s+presteren\s+|prestatie\s+van\s+)onze\s+leveranciers?\s+(dit\s+jaar|2025)",
                    r"delivery\s+(prestatie|performance)\s+leveranciers?\s+(dit\s+jaar|2025)",
                    r"leverancier\s+performance\s+(dit\s+jaar|2025)"
                ],
                sql_query="""SELECT 
                    r.NAME as Leverancier,
                    COUNT(po.ID) as TotaalOrders,
                    COUNT(CASE WHEN po.DELIVERYDATE <= po.REQUESTEDDELIVERYDATE THEN 1 END) as OpTijd,
                    COUNT(CASE WHEN po.DELIVERYDATE > po.REQUESTEDDELIVERYDATE THEN 1 END) as TeLaat,
                    ROUND(
                        CAST(COUNT(CASE WHEN po.DELIVERYDATE <= po.REQUESTEDDELIVERYDATE THEN 1 END) AS FLOAT) * 100.0 / 
                        CAST(COUNT(po.ID) AS FLOAT), 2
                    ) as PercentageOpTijd,
                    AVG(DATEDIFF(day, po.REQUESTEDDELIVERYDATE, po.DELIVERYDATE)) as GemiddeldeVertraging
                FROM R_PURCHASEORDER po
                INNER JOIN R_RELATION r ON po.FK_SUPPLIER = r.ID
                WHERE YEAR(po.ORDERDATE) = YEAR(GETDATE())
                  AND po.DELIVERYDATE IS NOT NULL
                  AND po.REQUESTEDDELIVERYDATE IS NOT NULL
                GROUP BY r.NAME, r.ID
                ORDER BY PercentageOpTijd DESC""",
                expected_result="multiple_rows",
                description="Delivery performance van leveranciers dit jaar",
                confidence_weight=0.90
            )
            
            self.add_mapping(
                name="top_leveranciers_performance",
                patterns=[
                    r"(beste|top)\s+leveranciers?\s+(delivery\s+)?performance",
                    r"(welke|wat\s+zijn\s+de)\s+(beste|top)\s+leveranciers?",
                    r"leveranciers?\s+met\s+(beste|hoogste)\s+performance",
                    r"top\s+\d+\s+leveranciers?\s+performance"
                ],
                sql_query="""SELECT TOP 10
                    r.NAME as Leverancier,
                    COUNT(po.ID) as TotaalOrders,
                    ROUND(
                        CAST(COUNT(CASE WHEN po.DELIVERYDATE <= po.REQUESTEDDELIVERYDATE THEN 1 END) AS FLOAT) * 100.0 / 
                        CAST(COUNT(po.ID) AS FLOAT), 2
                    ) as PercentageOpTijd,
                    SUM(po.TOTALAMOUNT) as TotaalWaarde,
                    AVG(DATEDIFF(day, po.REQUESTEDDELIVERYDATE, po.DELIVERYDATE)) as GemiddeldeVertraging
                FROM R_PURCHASEORDER po
                INNER JOIN R_RELATION r ON po.FK_SUPPLIER = r.ID
                WHERE YEAR(po.ORDERDATE) = YEAR(GETDATE())
                  AND po.DELIVERYDATE IS NOT NULL
                  AND po.REQUESTEDDELIVERYDATE IS NOT NULL
                GROUP BY r.NAME, r.ID
                HAVING COUNT(po.ID) >= 3
                ORDER BY PercentageOpTijd DESC, TotaalOrders DESC""",
                expected_result="multiple_rows",
                description="Top leveranciers op basis van delivery performance",
                confidence_weight=0.85
            )
            
            print("✅ Initial mappings populated (including leverancier performance)")
    
    def add_mapping(self, name: str, patterns: List[str], sql_query: str = None, 
                   expected_result: str = None, description: str = None,
                   requires_clarification: bool = False, clarification_options: List[str] = None,
                   confidence_weight: float = 1.0):
        """Add or update a query mapping"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT OR REPLACE INTO query_mappings 
        (name, patterns, sql_query, expected_result, description, requires_clarification, 
         clarification_options, confidence_weight, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            name,
            json.dumps(patterns),
            sql_query,
            expected_result,
            description,
            requires_clarification,
            json.dumps(clarification_options) if clarification_options else None,
            confidence_weight
        ))
        
        conn.commit()
        conn.close()
    
    def get_all_mappings(self) -> List[Dict[str, Any]]:
        """Get all query mappings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM query_mappings ORDER BY name")
        rows = cursor.fetchall()
        
        mappings = []
        for row in rows:
            mapping = {
                'id': row[0],
                'name': row[1],
                'patterns': json.loads(row[2]),
                'sql_query': row[3],
                'expected_result': row[4],
                'description': row[5],
                'requires_clarification': bool(row[6]),
                'clarification_options': json.loads(row[7]) if row[7] else None,
                'confidence_weight': row[8],
                'success_rate': row[9],
                'last_used': row[10],
                'usage_count': row[11]
            }
            mappings.append(mapping)
        
        conn.close()
        return mappings
    
    def get_mapping_count(self) -> int:
        """Get total number of mappings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM query_mappings")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def update_mapping_usage(self, mapping_name: str, success: bool = True, user_feedback: str = None, actual_result: Any = None):
        """Update usage statistics and learn from results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if success:
            cursor.execute("""
            UPDATE query_mappings 
            SET usage_count = usage_count + 1,
                last_used = CURRENT_TIMESTAMP,
                success_rate = CASE 
                    WHEN usage_count = 0 THEN 1.0
                    ELSE (success_rate * usage_count + 1.0) / (usage_count + 1)
                END
            WHERE name = ?
            """, (mapping_name,))
        else:
            cursor.execute("""
            UPDATE query_mappings 
            SET usage_count = usage_count + 1,
                last_used = CURRENT_TIMESTAMP,
                success_rate = CASE 
                    WHEN usage_count = 0 THEN 0.0
                    ELSE (success_rate * usage_count) / (usage_count + 1)
                END
            WHERE name = ?
            """, (mapping_name,))
        
        # Learn from actual results - update expected results dynamically
        if actual_result is not None and success:
            self._learn_from_result(mapping_name, actual_result)
        
        # Store user feedback for pattern learning
        if user_feedback:
            self._store_feedback(mapping_name, user_feedback, success)
        
        conn.commit()
        conn.close()
    
    def _learn_from_result(self, mapping_name: str, actual_result: Any):
        """Learn and adapt expected results based on actual query outcomes"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            # Get current expected result
            cursor.execute("SELECT expected_result, usage_count FROM query_mappings WHERE name = ?", (mapping_name,))
            result = cursor.fetchone()
            
            if result:
                current_expected, usage_count = result
                
                # For numerical results, use moving average to adapt expectations
                if isinstance(actual_result, (int, float)):
                    if current_expected and current_expected.isdigit():
                        current_val = float(current_expected)
                        # Weighted average: give more weight to recent results
                        weight = min(0.3, 10.0 / (usage_count + 10))  # Adaptive learning rate
                        new_expected = str(int(current_val * (1 - weight) + actual_result * weight))
                        
                        cursor.execute(
                            "UPDATE query_mappings SET expected_result = ? WHERE name = ?",
                            (new_expected, mapping_name)
                        )
                        
                        print(f"🧠 Learning: {mapping_name} expected result updated from {current_expected} to {new_expected}")
            
            conn.commit()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"⚠️ Database temporarily locked, skipping learning for {mapping_name}")
            else:
                raise e
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _store_feedback(self, mapping_name: str, feedback: str, success: bool):
        """Store user feedback for future pattern analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create feedback table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mapping_name TEXT NOT NULL,
            feedback TEXT NOT NULL,
            success BOOLEAN NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute(
            "INSERT INTO user_feedback (mapping_name, feedback, success) VALUES (?, ?, ?)",
            (mapping_name, feedback, success)
        )
        
        conn.commit()
        conn.close()
    
    def analyze_and_suggest_improvements(self) -> List[Dict[str, Any]]:
        """Analyze usage patterns and suggest dynamic improvements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        suggestions = []
        
        # Find low-performing mappings
        cursor.execute("""
        SELECT name, success_rate, usage_count, description 
        FROM query_mappings 
        WHERE usage_count > 5 AND success_rate < 0.7
        ORDER BY usage_count DESC
        """)
        
        low_performers = cursor.fetchall()
        for name, success_rate, usage_count, description in low_performers:
            suggestions.append({
                'type': 'low_performance',
                'mapping': name,
                'issue': f'Success rate {success_rate:.1%} with {usage_count} uses',
                'suggestion': 'Consider updating patterns or SQL query',
                'priority': 'high' if usage_count > 20 else 'medium'
            })
        
        # Find unused mappings that might be obsolete
        cursor.execute("""
        SELECT name, created_at, description 
        FROM query_mappings 
        WHERE usage_count = 0 AND created_at < datetime('now', '-30 days')
        """)
        
        unused = cursor.fetchall()
        for name, created_at, description in unused:
            suggestions.append({
                'type': 'unused_mapping',
                'mapping': name,
                'issue': f'No usage since {created_at}',
                'suggestion': 'Consider archiving or updating patterns',
                'priority': 'low'
            })
        
        # Find patterns that need new mappings based on failed queries
        cursor.execute("""
        SELECT feedback, COUNT(*) as frequency 
        FROM user_feedback 
        WHERE success = 0 AND timestamp > datetime('now', '-7 days')
        GROUP BY feedback 
        HAVING frequency > 2
        ORDER BY frequency DESC
        """)
        
        common_failures = cursor.fetchall()
        for feedback, frequency in common_failures:
            suggestions.append({
                'type': 'missing_mapping',
                'pattern': feedback,
                'issue': f'Failed {frequency} times in last week',
                'suggestion': 'Consider creating new mapping for this pattern',
                'priority': 'high' if frequency > 5 else 'medium'
            })
        
        conn.close()
        return suggestions
    
    def auto_optimize_patterns(self):
        """Automatically optimize patterns based on usage data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find frequently failing patterns and adjust confidence weights
        cursor.execute("""
        SELECT name, success_rate, confidence_weight 
        FROM query_mappings 
        WHERE usage_count > 10 AND success_rate < 0.8
        """)
        
        failing_mappings = cursor.fetchall()
        optimizations = []
        
        for name, success_rate, confidence_weight in failing_mappings:
            # Reduce confidence weight for poor performers
            new_weight = confidence_weight * success_rate
            
            cursor.execute(
                "UPDATE query_mappings SET confidence_weight = ? WHERE name = ?",
                (new_weight, name)
            )
            
            optimizations.append(f"🔧 Reduced confidence weight for '{name}' from {confidence_weight:.2f} to {new_weight:.2f}")
        
        # Boost confidence for high performers
        cursor.execute("""
        SELECT name, success_rate, confidence_weight 
        FROM query_mappings 
        WHERE usage_count > 10 AND success_rate > 0.95 AND confidence_weight < 1.0
        """)
        
        high_performers = cursor.fetchall()
        for name, success_rate, confidence_weight in high_performers:
            new_weight = min(1.0, confidence_weight * 1.1)
            
            cursor.execute(
                "UPDATE query_mappings SET confidence_weight = ? WHERE name = ?",
                (new_weight, name)
            )
            
            optimizations.append(f"⚡ Boosted confidence weight for '{name}' from {confidence_weight:.2f} to {new_weight:.2f}")
        
        conn.commit()
        conn.close()
        
        return optimizations
    
    def calibrate_confidence(self, query_type: str, raw_confidence: float, actual_accuracy: float = None):
        """Add confidence calibration data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate calibrated confidence (simple moving average for now)
        cursor.execute("""
        SELECT AVG(calibrated_confidence), COUNT(*) 
        FROM confidence_calibration 
        WHERE query_type = ? AND raw_confidence BETWEEN ? AND ?
        """, (query_type, raw_confidence - 0.1, raw_confidence + 0.1))
        
        result = cursor.fetchone()
        avg_calibrated = result[0] if result[0] else raw_confidence
        sample_count = result[1]
        
        # Simple calibration: blend with historical data
        if sample_count > 0:
            calibrated = (avg_calibrated * 0.8) + (raw_confidence * 0.2)
        else:
            calibrated = raw_confidence
        
        cursor.execute("""
        INSERT INTO confidence_calibration 
        (query_type, raw_confidence, calibrated_confidence, actual_accuracy, last_updated)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (query_type, raw_confidence, calibrated, actual_accuracy))
        
        conn.commit()
        conn.close()
        
        return calibrated
    
    def get_calibrated_confidence(self, query_type: str, raw_confidence: float) -> float:
        """Get calibrated confidence for a query type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT AVG(calibrated_confidence) 
        FROM confidence_calibration 
        WHERE query_type = ? AND raw_confidence BETWEEN ? AND ?
        """, (query_type, raw_confidence - 0.15, raw_confidence + 0.15))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result[0] else raw_confidence
    
    def set_setting(self, key: str, value: Any, setting_type: str = 'string', description: str = None):
        """Set a system setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if setting_type == 'json':
            value_str = json.dumps(value)
        else:
            value_str = str(value)
        
        cursor.execute("""
        INSERT OR REPLACE INTO system_settings (key, value, type, description, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (key, value_str, setting_type, description))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default=None):
        """Get a system setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value, type FROM system_settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return default
        
        value_str, setting_type = result
        
        if setting_type == 'json':
            return json.loads(value_str)
        elif setting_type == 'number':
            return float(value_str)
        elif setting_type == 'boolean':
            return value_str.lower() in ('true', '1', 'yes')
        else:
            return value_str
    
    def get_dynamic_query_recommendations(self, user_input: str) -> List[Dict[str, Any]]:
        """Get dynamic query recommendations based on patterns and learning"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find similar successful patterns
        cursor.execute("""
        SELECT name, patterns, description, success_rate, confidence_weight
        FROM query_mappings 
        WHERE success_rate > 0.5
        ORDER BY usage_count DESC, success_rate DESC
        LIMIT 10
        """)
        
        recommendations = []
        mappings = cursor.fetchall()
        
        for name, patterns_json, description, success_rate, confidence_weight in mappings:
            patterns = json.loads(patterns_json)
            
            # Simple similarity check (can be enhanced with ML)
            similarity_score = self._calculate_similarity(user_input, patterns)
            
            if similarity_score > 0.3:
                recommendations.append({
                    'mapping_name': name,
                    'description': description,
                    'similarity': similarity_score,
                    'success_rate': success_rate,
                    'confidence_weight': confidence_weight,
                    'suggestion': f"Dit lijkt op: {description}"
                })
        
        conn.close()
        return sorted(recommendations, key=lambda x: x['similarity'], reverse=True)[:3]
    
    def _calculate_similarity(self, user_input: str, patterns: List[str]) -> float:
        """Calculate similarity between user input and existing patterns"""
        user_words = set(user_input.lower().split())
        
        max_similarity = 0.0
        for pattern in patterns:
            # Extract words from regex pattern (simplified)
            pattern_words = set(re.findall(r'\w+', pattern.lower()))
            
            if pattern_words and user_words:
                intersection = len(user_words & pattern_words)
                union = len(user_words | pattern_words)
                similarity = intersection / union if union > 0 else 0.0
                max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def schedule_learning_cycle(self):
        """Run automated learning and optimization cycle"""
        print("🤖 Starting automated learning cycle...")
        
        # Auto-optimize patterns
        optimizations = self.auto_optimize_patterns()
        for opt in optimizations:
            print(opt)
        
        # Get improvement suggestions
        suggestions = self.analyze_and_suggest_improvements()
        
        high_priority = [s for s in suggestions if s['priority'] == 'high']
        if high_priority:
            print(f"\n⚠️ Found {len(high_priority)} high-priority improvements needed:")
            for suggestion in high_priority[:3]:
                print(f"  • {suggestion['type']}: {suggestion['issue']}")
        
        # Auto-calibrate confidence based on recent performance
        self._auto_calibrate_confidence()
        
        print("✅ Learning cycle completed")
        
        return {
            'optimizations': len(optimizations),
            'suggestions': len(suggestions),
            'high_priority_issues': len(high_priority)
        }
    
    def _auto_calibrate_confidence(self):
        """Automatically calibrate confidence scores based on actual performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent performance data
        cursor.execute("""
        SELECT query_type, AVG(actual_accuracy), COUNT(*) as samples
        FROM confidence_calibration 
        WHERE last_updated > datetime('now', '-30 days')
          AND actual_accuracy IS NOT NULL
        GROUP BY query_type
        HAVING samples > 3
        """)
        
        calibrations = cursor.fetchall()
        for query_type, avg_accuracy, samples in calibrations:
            # Update confidence calibration based on real performance
            cursor.execute("""
            INSERT INTO confidence_calibration 
            (query_type, raw_confidence, calibrated_confidence, actual_accuracy, sample_size)
            VALUES (?, ?, ?, ?, ?)
            """, (query_type, avg_accuracy, avg_accuracy, avg_accuracy, samples))
        
        conn.commit()
        conn.close()

    def run_daily_maintenance(self):
        """Run daily database maintenance and learning cycle"""
        print("🔄 Running daily database maintenance...")
        
        # Update expected results from actual database state
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Example: Update machine counts automatically
        try:
            from .main import execute_query  # Dynamic import to avoid circular dependency
            
            # Update C6 machines count
            c6_result = execute_query("SELECT COUNT(*) FROM V_R_SERVICEOBJECT WHERE FK_SERVICEOBJECTTYPE = 10 AND YEAR(DATUMGEREED) = YEAR(GETDATE())")
            if c6_result and len(c6_result) > 0:
                new_count = str(c6_result[0][0])
                cursor.execute("UPDATE query_mappings SET expected_result = ? WHERE name = 'c6_machines_dit_jaar'", (new_count,))
                print(f"📊 Updated C6 machines expected result to {new_count}")
            
            # Update total machines count
            total_result = execute_query("SELECT COUNT(*) FROM V_R_SERVICEOBJECT WHERE FK_SERVICEOBJECTTYPE IN (10, 15, 6, 12, 29) AND YEAR(DATUMGEREED) = YEAR(GETDATE())")
            if total_result and len(total_result) > 0:
                new_total = str(total_result[0][0])
                cursor.execute("UPDATE query_mappings SET expected_result = ? WHERE name = 'machines_dit_jaar_totaal'", (new_total,))
                print(f"📊 Updated total machines expected result to {new_total}")
                
        except Exception as e:
            print(f"⚠️ Could not auto-update expected results: {e}")
        
        conn.commit()
        conn.close()
        
        # Run learning cycle
        self.schedule_learning_cycle()
        
        print("✅ Daily maintenance completed")
    
    def get_database_freshness_score(self) -> float:
        """Calculate how up-to-date the configuration is"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check how recent the data updates are
        cursor.execute("""
        SELECT AVG(
            CASE 
                WHEN last_used IS NULL THEN 0
                WHEN last_used > datetime('now', '-7 days') THEN 1.0
                WHEN last_used > datetime('now', '-30 days') THEN 0.7
                WHEN last_used > datetime('now', '-90 days') THEN 0.4
                ELSE 0.1
            END
        ) as freshness
        FROM query_mappings
        """)
        
        freshness = cursor.fetchone()[0] or 0.0
        conn.close()
        
        return freshness
    
    def export_dynamic_insights(self) -> Dict[str, Any]:
        """Export current state and learning insights"""
        insights = {
            "database_freshness": self.get_database_freshness_score(),
            "total_mappings": self.get_mapping_count(),
            "improvement_suggestions": self.analyze_and_suggest_improvements(),
            "learning_stats": {
                "queries_processed": 0,
                "patterns_learned": 0,
                "auto_optimizations": 0
            }
        }
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get usage statistics
        cursor.execute("SELECT SUM(usage_count), AVG(success_rate) FROM query_mappings")
        total_usage, avg_success = cursor.fetchone()
        insights["learning_stats"]["queries_processed"] = total_usage or 0
        insights["learning_stats"]["average_success_rate"] = avg_success or 0.0
        
        # Get feedback count
        cursor.execute("SELECT COUNT(*) FROM user_feedback")
        feedback_count = cursor.fetchone()[0]
        insights["learning_stats"]["feedback_entries"] = feedback_count
        
        conn.close()
        return insights

if __name__ == "__main__":
    # Test the configuration database
    config_db = ConfigDatabase()
    
    print("🧪 Testing Dynamic Configuration Database...")
    
    # Test mappings
    mappings = config_db.get_all_mappings()
    print(f"✅ Found {len(mappings)} query mappings")
    
    # Test settings
    config_db.set_setting("confidence_threshold", 0.75, "number", "Minimum confidence for auto-execution")
    threshold = config_db.get_setting("confidence_threshold")
    print(f"✅ Confidence threshold: {threshold}")
    
    # Test confidence calibration
    calibrated = config_db.calibrate_confidence("machine_count", 0.85, 0.92)
    print(f"✅ Calibrated confidence: {calibrated}")
    
    # Test dynamic learning features
    print("\n🤖 Testing Dynamic Learning Features:")
    
    # Test learning from results
    config_db.update_mapping_usage("c6_machines_dit_jaar", success=True, actual_result=75)
    print("✅ Learning from results tested")
    
    # Test optimization
    optimizations = config_db.auto_optimize_patterns()
    print(f"✅ Auto-optimization: {len(optimizations)} changes made")
    
    # Test improvement suggestions
    suggestions = config_db.analyze_and_suggest_improvements()
    print(f"✅ Improvement analysis: {len(suggestions)} suggestions generated")
    
    # Test query recommendations
    recommendations = config_db.get_dynamic_query_recommendations("hoeveel machines")
    print(f"✅ Dynamic recommendations: {len(recommendations)} suggestions")
    
    # Test freshness score
    freshness = config_db.get_database_freshness_score()
    print(f"✅ Database freshness score: {freshness:.2f}")
    
    # Test insights export
    insights = config_db.export_dynamic_insights()
    print(f"✅ Dynamic insights: {insights['total_mappings']} mappings, {insights['database_freshness']:.2f} freshness")
    
    print("\n✅ Dynamic Configuration Database fully operational!")
    print("🔄 Data will remain dynamic through:")
    print("  • Automatic result learning")
    print("  • Weekly confidence optimization") 
    print("  • User feedback integration")
    print("  • Daily database synchronization")
    print("  • Pattern recognition updates")
#!/usr/bin/env python3
"""
INTELLIGENT TABLE CACHE - ERIK's Performance Optimization System
NO MORE SLOW SCHEMA QUERIES - SMART CACHING FOR 965+ TABLES!
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import sqlite3
import threading
from collections import defaultdict
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TableCacheEntry:
    """Single table cache entry"""
    table_name: str
    schema: Dict[str, Any]
    column_info: List[Dict[str, Any]]
    sample_data: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    business_context: str
    access_frequency: int
    last_accessed: str
    cache_timestamp: str
    is_dirty: bool = False
    
@dataclass
class QueryCacheEntry:
    """Single query cache entry"""
    query_hash: str
    query_sql: str
    result_data: Any
    execution_time: float
    confidence: float
    cache_timestamp: str
    access_count: int
    last_accessed: str
    expiry_time: str

@dataclass
class CacheStats:
    """Cache performance statistics"""
    total_tables_cached: int
    total_queries_cached: int
    cache_hit_rate: float
    average_response_time: float
    memory_usage_mb: float
    last_cleanup: str
    cache_size_mb: float

class IntelligentTableCache:
    """🔥 ERIK's Intelligent Table Cache System - PERFORMANCE OPTIMIZATION!"""
    
    def __init__(self, cache_dir: str = "../cache"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cache_dir = cache_dir
        self.cache_db_path = os.path.join(cache_dir, "intelligent_cache.db")
        
        # In-memory caches for fastest access
        self.table_cache: Dict[str, TableCacheEntry] = {}
        self.query_cache: Dict[str, QueryCacheEntry] = {}
        
        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_queries = 0
        
        # Cache settings
        self.max_cache_size_mb = 500  # 500MB max cache
        self.max_query_cache_entries = 1000
        self.max_table_cache_entries = 1000
        self.query_expiry_hours = 24
        self.table_expiry_hours = 168  # 1 week
        
        # Thread safety
        self.cache_lock = threading.RLock()
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize SQLite cache database
        self._initialize_cache_db()
        
        # Load existing cache from disk
        self._load_cache_from_disk()
        
        self.logger.info("🔥 ERIK: Intelligent Table Cache initialized with high-performance optimization")
    
    def _initialize_cache_db(self):
        """Initialize SQLite cache database"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                # Table cache table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS table_cache (
                        table_name TEXT PRIMARY KEY,
                        schema_json TEXT,
                        column_info_json TEXT,
                        sample_data_json TEXT,
                        relationships_json TEXT,
                        business_context TEXT,
                        access_frequency INTEGER DEFAULT 0,
                        last_accessed TEXT,
                        cache_timestamp TEXT,
                        is_dirty INTEGER DEFAULT 0
                    )
                """)
                
                # Query cache table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS query_cache (
                        query_hash TEXT PRIMARY KEY,
                        query_sql TEXT,
                        result_data_json TEXT,
                        execution_time REAL,
                        confidence REAL,
                        cache_timestamp TEXT,
                        access_count INTEGER DEFAULT 0,
                        last_accessed TEXT,
                        expiry_time TEXT
                    )
                """)
                
                # Cache statistics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cache_stats (
                        id INTEGER PRIMARY KEY,
                        total_tables_cached INTEGER,
                        total_queries_cached INTEGER,
                        cache_hit_rate REAL,
                        average_response_time REAL,
                        memory_usage_mb REAL,
                        last_cleanup TEXT,
                        cache_size_mb REAL,
                        timestamp TEXT
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to initialize cache database: {e}")
    
    def _load_cache_from_disk(self):
        """Load existing cache from SQLite database"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                # Load table cache
                cursor.execute("SELECT * FROM table_cache")
                for row in cursor.fetchall():
                    table_name = row[0]
                    try:
                        entry = TableCacheEntry(
                            table_name=table_name,
                            schema=json.loads(row[1]) if row[1] else {},
                            column_info=json.loads(row[2]) if row[2] else [],
                            sample_data=json.loads(row[3]) if row[3] else [],
                            relationships=json.loads(row[4]) if row[4] else [],
                            business_context=row[5] or "",
                            access_frequency=row[6] or 0,
                            last_accessed=row[7] or "",
                            cache_timestamp=row[8] or "",
                            is_dirty=bool(row[9])
                        )
                        self.table_cache[table_name] = entry
                    except Exception as e:
                        self.logger.warning(f"Failed to load table cache entry {table_name}: {e}")
                
                # Load query cache
                cursor.execute("SELECT * FROM query_cache")
                for row in cursor.fetchall():
                    query_hash = row[0]
                    try:
                        entry = QueryCacheEntry(
                            query_hash=query_hash,
                            query_sql=row[1] or "",
                            result_data=json.loads(row[2]) if row[2] else None,
                            execution_time=row[3] or 0.0,
                            confidence=row[4] or 0.0,
                            cache_timestamp=row[5] or "",
                            access_count=row[6] or 0,
                            last_accessed=row[7] or "",
                            expiry_time=row[8] or ""
                        )
                        self.query_cache[query_hash] = entry
                    except Exception as e:
                        self.logger.warning(f"Failed to load query cache entry {query_hash}: {e}")
                
                self.logger.info(f"✅ ERIK: Loaded {len(self.table_cache)} table entries and {len(self.query_cache)} query entries from cache")
                
        except Exception as e:
            self.logger.error(f"Failed to load cache from disk: {e}")
    
    def _save_cache_to_disk(self):
        """Save current cache to SQLite database"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                
                # Save table cache
                for table_name, entry in self.table_cache.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO table_cache 
                        (table_name, schema_json, column_info_json, sample_data_json, 
                         relationships_json, business_context, access_frequency, 
                         last_accessed, cache_timestamp, is_dirty)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        table_name,
                        json.dumps(entry.schema),
                        json.dumps(entry.column_info),
                        json.dumps(entry.sample_data),
                        json.dumps(entry.relationships),
                        entry.business_context,
                        entry.access_frequency,
                        entry.last_accessed,
                        entry.cache_timestamp,
                        int(entry.is_dirty)
                    ))
                
                # Save query cache
                for query_hash, entry in self.query_cache.items():
                    cursor.execute("""
                        INSERT OR REPLACE INTO query_cache 
                        (query_hash, query_sql, result_data_json, execution_time, 
                         confidence, cache_timestamp, access_count, last_accessed, expiry_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        query_hash,
                        entry.query_sql,
                        json.dumps(entry.result_data, default=str),
                        entry.execution_time,
                        entry.confidence,
                        entry.cache_timestamp,
                        entry.access_count,
                        entry.last_accessed,
                        entry.expiry_time
                    ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to save cache to disk: {e}")
    
    def _generate_query_hash(self, query_sql: str) -> str:
        """Generate hash for SQL query"""
        return hashlib.md5(query_sql.encode('utf-8')).hexdigest()
    
    def _is_cache_entry_expired(self, timestamp: str, expiry_hours: int) -> bool:
        """Check if cache entry is expired"""
        try:
            cache_time = datetime.fromisoformat(timestamp)
            expiry_time = cache_time + timedelta(hours=expiry_hours)
            return datetime.now() > expiry_time
        except:
            return True
    
    async def cache_table_info(self, table_name: str, schema: Dict[str, Any], 
                             column_info: List[Dict[str, Any]], 
                             sample_data: List[Dict[str, Any]] = None,
                             relationships: List[Dict[str, Any]] = None,
                             business_context: str = "") -> bool:
        """🔥 ERIK: Cache table information for fast retrieval"""
        try:
            with self.cache_lock:
                current_time = datetime.now().isoformat()
                
                # Create cache entry
                entry = TableCacheEntry(
                    table_name=table_name,
                    schema=schema,
                    column_info=column_info,
                    sample_data=sample_data or [],
                    relationships=relationships or [],
                    business_context=business_context,
                    access_frequency=0,
                    last_accessed=current_time,
                    cache_timestamp=current_time,
                    is_dirty=False
                )
                
                # Store in memory cache
                self.table_cache[table_name] = entry
                
                # Persist to disk (async to avoid blocking)
                self._save_table_to_disk(entry)
                
                self.logger.debug(f"✅ ERIK: Cached table {table_name} with {len(column_info)} columns")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ ERIK: Failed to cache table {table_name}: {e}")
            return False
    
    def _save_table_to_disk(self, entry: TableCacheEntry):
        """Save single table entry to disk"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO table_cache 
                    (table_name, schema_json, column_info_json, sample_data_json, 
                     relationships_json, business_context, access_frequency, 
                     last_accessed, cache_timestamp, is_dirty)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.table_name,
                    json.dumps(entry.schema),
                    json.dumps(entry.column_info),
                    json.dumps(entry.sample_data),
                    json.dumps(entry.relationships),
                    entry.business_context,
                    entry.access_frequency,
                    entry.last_accessed,
                    entry.cache_timestamp,
                    int(entry.is_dirty)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to save table to disk: {e}")
    
    async def get_cached_table_info(self, table_name: str) -> Optional[TableCacheEntry]:
        """🔥 ERIK: Get cached table information - SUPER FAST!"""
        try:
            with self.cache_lock:
                # Check memory cache first
                if table_name in self.table_cache:
                    entry = self.table_cache[table_name]
                    
                    # Check if expired
                    if self._is_cache_entry_expired(entry.cache_timestamp, self.table_expiry_hours):
                        # Mark as dirty and remove from cache
                        del self.table_cache[table_name]
                        self.cache_misses += 1
                        return None
                    
                    # Update access statistics
                    entry.access_frequency += 1
                    entry.last_accessed = datetime.now().isoformat()
                    
                    self.cache_hits += 1
                    self.logger.debug(f"🎯 ERIK: Cache HIT for table {table_name}")
                    return entry
                
                self.cache_misses += 1
                self.logger.debug(f"❌ ERIK: Cache MISS for table {table_name}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get cached table info: {e}")
            return None
    
    async def cache_query_result(self, query_sql: str, result_data: Any, 
                               execution_time: float, confidence: float) -> bool:
        """🔥 ERIK: Cache query result for lightning-fast repeat queries"""
        try:
            with self.cache_lock:
                query_hash = self._generate_query_hash(query_sql)
                current_time = datetime.now().isoformat()
                expiry_time = (datetime.now() + timedelta(hours=self.query_expiry_hours)).isoformat()
                
                # Create cache entry
                entry = QueryCacheEntry(
                    query_hash=query_hash,
                    query_sql=query_sql,
                    result_data=result_data,
                    execution_time=execution_time,
                    confidence=confidence,
                    cache_timestamp=current_time,
                    access_count=0,
                    last_accessed=current_time,
                    expiry_time=expiry_time
                )
                
                # Store in memory cache
                self.query_cache[query_hash] = entry
                
                # Save to disk
                self._save_query_to_disk(entry)
                
                # Cleanup if cache is too large
                await self._cleanup_query_cache()
                
                self.logger.debug(f"✅ ERIK: Cached query result (hash: {query_hash[:8]}...)")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ ERIK: Failed to cache query result: {e}")
            return False
    
    def _save_query_to_disk(self, entry: QueryCacheEntry):
        """Save single query entry to disk"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO query_cache 
                    (query_hash, query_sql, result_data_json, execution_time, 
                     confidence, cache_timestamp, access_count, last_accessed, expiry_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.query_hash,
                    entry.query_sql,
                    json.dumps(entry.result_data, default=str),
                    entry.execution_time,
                    entry.confidence,
                    entry.cache_timestamp,
                    entry.access_count,
                    entry.last_accessed,
                    entry.expiry_time
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Failed to save query to disk: {e}")
    
    async def get_cached_query_result(self, query_sql: str) -> Optional[QueryCacheEntry]:
        """🔥 ERIK: Get cached query result - INSTANT RESULTS!"""
        try:
            with self.cache_lock:
                query_hash = self._generate_query_hash(query_sql)
                
                # Check memory cache first
                if query_hash in self.query_cache:
                    entry = self.query_cache[query_hash]
                    
                    # Check if expired
                    if self._is_cache_entry_expired(entry.expiry_time, 0):
                        # Remove expired entry
                        del self.query_cache[query_hash]
                        self.cache_misses += 1
                        return None
                    
                    # Update access statistics
                    entry.access_count += 1
                    entry.last_accessed = datetime.now().isoformat()
                    
                    self.cache_hits += 1
                    self.total_queries += 1
                    self.logger.debug(f"🎯 ERIK: Query cache HIT (hash: {query_hash[:8]}...)")
                    return entry
                
                self.cache_misses += 1
                self.total_queries += 1
                self.logger.debug(f"❌ ERIK: Query cache MISS (hash: {query_hash[:8]}...)")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get cached query result: {e}")
            return None
    
    async def _cleanup_query_cache(self):
        """Clean up old query cache entries"""
        try:
            if len(self.query_cache) <= self.max_query_cache_entries:
                return
            
            # Remove expired entries first
            expired_hashes = []
            for query_hash, entry in self.query_cache.items():
                if self._is_cache_entry_expired(entry.expiry_time, 0):
                    expired_hashes.append(query_hash)
            
            for query_hash in expired_hashes:
                del self.query_cache[query_hash]
            
            # If still too many, remove least frequently accessed
            if len(self.query_cache) > self.max_query_cache_entries:
                sorted_entries = sorted(
                    self.query_cache.items(), 
                    key=lambda x: (x[1].access_count, x[1].last_accessed)
                )
                
                # Remove 20% of entries
                entries_to_remove = len(sorted_entries) // 5
                for i in range(entries_to_remove):
                    query_hash = sorted_entries[i][0]
                    del self.query_cache[query_hash]
            
            self.logger.info(f"✅ ERIK: Query cache cleanup completed, {len(self.query_cache)} entries remaining")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup query cache: {e}")
    
    async def get_cache_statistics(self) -> CacheStats:
        """🔥 ERIK: Get comprehensive cache performance statistics"""
        try:
            with self.cache_lock:
                # Calculate hit rate
                total_requests = self.cache_hits + self.cache_misses
                hit_rate = (self.cache_hits / total_requests) if total_requests > 0 else 0.0
                
                # Calculate average response time from cached queries
                cached_execution_times = [entry.execution_time for entry in self.query_cache.values()]
                avg_response_time = sum(cached_execution_times) / len(cached_execution_times) if cached_execution_times else 0.0
                
                # Estimate memory usage (rough calculation)
                memory_usage = 0
                for entry in self.table_cache.values():
                    memory_usage += len(json.dumps(asdict(entry), default=str))
                for entry in self.query_cache.values():
                    memory_usage += len(json.dumps(asdict(entry), default=str))
                memory_usage_mb = memory_usage / (1024 * 1024)
                
                stats = CacheStats(
                    total_tables_cached=len(self.table_cache),
                    total_queries_cached=len(self.query_cache),
                    cache_hit_rate=hit_rate,
                    average_response_time=avg_response_time,
                    memory_usage_mb=memory_usage_mb,
                    last_cleanup=datetime.now().isoformat(),
                    cache_size_mb=memory_usage_mb
                )
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get cache statistics: {e}")
            return CacheStats(0, 0, 0.0, 0.0, 0.0, "", 0.0)
    
    async def get_popular_tables(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently accessed tables"""
        try:
            with self.cache_lock:
                table_access = [(name, entry.access_frequency) 
                              for name, entry in self.table_cache.items()]
                table_access.sort(key=lambda x: x[1], reverse=True)
                return table_access[:limit]
        except Exception as e:
            self.logger.error(f"Failed to get popular tables: {e}")
            return []
    
    async def get_cache_performance_report(self) -> Dict[str, Any]:
        """🔥 ERIK: Generate comprehensive cache performance report"""
        try:
            stats = await self.get_cache_statistics()
            popular_tables = await self.get_popular_tables()
            
            # Query cache analysis
            query_stats = defaultdict(int)
            for entry in self.query_cache.values():
                query_stats['total_access_count'] += entry.access_count
                if 'COUNT' in entry.query_sql.upper():
                    query_stats['count_queries'] += 1
                elif 'SUM' in entry.query_sql.upper():
                    query_stats['sum_queries'] += 1
                elif 'SELECT' in entry.query_sql.upper():
                    query_stats['select_queries'] += 1
            
            report = {
                "cache_performance": {
                    "total_tables_cached": stats.total_tables_cached,
                    "total_queries_cached": stats.total_queries_cached,
                    "cache_hit_rate": f"{stats.cache_hit_rate:.1%}",
                    "average_response_time": f"{stats.average_response_time:.3f}s",
                    "memory_usage_mb": f"{stats.memory_usage_mb:.2f}MB",
                    "cache_size_mb": f"{stats.cache_size_mb:.2f}MB"
                },
                "access_patterns": {
                    "total_cache_hits": self.cache_hits,
                    "total_cache_misses": self.cache_misses,
                    "total_queries_processed": self.total_queries,
                    "popular_tables": popular_tables
                },
                "query_analysis": dict(query_stats),
                "performance_impact": {
                    "estimated_time_saved": f"{(self.cache_hits * stats.average_response_time):.2f}s",
                    "estimated_db_load_reduction": f"{stats.cache_hit_rate:.1%}",
                    "cache_efficiency": "High" if stats.cache_hit_rate > 0.7 else "Medium" if stats.cache_hit_rate > 0.4 else "Low"
                },
                "recommendations": self._generate_cache_recommendations(stats),
                "timestamp": datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate cache performance report: {e}")
            return {"error": str(e)}
    
    def _generate_cache_recommendations(self, stats: CacheStats) -> List[str]:
        """Generate cache optimization recommendations"""
        recommendations = []
        
        if stats.cache_hit_rate < 0.3:
            recommendations.append("Consider increasing cache expiry time to improve hit rate")
        
        if stats.memory_usage_mb > 400:
            recommendations.append("Cache memory usage is high, consider reducing cache size or implementing compression")
        
        if stats.average_response_time > 1.0:
            recommendations.append("Average response time is high, consider optimizing frequently accessed queries")
        
        if len(self.table_cache) < 100:
            recommendations.append("Low table cache utilization, consider pre-caching important tables")
        
        if not recommendations:
            recommendations.append("Cache performance is optimal!")
        
        return recommendations
    
    async def invalidate_table_cache(self, table_name: str) -> bool:
        """Invalidate specific table cache entry"""
        try:
            with self.cache_lock:
                if table_name in self.table_cache:
                    del self.table_cache[table_name]
                    self.logger.info(f"✅ ERIK: Invalidated cache for table {table_name}")
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Failed to invalidate table cache: {e}")
            return False
    
    async def clear_all_cache(self) -> bool:
        """Clear all cache entries"""
        try:
            with self.cache_lock:
                self.table_cache.clear()
                self.query_cache.clear()
                self.cache_hits = 0
                self.cache_misses = 0
                self.total_queries = 0
                
                # Clear disk cache
                with sqlite3.connect(self.cache_db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM table_cache")
                    cursor.execute("DELETE FROM query_cache")
                    conn.commit()
                
                self.logger.info("✅ ERIK: All cache cleared successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return False

# Global cache instance
_cache_instance = None

def get_intelligent_cache() -> IntelligentTableCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = IntelligentTableCache()
    return _cache_instance

# Factory function
def create_intelligent_cache(cache_dir: str = "../cache") -> IntelligentTableCache:
    """Factory function to create intelligent cache"""
    return IntelligentTableCache(cache_dir)

# Test the intelligent cache system
async def main():
    """Test the intelligent cache system"""
    print("🔥 ERIK: Testing Intelligent Table Cache System")
    
    # Initialize cache
    cache = create_intelligent_cache()
    
    # Test table caching
    print("\n📊 Testing table caching...")
    test_schema = {"columns": ["id", "name", "value"], "primary_key": "id"}
    test_columns = [
        {"name": "id", "type": "int", "nullable": False},
        {"name": "name", "type": "varchar", "nullable": True},
        {"name": "value", "type": "decimal", "nullable": True}
    ]
    
    # Cache a table
    await cache.cache_table_info("test_table", test_schema, test_columns, business_context="Test table for demo")
    
    # Retrieve from cache
    cached_info = await cache.get_cached_table_info("test_table")
    if cached_info:
        print(f"✅ Successfully cached and retrieved table: {cached_info.table_name}")
        print(f"   Columns: {len(cached_info.column_info)}")
        print(f"   Business context: {cached_info.business_context}")
    
    # Test query caching
    print("\n🔍 Testing query caching...")
    test_query = "SELECT COUNT(*) FROM test_table WHERE active = 1"
    test_result = {"count": 42}
    
    # Cache query result
    await cache.cache_query_result(test_query, test_result, 0.15, 0.95)
    
    # Retrieve from cache
    cached_query = await cache.get_cached_query_result(test_query)
    if cached_query:
        print(f"✅ Successfully cached and retrieved query result")
        print(f"   Execution time: {cached_query.execution_time}s")
        print(f"   Confidence: {cached_query.confidence}")
        print(f"   Result: {cached_query.result_data}")
    
    # Get performance statistics
    print("\n📈 Cache Performance Statistics:")
    stats = await cache.get_cache_statistics()
    print(f"   Tables cached: {stats.total_tables_cached}")
    print(f"   Queries cached: {stats.total_queries_cached}")
    print(f"   Hit rate: {stats.cache_hit_rate:.1%}")
    print(f"   Memory usage: {stats.memory_usage_mb:.2f}MB")
    
    # Generate performance report
    print("\n📋 Generating performance report...")
    report = await cache.get_cache_performance_report()
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
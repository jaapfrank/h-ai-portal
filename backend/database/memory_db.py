"""
Database setup voor user context en memory management
Ondersteunt PostgreSQL met pgvector voor vector storage
"""
import os
import logging
from typing import Optional
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.user_context import Base
from ..core.config import get_config

logger = logging.getLogger(__name__)


class MemoryDatabaseManager:
    """
    Database manager voor user context en memory storage
    Gebruikt PostgreSQL met pgvector extensie
    """
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialiseer database connectie"""
        try:
            # Database URL samenstellen
            db_url = self._get_database_url()
            
            # Engine configureren
            self.engine = create_engine(
                db_url,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                echo=False  # Set to True voor SQL debugging
            )
            
            # Session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Test connectie
            self._test_connection()
            
            logger.info("Memory database succesvol geïnitialiseerd")
            
        except Exception as e:
            logger.error(f"Fout bij database initialisatie: {e}")
            raise
    
    def _get_database_url(self) -> str:
        """Verkrijg database URL van environment variables"""
        # Database configuratie van environment variables
        db_host = os.getenv("MEMORY_DB_HOST", "localhost")
        db_port = os.getenv("MEMORY_DB_PORT", "5432")
        db_name = os.getenv("MEMORY_DB_NAME", "hoeflon_memory")
        db_user = os.getenv("MEMORY_DB_USER", "hoeflon_user")
        db_password = os.getenv("MEMORY_DB_PASSWORD", "")
        
        if not db_password:
            logger.warning("MEMORY_DB_PASSWORD niet ingesteld")
        
        # PostgreSQL URL
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        return db_url
    
    def _test_connection(self):
        """Test database connectie"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Database connectie test geslaagd")
        except Exception as e:
            logger.error(f"Database connectie test gefaald: {e}")
            raise
    
    def create_tables(self):
        """Creëer alle tabellen"""
        try:
            # Check of pgvector extensie beschikbaar is
            self._ensure_pgvector_extension()
            
            # Creëer tabellen
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Database tabellen succesvol gecreëerd")
            
        except Exception as e:
            logger.error(f"Fout bij creëren tabellen: {e}")
            raise
    
    def _ensure_pgvector_extension(self):
        """Zorg dat pgvector extensie beschikbaar is"""
        try:
            with self.engine.connect() as conn:
                # Probeer pgvector extensie te maken (vereist superuser privileges)
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    conn.commit()
                    logger.info("pgvector extensie beschikbaar")
                except SQLAlchemyError as e:
                    # Extensie misschien al aanwezig of geen privileges
                    logger.warning(f"Kon pgvector extensie niet maken: {e}")
                    
                    # Check of extensie al bestaat
                    result = conn.execute(text(
                        "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
                    ))
                    if result.fetchone():
                        logger.info("pgvector extensie al beschikbaar")
                    else:
                        logger.error("pgvector extensie niet beschikbaar en kan niet worden geïnstalleerd")
                        
        except Exception as e:
            logger.error(f"Fout bij controleren pgvector extensie: {e}")
            # Niet fataal - systeem kan werken zonder vector support
    
    def get_session(self) -> Session:
        """Verkrijg nieuwe database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database niet geïnitialiseerd")
        return self.SessionLocal()
    
    @contextmanager
    def get_session_context(self):
        """Context manager voor database session"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def health_check(self) -> dict:
        """Database health check"""
        try:
            with self.get_session_context() as session:
                # Test query
                result = session.execute(text("SELECT 1 as health_check"))
                result.fetchone()
                
                # Check tabellen
                tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('user_contexts', 'user_sessions', 'user_preferences')
                """)
                tables = session.execute(tables_query).fetchall()
                table_names = [row[0] for row in tables]
                
                # Check pgvector
                vector_check = text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                vector_result = session.execute(vector_check).fetchone()
                
                return {
                    "status": "healthy",
                    "tables": table_names,
                    "pgvector_available": bool(vector_result),
                    "connection": "ok"
                }
                
        except Exception as e:
            logger.error(f"Database health check gefaald: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection": "failed"
            }
    
    def migrate_database(self):
        """Voer database migraties uit"""
        try:
            # Voor nu gewoon alle tabellen creëren
            # Later kunnen we Alembic gebruiken voor migrations
            self.create_tables()
            logger.info("Database migratie voltooid")
            
        except Exception as e:
            logger.error(f"Database migratie gefaald: {e}")
            raise
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Maak database backup (placeholder voor productie)
        
        Args:
            backup_path: Pad waar backup moet worden opgeslagen
            
        Returns:
            Success status
        """
        try:
            # In productie zou dit pg_dump gebruiken
            logger.info(f"Database backup naar {backup_path} (placeholder)")
            return True
            
        except Exception as e:
            logger.error(f"Database backup gefaald: {e}")
            return False
    
    def close(self):
        """Sluit database connecties"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connecties gesloten")


# Singleton instance
_memory_db_instance: Optional[MemoryDatabaseManager] = None

def get_memory_db() -> MemoryDatabaseManager:
    """Verkrijg singleton database manager instance"""
    global _memory_db_instance
    if _memory_db_instance is None:
        _memory_db_instance = MemoryDatabaseManager()
    return _memory_db_instance

def get_db_session() -> Session:
    """Helper functie voor database session"""
    return get_memory_db().get_session()

@contextmanager
def get_db_context():
    """Helper context manager voor database sessie"""
    with get_memory_db().get_session_context() as session:
        yield session
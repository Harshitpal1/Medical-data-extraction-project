"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging

from config import get_config
from src.database.models import Base

logger = logging.getLogger(__name__)
config = get_config()


class DatabaseManager:
    """Database manager for connection and session handling"""
    
    def __init__(self, database_url: str = None):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL
        """
        self.database_url = database_url or config.DATABASE_URL
        
        # Create engine
        if self.database_url.startswith("sqlite"):
            # SQLite specific configuration
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            # PostgreSQL configuration
            self.engine = create_engine(
                self.database_url,
                pool_size=config.DATABASE_POOL_SIZE,
                max_overflow=config.DATABASE_MAX_OVERFLOW,
            )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        
        logger.info(f"Database engine created for {self.database_url}")
    
    def create_tables(self):
        """Create all tables in the database"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """Drop all tables in the database"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """
        Get a database session
        
        Returns:
            SQLAlchemy session
        """
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope for database operations
        
        Yields:
            SQLAlchemy session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()


# Global database manager instance
db_manager = None


def init_db(database_url: str = None):
    """
    Initialize database
    
    Args:
        database_url: Database connection URL
    """
    global db_manager
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()


def get_db():
    """
    Dependency for getting database session
    
    Yields:
        Database session
    """
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()

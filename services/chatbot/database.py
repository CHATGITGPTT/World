# app/database.py
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Float, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/chatbotdb")

# Create engine with connection pooling and timeout settings
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    intent = Column(String(100), index=True)
    intent_confidence = Column(Float)
    sentiment = Column(String(50), index=True)
    sentiment_score = Column(Float)
    entities = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    response_time = Column(Float)
    
    # Add indexes for better query performance
    __table_args__ = (
        Index('idx_session_timestamp', 'session_id', 'timestamp'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )

class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_id = Column(String(255), index=True, nullable=False)
    rating = Column(Integer, nullable=False)
    feedback_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), index=True, nullable=False)
    metric_value = Column(Float, nullable=False)
    dimensions = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

def get_db():
    """Database dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
            logger.info("Database connection successful")
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        raise

def check_db_health():
    """Check database health status"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

# Initialize database on import (only in development)
if os.getenv("ENVIRONMENT", "development") == "development":
    try:
        init_db()
    except Exception as e:
        logger.warning(f"Database initialization failed: {str(e)}")
        logger.warning("Tables will be created when first accessed")

"""
Database configuration and session management for StarHub Customer Communications Generator.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
import pathlib

# Load environment variables from backend/.env
env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Database URL from environment or default to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./starhub_comms.db")

# Create SQLAlchemy engine
# For SQLite, we need to enable foreign key support and check same thread
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL debugging
    )
else:
    engine = create_engine(DATABASE_URL, echo=False)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields:
        Session: SQLAlchemy database session

    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.

    This function creates all tables defined in the models if they don't exist.
    It should be called on application startup.
    """
    # Import all models to ensure they are registered with Base
    from app.models import (
        Campaign,
        GeneratedCommunication,
        ErrorLog,
        PromotionUpload
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def drop_all_tables() -> None:
    """
    Drop all tables from the database.

    WARNING: This will delete all data. Use only for testing or reset scenarios.
    """
    Base.metadata.drop_all(bind=engine)
    print("All database tables dropped")


def reset_db() -> None:
    """
    Reset database by dropping all tables and recreating them.

    WARNING: This will delete all data. Use only for testing or reset scenarios.
    """
    drop_all_tables()
    init_db()
    print("Database reset completed")

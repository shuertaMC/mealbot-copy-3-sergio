"""Database module for SQLAlchemy engine and session management.

This module provides database connectivity using SQLAlchemy 2.0+,
replacing Go's database/sql with lib/pq driver pattern.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from .config import get_settings

# SQLAlchemy Base class for ORM models
Base = declarative_base()

# Create engine with connection pooling
# pool_pre_ping ensures connections are valid before use
_settings = get_settings()
engine = create_engine(
    _settings.database_url,
    pool_pre_ping=True,
)

# Session factory configured for explicit transaction management
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session management.

    Yields a database session and ensures it is closed after use.
    This pattern matches the Go code's approach of creating a new
    connection for each handler and closing it after use.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

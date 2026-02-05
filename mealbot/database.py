"""Database engine and session management using SQLAlchemy."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from mealbot.config import settings

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Enable connection health checks
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session.

    The session is automatically closed after the request is complete.

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

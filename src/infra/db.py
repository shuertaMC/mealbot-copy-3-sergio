"""Database engine, session factory, and FastAPI dependency for SQLAlchemy."""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from infra.config import get_settings

_engine = None
_SessionLocal = None


def _get_engine():
    """Return a lazily-initialized SQLAlchemy engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.sqlalchemy_database_url,
            pool_pre_ping=True,
        )
    return _engine


def _get_session_factory():
    """Return a lazily-initialized session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=_get_engine(),
        )
    return _SessionLocal


def get_db() -> Generator[Session, Any, None]:
    """FastAPI dependency that yields a SQLAlchemy session per request.

    The session is automatically closed after the request completes.
    Usage in route handlers::

        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    session_factory = _get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

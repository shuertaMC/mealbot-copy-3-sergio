"""Test fixtures for the mealbot test suite.

Provides:
- In-memory SQLite database for testing (no PostgreSQL required)
- FastAPI test client with database dependency override
- Database session fixture for unit tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from infra.db import get_db
from infra.models import Base
from mealbot_api.main import create_app

# Use in-memory SQLite for tests (no PostgreSQL required)
SQLALCHEMY_DATABASE_URL = "sqlite://"


@pytest.fixture
def engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(engine):
    """Create a fresh database session for each test."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(engine):
    """Create a FastAPI test client with overridden database dependency."""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

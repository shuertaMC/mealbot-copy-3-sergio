"""
Pytest fixtures for the mealbot test suite.

Provides a Flask test app and client configured for testing.
Authentication is disabled in test mode.
"""

import pytest

from mealbot.app import create_app


@pytest.fixture
def app():
    """Create a Flask application configured for testing."""
    app = create_app(test_config={"TESTING": True})
    app.config["SERVER_NAME"] = "localhost"
    yield app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Provide an application context for tests that need it."""
    with app.app_context():
        yield app

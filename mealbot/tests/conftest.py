"""
Shared pytest fixtures for mealbot tests.
"""

import pytest

from mealbot.app import create_app


@pytest.fixture
def app():
    """Create a Flask application instance for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()

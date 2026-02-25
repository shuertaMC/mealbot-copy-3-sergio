"""
Tests for the JWT authentication middleware.

Tests that the auth middleware correctly validates tokens,
rejects invalid tokens, and passes through OPTIONS requests.
Note: In normal test mode, auth is skipped. These tests use
a separate app fixture with auth enabled.
"""

from unittest.mock import MagicMock, patch

import pytest

from mealbot.app import create_app


@pytest.fixture
def auth_app():
    """Create a Flask app with authentication enabled for testing."""
    app = create_app(test_config={"TESTING": False})
    app.config["SERVER_NAME"] = "localhost"
    return app


@pytest.fixture
def auth_client(auth_app):
    """Create a test client with authentication enabled."""
    return auth_app.test_client()


class TestAuthMiddleware:
    """Tests for JWT authentication behavior."""

    def test_options_passes_through(self, auth_client):
        """Test that OPTIONS requests pass through without auth."""
        response = auth_client.options(
            "/orgs",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        # OPTIONS should not be blocked by auth
        assert response.status_code == 200

    def test_static_files_pass_through(self, auth_client):
        """Test that static file requests pass through without auth."""
        response = auth_client.get("/")
        assert response.status_code == 200

    def test_missing_auth_header_returns_401(self, auth_client):
        """Test that missing Authorization header returns 401."""
        response = auth_client.get("/orgs?admin=test@example.com")
        assert response.status_code == 401
        data = response.get_json()
        assert data["Message"] == "No authorization header"

    def test_invalid_auth_header_format_returns_401(self, auth_client):
        """Test that invalid Authorization header format returns 401."""
        response = auth_client.get(
            "/orgs?admin=test@example.com",
            headers={"Authorization": "InvalidFormat"},
        )
        assert response.status_code == 401
        data = response.get_json()
        assert "Authorization header format" in data["Message"]

    def test_non_bearer_auth_returns_401(self, auth_client):
        """Test that non-Bearer auth type returns 401."""
        response = auth_client.get(
            "/orgs?admin=test@example.com",
            headers={"Authorization": "Basic abc123"},
        )
        assert response.status_code == 401

    @patch("mealbot.auth._get_jwks_client")
    def test_invalid_token_returns_401(self, mock_jwks, auth_client):
        """Test that an invalid JWT token returns 401."""
        mock_client = MagicMock()
        mock_client.get_signing_key_from_jwt.side_effect = Exception(
            "Invalid token"
        )
        mock_jwks.return_value = mock_client

        response = auth_client.get(
            "/orgs?admin=test@example.com",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    def test_health_endpoint_requires_auth_when_enabled(self, auth_client):
        """Test that non-static endpoints require auth."""
        response = auth_client.get("/health")
        assert response.status_code == 401

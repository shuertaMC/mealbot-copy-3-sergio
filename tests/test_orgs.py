"""
Tests for the Organization API handlers.

Tests the HTTP endpoints for organization management by mocking
the database layer. Validates request/response format, status codes,
and error handling to ensure parity with the Go implementation.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestGetOrganizationsHandler:
    """Tests for GET /orgs endpoint."""

    @patch("mealbot.models.orgs.get_db_connection")
    def test_success(self, mock_get_db, client):
        """Test successful fetch of organizations."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("org1",), ("org2",)]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/orgs?admin=test@example.com")

        assert response.status_code == 200
        data = response.get_json()
        assert data == {"orgs": ["org1", "org2"]}
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch("mealbot.models.orgs.get_db_connection")
    def test_empty_results(self, mock_get_db, client):
        """Test fetch returns empty list when no orgs found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/orgs?admin=unknown@example.com")

        assert response.status_code == 200
        data = response.get_json()
        assert data == {"orgs": []}

    def test_missing_admin_param(self, client):
        """Test that missing admin param returns 400."""
        response = client.get("/orgs")

        assert response.status_code == 400
        data = response.get_json()
        assert "Message" in data
        assert "admin" in data["Message"]

    def test_multiple_admin_params(self, client):
        """Test that multiple admin params returns 400."""
        response = client.get("/orgs?admin=a&admin=b")

        assert response.status_code == 400

    @patch("mealbot.models.orgs.get_db_connection")
    def test_db_error(self, mock_get_db, client):
        """Test that database error returns 500."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB connection failed")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.get("/orgs?admin=test@example.com")

        assert response.status_code == 500
        data = response.get_json()
        assert "Message" in data


class TestCreateOrganizationHandler:
    """Tests for POST /org endpoint."""

    @patch("mealbot.models.orgs.get_db_connection")
    def test_success(self, mock_get_db, client):
        """Test successful organization creation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/org?admin=test@example.com",
            json={"org": "test-org"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["Message"] == "Successfully created new organization"
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_missing_admin_param(self, client):
        """Test that missing admin param returns 400."""
        response = client.post(
            "/org",
            json={"org": "test-org"},
        )

        assert response.status_code == 400

    @patch("mealbot.models.orgs.get_db_connection")
    def test_empty_org_name(self, mock_get_db, client):
        """Test that empty org name returns 500 (ValueError from create)."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/org?admin=test@example.com",
            json={"org": ""},
        )

        assert response.status_code == 500
        data = response.get_json()
        assert "Message" in data

    @patch("mealbot.models.orgs.get_db_connection")
    def test_db_error(self, mock_get_db, client):
        """Test that database error returns 500."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Duplicate key")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/org?admin=test@example.com",
            json={"org": "existing-org"},
        )

        assert response.status_code == 500


class TestCrossMatchTraitHandler:
    """Tests for POST /crossmatchtrait endpoint."""

    @patch("mealbot.models.orgs.get_db_connection")
    def test_success(self, mock_get_db, client):
        """Test successful cross-match trait setting."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/crossmatchtrait?org=test-org",
            json={"trait": "college"},
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["Message"] == "Successfully set the cross match trait"
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_missing_org_param(self, client):
        """Test that missing org param returns 400."""
        response = client.post(
            "/crossmatchtrait",
            json={"trait": "college"},
        )

        assert response.status_code == 400

    @patch("mealbot.models.orgs.get_db_connection")
    def test_db_error(self, mock_get_db, client):
        """Test that database error returns 500."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        response = client.post(
            "/crossmatchtrait?org=test-org",
            json={"trait": "college"},
        )

        assert response.status_code == 500


class TestGetCrossMatchTrait:
    """Tests for the get_cross_match_trait database function."""

    @patch("mealbot.models.orgs.get_db_connection")
    def test_returns_trait(self, mock_get_db, app):
        """Test that get_cross_match_trait returns the trait value."""
        from mealbot.models.orgs import get_cross_match_trait

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("college",)
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        with app.app_context():
            result = get_cross_match_trait("test-org")

        assert result == "college"

    @patch("mealbot.models.orgs.get_db_connection")
    def test_returns_empty_for_null(self, mock_get_db, app):
        """Test that NULL trait returns empty string."""
        from mealbot.models.orgs import get_cross_match_trait

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (None,)
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        with app.app_context():
            result = get_cross_match_trait("test-org")

        assert result == ""

    @patch("mealbot.models.orgs.get_db_connection")
    def test_returns_empty_for_no_rows(self, mock_get_db, app):
        """Test that no rows returns empty string."""
        from mealbot.models.orgs import get_cross_match_trait

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        with app.app_context():
            result = get_cross_match_trait("nonexistent-org")

        assert result == ""

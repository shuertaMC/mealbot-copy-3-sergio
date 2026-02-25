"""Tests for Organization API endpoints and the app factory.

Validates:
- App factory creates a valid Flask app
- GET /orgs returns organizations for a given admin
- POST /org creates a new organization
- POST /crossmatchtrait sets a cross-match trait
- Static file serving at /
- Error cases: missing params, wrong HTTP methods
"""

import json
from unittest.mock import patch, MagicMock

import pytest

from mealbot.app import create_app


@pytest.fixture
def app():
    """Create a Flask test app with TESTING=True (auth disabled)."""
    app = create_app(test_config={"TESTING": True})
    return app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()


class TestAppFactory:
    def test_create_app_returns_flask_app(self):
        app = create_app(test_config={"TESTING": True})
        assert app is not None
        assert app.config["TESTING"] is True

    def test_static_file_serving(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert b"Privacy Policy" in response.data


class TestGetOrganizations:
    @patch("mealbot.models.orgs.get_db_connection")
    def test_get_orgs_success(self, mock_db_conn, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("org1",), ("org2",)]
        mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_db_conn.return_value = mock_conn

        response = client.get("/orgs?admin=test@example.com")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == {"orgs": ["org1", "org2"]}

    def test_get_orgs_missing_admin(self, client):
        response = client.get("/orgs")
        assert response.status_code == 400

    @patch("mealbot.models.orgs.get_db_connection")
    def test_get_orgs_empty_result(self, mock_db_conn, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_db_conn.return_value = mock_conn

        response = client.get("/orgs?admin=nobody@example.com")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == {"orgs": []}


class TestCreateOrganization:
    @patch("mealbot.models.orgs.get_db_connection")
    def test_create_org_success(self, mock_db_conn, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_db_conn.return_value = mock_conn

        response = client.post(
            "/org?admin=test@example.com",
            data=json.dumps({"org": "testorg"}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["Message"] == "Successfully created new organization"

    def test_create_org_missing_admin(self, client):
        response = client.post(
            "/org",
            data=json.dumps({"org": "testorg"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    @patch("mealbot.models.orgs.get_db_connection")
    def test_create_org_empty_name(self, mock_db_conn, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_db_conn.return_value = mock_conn

        response = client.post(
            "/org?admin=test@example.com",
            data=json.dumps({"org": ""}),
            content_type="application/json",
        )
        assert response.status_code == 500


class TestCrossMatchTrait:
    @patch("mealbot.models.orgs.get_db_connection")
    def test_set_cross_match_trait_success(self, mock_db_conn, client):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_db_conn.return_value = mock_conn

        response = client.post(
            "/crossmatchtrait?org=testorg",
            data=json.dumps({"trait": "college"}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["Message"] == "Successfully set the cross match trait"

    def test_set_cross_match_trait_missing_org(self, client):
        response = client.post(
            "/crossmatchtrait",
            data=json.dumps({"trait": "college"}),
            content_type="application/json",
        )
        assert response.status_code == 400

"""
Tests for organization endpoints and related functionality.

Tests use mocked database connections so they can run without a real
PostgreSQL instance. Tests verify HTTP behavior, response shapes,
status codes, method validation, and CORS headers.
"""

import json
from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# GET /orgs tests
# ---------------------------------------------------------------------------


class TestGetOrganizationsHandler:
    """Tests for GET /orgs endpoint."""

    @patch("mealbot.models.orgs.get_db_connection")
    def test_get_orgs_success(self, mock_get_conn, client):
        """GET /orgs?admin=<email> returns list of org names."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("org1",), ("org2",)]
        mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        resp = client.get("/orgs?admin=test@example.com")

        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "orgs" in data
        assert data["orgs"] == ["org1", "org2"]

    @patch("mealbot.models.orgs.get_db_connection")
    def test_get_orgs_empty(self, mock_get_conn, client):
        """GET /orgs with valid admin but no orgs returns empty list."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        resp = client.get("/orgs?admin=test@example.com")

        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["orgs"] == []

    def test_get_orgs_missing_admin_param(self, client):
        """GET /orgs without admin param returns 400."""
        resp = client.get("/orgs")

        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert "Message" in data
        assert "admin" in data["Message"].lower()

    def test_get_orgs_duplicate_admin_param(self, client):
        """GET /orgs with multiple admin params returns 400."""
        resp = client.get("/orgs?admin=a@b.com&admin=c@d.com")

        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert "Message" in data

    @patch("mealbot.models.orgs.get_db_connection")
    def test_get_orgs_db_error(self, mock_get_conn, client):
        """GET /orgs returns 500 on database errors."""
        mock_get_conn.side_effect = Exception("Connection failed")

        resp = client.get("/orgs?admin=test@example.com")

        assert resp.status_code == 500
        data = json.loads(resp.data)
        assert "Message" in data


# ---------------------------------------------------------------------------
# POST /org tests
# ---------------------------------------------------------------------------


class TestCreateOrganizationHandler:
    """Tests for POST /org endpoint."""

    @patch("mealbot.models.orgs.get_db_connection")
    def test_create_org_success(self, mock_get_conn, client):
        """POST /org creates organization and returns 201."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        resp = client.post(
            "/org?admin=test@example.com",
            data=json.dumps({"org": "testorg"}),
            content_type="application/json",
        )

        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert "Message" in data
        assert "Successfully created new organization" in data["Message"]

    def test_create_org_missing_admin(self, client):
        """POST /org without admin param returns 400."""
        resp = client.post(
            "/org",
            data=json.dumps({"org": "testorg"}),
            content_type="application/json",
        )

        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert "Message" in data

    def test_create_org_bad_body(self, client):
        """POST /org with malformed JSON body returns 400."""
        resp = client.post(
            "/org?admin=test@example.com",
            data="not json at all{{{",
            content_type="application/json",
        )

        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert "Message" in data

    @patch("mealbot.models.orgs.get_db_connection")
    def test_create_org_empty_name(self, mock_get_conn, client):
        """POST /org with empty org name returns 500 (ValueError from create_organization)."""
        # create_organization raises ValueError for empty name,
        # which is caught and returned as 500
        resp = client.post(
            "/org?admin=test@example.com",
            data=json.dumps({"org": ""}),
            content_type="application/json",
        )

        assert resp.status_code == 500
        data = json.loads(resp.data)
        assert "Message" in data
        assert "empty string" in data["Message"].lower() or "empty" in data["Message"].lower()

    def test_create_org_wrong_method(self, client):
        """GET /org returns 405 with error message (only POST allowed)."""
        resp = client.get("/org")

        assert resp.status_code == 405
        data = json.loads(resp.data)
        assert "Message" in data
        assert "POST" in data["Message"]


# ---------------------------------------------------------------------------
# POST /crossmatchtrait tests
# ---------------------------------------------------------------------------


class TestCrossMatchTraitHandler:
    """Tests for POST /crossmatchtrait endpoint."""

    @patch("mealbot.models.orgs.get_db_connection")
    def test_set_trait_success(self, mock_get_conn, client):
        """POST /crossmatchtrait sets trait and returns 201."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        resp = client.post(
            "/crossmatchtrait?org=testorg",
            data=json.dumps({"trait": "College"}),
            content_type="application/json",
        )

        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert "Message" in data
        assert "Successfully set the cross match trait" in data["Message"]

    def test_set_trait_missing_org(self, client):
        """POST /crossmatchtrait without org param returns 400."""
        resp = client.post(
            "/crossmatchtrait",
            data=json.dumps({"trait": "College"}),
            content_type="application/json",
        )

        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert "Message" in data

    def test_set_trait_bad_body(self, client):
        """POST /crossmatchtrait with malformed body returns 400."""
        resp = client.post(
            "/crossmatchtrait?org=testorg",
            data="not json",
            content_type="application/json",
        )

        assert resp.status_code == 400

    def test_set_trait_missing_trait_key(self, client):
        """POST /crossmatchtrait without 'trait' key in body returns 400."""
        resp = client.post(
            "/crossmatchtrait?org=testorg",
            data=json.dumps({"wrong_key": "value"}),
            content_type="application/json",
        )

        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert "Message" in data

    def test_set_trait_wrong_method(self, client):
        """GET /crossmatchtrait returns 405 with error message (only POST allowed)."""
        resp = client.get("/crossmatchtrait")

        assert resp.status_code == 405
        data = json.loads(resp.data)
        assert "Message" in data
        assert "POST" in data["Message"]


# ---------------------------------------------------------------------------
# CORS tests
# ---------------------------------------------------------------------------


class TestCorsHeaders:
    """Tests for CORS header behavior."""

    @patch("mealbot.models.orgs.get_db_connection")
    def test_cors_origin_echoed(self, mock_get_conn, client):
        """CORS: Origin header is echoed back in Access-Control-Allow-Origin."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.cursor.return_value.__enter__ = lambda s: mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        origin = "https://mealbot-web.herokuapp.com"
        resp = client.get(
            "/orgs?admin=test@example.com",
            headers={"Origin": origin},
        )

        assert resp.headers.get("Access-Control-Allow-Origin") == origin

    def test_cors_allowed_methods(self, client):
        """CORS: Access-Control-Allow-Methods includes GET, POST, DELETE."""
        resp = client.options("/orgs", headers={"Origin": "http://localhost:3000"})

        methods = resp.headers.get("Access-Control-Allow-Methods", "")
        assert "GET" in methods
        assert "POST" in methods
        assert "DELETE" in methods

    def test_cors_allowed_headers(self, client):
        """CORS: Access-Control-Allow-Headers includes Authorization, Content-Type, etc."""
        resp = client.options("/orgs", headers={"Origin": "http://localhost:3000"})

        headers = resp.headers.get("Access-Control-Allow-Headers", "")
        assert "Authorization" in headers
        assert "Content-Type" in headers
        assert "Origin" in headers
        assert "Accept" in headers
        assert "token" in headers

    def test_cors_preflight_returns_200(self, client):
        """CORS: OPTIONS preflight requests return 200."""
        resp = client.options("/orgs", headers={"Origin": "http://localhost:3000"})

        assert resp.status_code == 200

    def test_cors_different_origins(self, client):
        """CORS: Different origin values are echoed correctly."""
        for origin in ["http://localhost:3000", "https://example.com", "https://app.test.io"]:
            resp = client.options("/orgs", headers={"Origin": origin})
            assert resp.headers.get("Access-Control-Allow-Origin") == origin


# ---------------------------------------------------------------------------
# Static file tests
# ---------------------------------------------------------------------------


class TestStaticFiles:
    """Tests for static file serving."""

    def test_root_serves_privacy_html(self, client):
        """GET / serves privacy.html."""
        resp = client.get("/")

        assert resp.status_code == 200
        assert b"Privacy Policy" in resp.data

    def test_sample_csv_accessible(self, client):
        """GET /sample.csv serves the sample CSV file."""
        resp = client.get("/sample.csv")

        assert resp.status_code == 200
        assert b"Name,Email" in resp.data

    def test_nonexistent_static_returns_404(self, client):
        """GET /nonexistent.txt returns 404."""
        resp = client.get("/nonexistent.txt")

        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Utils tests
# ---------------------------------------------------------------------------


class TestUtils:
    """Tests for utility functions."""

    def test_str_to_bytes(self):
        """str_to_bytes produces correct JSON format."""
        from mealbot.utils import str_to_bytes

        result = json.loads(str_to_bytes("Hello"))
        assert result == {"Message": "Hello"}

    def test_err_to_bytes(self):
        """err_to_bytes produces correct JSON format."""
        from mealbot.utils import err_to_bytes

        result = json.loads(err_to_bytes(ValueError("test error")))
        assert result == {"Message": "test error"}

    def test_err_to_bytes_string(self):
        """err_to_bytes works with string input."""
        from mealbot.utils import err_to_bytes

        result = json.loads(err_to_bytes("some error"))
        assert result == {"Message": "some error"}

    def test_get_query_param_success(self, app):
        """get_query_param returns value for valid single param."""
        from mealbot.utils import get_query_param

        with app.test_request_context("/test?key=value"):
            value, err = get_query_param("key")
            assert value == "value"
            assert err is None

    def test_get_query_param_missing(self, app):
        """get_query_param returns error for missing param."""
        from mealbot.utils import get_query_param

        with app.test_request_context("/test"):
            value, err = get_query_param("key")
            assert value is None
            assert err is not None
            assert "key" in err

    def test_get_query_param_multiple(self, app):
        """get_query_param returns error for multiple values."""
        from mealbot.utils import get_query_param

        with app.test_request_context("/test?key=a&key=b"):
            value, err = get_query_param("key")
            assert value is None
            assert err is not None

    def test_get_query_params_success(self, app):
        """get_query_params returns values for valid params."""
        from mealbot.utils import get_query_params

        with app.test_request_context("/test?a=1&b=2"):
            values, err = get_query_params(["a", "b"])
            assert values == ["1", "2"]
            assert err is None

    def test_get_query_params_missing(self, app):
        """get_query_params returns error for missing key."""
        from mealbot.utils import get_query_params

        with app.test_request_context("/test?a=1"):
            values, err = get_query_params(["a", "b"])
            assert values == []
            assert err is not None
            assert "b" in err


# ---------------------------------------------------------------------------
# Database module tests
# ---------------------------------------------------------------------------


class TestDbModule:
    """Tests for the database connection module."""

    @patch.dict("os.environ", {"DATABASE_URL": "postgres://user:pass@host:5432/db"})
    @patch("mealbot.db.psycopg2.connect")
    def test_postgres_url_normalized(self, mock_connect):
        """DATABASE_URL with postgres:// scheme is normalized to postgresql://."""
        from mealbot.db import get_db_connection

        mock_connect.return_value = MagicMock()
        get_db_connection()

        call_args = mock_connect.call_args[0][0]
        assert call_args.startswith("postgresql://")
        assert not call_args.startswith("postgres://")

    @patch.dict("os.environ", {"DATABASE_URL": "postgresql://user:pass@host:5432/db"})
    @patch("mealbot.db.psycopg2.connect")
    def test_postgresql_url_unchanged(self, mock_connect):
        """DATABASE_URL with postgresql:// scheme is used as-is."""
        from mealbot.db import get_db_connection

        mock_connect.return_value = MagicMock()
        get_db_connection()

        call_args = mock_connect.call_args[0][0]
        assert call_args == "postgresql://user:pass@host:5432/db"

    @patch.dict("os.environ", {}, clear=True)
    @patch("mealbot.db.psycopg2.connect")
    def test_local_fallback(self, mock_connect):
        """Without DATABASE_URL, falls back to local connection string."""
        from mealbot.db import get_db_connection

        mock_connect.return_value = MagicMock()
        get_db_connection()

        call_args = mock_connect.call_args[0][0]
        assert "johnamadeodaniswara" in call_args
        assert "mealbot" in call_args
        assert "sslmode=disable" in call_args

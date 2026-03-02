"""End-to-end tests for organization management endpoints.

Tests the full request/response cycle through the FastAPI app,
verifying behavioral parity with the Go application.
"""


class TestGetOrganizations:
    """Tests for GET /orgs endpoint."""

    def test_get_orgs_empty(self, client):
        """GET /orgs returns empty list when no organizations exist."""
        response = client.get("/orgs?admin=test@example.com")
        assert response.status_code == 200
        data = response.json()
        assert "orgs" in data
        assert data["orgs"] == []

    def test_get_orgs_missing_admin(self, client):
        """GET /orgs without admin param returns 400 with error message."""
        response = client.get("/orgs")
        assert response.status_code == 400
        data = response.json()
        assert "Message" in data
        assert "admin" in data["Message"].lower()

    def test_get_orgs_after_create(self, client):
        """GET /orgs returns created organizations."""
        # Create an organization first
        client.post(
            "/org?admin=test@example.com",
            json={"org": "testorg"},
        )

        response = client.get("/orgs?admin=test@example.com")
        assert response.status_code == 200
        data = response.json()
        assert "orgs" in data
        assert "testorg" in data["orgs"]

    def test_get_orgs_filters_by_admin(self, client):
        """GET /orgs only returns orgs for the specified admin."""
        client.post("/org?admin=admin1@example.com", json={"org": "org1"})
        client.post("/org?admin=admin2@example.com", json={"org": "org2"})

        response = client.get("/orgs?admin=admin1@example.com")
        data = response.json()
        assert "org1" in data["orgs"]
        assert "org2" not in data["orgs"]


class TestCreateOrganization:
    """Tests for POST /org endpoint."""

    def test_create_org_success(self, client):
        """POST /org creates organization and returns 201 with Message."""
        response = client.post(
            "/org?admin=test@example.com",
            json={"org": "neworg"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["Message"] == "Successfully created new organization"

    def test_create_org_missing_admin(self, client):
        """POST /org without admin param returns error."""
        response = client.post("/org", json={"org": "neworg"})
        data = response.json()
        assert "Message" in data
        assert "admin" in data["Message"].lower()

    def test_create_org_empty_name(self, client):
        """POST /org with empty org name returns error."""
        response = client.post(
            "/org?admin=test@example.com",
            json={"org": ""},
        )
        data = response.json()
        assert "Message" in data

    def test_create_org_missing_body(self, client):
        """POST /org without body returns 422 validation error."""
        response = client.post("/org?admin=test@example.com")
        assert response.status_code == 422


class TestCrossMatchTrait:
    """Tests for POST /crossmatchtrait endpoint."""

    def test_set_cross_match_trait_success(self, client):
        """POST /crossmatchtrait sets trait and returns 201."""
        # Create org first
        client.post(
            "/org?admin=test@example.com",
            json={"org": "testorg"},
        )

        response = client.post(
            "/crossmatchtrait?org=testorg",
            json={"trait": "college"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["Message"] == "Successfully set the cross match trait"

    def test_set_cross_match_trait_missing_org(self, client):
        """POST /crossmatchtrait without org param returns error."""
        response = client.post(
            "/crossmatchtrait",
            json={"trait": "college"},
        )
        data = response.json()
        assert "Message" in data

    def test_set_cross_match_trait_missing_body(self, client):
        """POST /crossmatchtrait without body returns 422."""
        response = client.post("/crossmatchtrait?org=testorg")
        assert response.status_code == 422

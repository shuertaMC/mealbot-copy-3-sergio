"""
Tests for the Flask application factory and basic routes.

Validates that the app starts correctly, health check works,
static files are served, and CORS headers are present.
"""


def test_create_app(app):
    """Test that the app factory creates a valid Flask app."""
    assert app is not None
    assert app.config["TESTING"] is True


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"


def test_root_serves_static(client):
    """Test that the root route serves the privacy.html static file."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Privacy Policy" in response.data


def test_static_privacy_html(client):
    """Test that privacy.html is served from /static/."""
    response = client.get("/static/privacy.html")
    assert response.status_code == 200
    assert b"Privacy Policy" in response.data


def test_static_sample_csv(client):
    """Test that sample.csv is served from /static/."""
    response = client.get("/static/sample.csv")
    assert response.status_code == 200
    assert b"Name,Email" in response.data


def test_cors_headers_on_response(client):
    """Test that CORS headers are present on responses."""
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    # Flask-CORS should set Access-Control-Allow-Origin
    assert "Access-Control-Allow-Origin" in response.headers


def test_cors_preflight(client):
    """Test that OPTIONS preflight requests work correctly."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert "Access-Control-Allow-Methods" in response.headers


def test_404_for_unknown_routes(client):
    """Test that unknown routes return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404

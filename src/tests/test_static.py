"""Tests for static file serving."""


class TestStaticFiles:
    """Verify static files are served correctly at root path."""

    def test_privacy_html(self, client):
        """GET /privacy.html returns the privacy policy page."""
        response = client.get("/privacy.html")
        assert response.status_code == 200
        assert "Privacy Policy" in response.text
        assert "text/html" in response.headers.get("content-type", "")

    def test_sample_csv(self, client):
        """GET /sample.csv returns the sample CSV template."""
        response = client.get("/sample.csv")
        assert response.status_code == 200
        assert "Name,Email" in response.text

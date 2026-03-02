"""Tests for configuration module."""

from infra.config import Settings


class TestSettings:
    """Verify Settings class behavior."""

    def test_default_port(self):
        """Default port should be 8080, matching Go app default."""
        settings = Settings(database_url="postgresql://localhost/test")
        assert settings.port == 8080

    def test_default_database_url(self):
        """Default DATABASE_URL should be a local PostgreSQL URL."""
        settings = Settings()
        assert "postgresql" in settings.database_url

    def test_postgres_url_normalization(self):
        """postgres:// scheme should be normalized to postgresql://."""
        settings = Settings(database_url="postgres://user:pass@host:5432/db")
        assert settings.sqlalchemy_database_url == "postgresql://user:pass@host:5432/db"

    def test_postgresql_url_unchanged(self):
        """postgresql:// scheme should not be modified."""
        url = "postgresql://user:pass@host:5432/db"
        settings = Settings(database_url=url)
        assert settings.sqlalchemy_database_url == url

    def test_auth0_defaults(self):
        """Auth0 settings should have default values matching Go constants."""
        settings = Settings()
        assert settings.auth0_domain == "mealbot.auth0.com"
        assert settings.auth0_audience == "https://mealbot-2.herokuapp.com/"

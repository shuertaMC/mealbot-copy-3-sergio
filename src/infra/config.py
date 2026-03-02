"""Application configuration loaded from environment variables via pydantic-settings."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Mirrors the environment variables used by the Go application:
    - DATABASE_URL: PostgreSQL connection string (Heroku sets this automatically)
    - PORT: HTTP server port (default 8080, matching Go default)
    - Auth0 settings for JWT authentication (used in Milestone 3)
    - Mailgun settings for email delivery (used in Milestone 4)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql://localhost:5432/mealbot"

    # Server
    port: int = 8080

    # Auth0 (deferred to Milestone 3)
    auth0_domain: str = "mealbot.auth0.com"
    auth0_audience: str = "https://mealbot-2.herokuapp.com/"

    # Mailgun (deferred to Milestone 4)
    mailgun_domain: Optional[str] = None
    mailgun_api_key: Optional[str] = None
    mailgun_from: Optional[str] = None

    @property
    def sqlalchemy_database_url(self) -> str:
        """Return the database URL normalized for SQLAlchemy.

        Heroku sets DATABASE_URL with the 'postgres://' scheme, but SQLAlchemy 2.x
        requires 'postgresql://'. This property handles the conversion.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Uses lru_cache so the settings object is created once and reused.
    """
    return Settings()

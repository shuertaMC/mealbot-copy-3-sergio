"""Configuration management using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All configuration values can be set via environment variables or a .env file.
    The .env file is loaded automatically if present in the working directory.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server configuration
    port: int = 8080

    # Database configuration
    database_url: str = "postgresql+psycopg://localhost/mealbot"

    # Mailgun configuration
    mailgun_domain: str = ""
    mailgun_api_key: str = ""

    # Auth0 configuration
    auth0_issuer: str = "https://mealbot.auth0.com/"
    auth0_audience: str = "https://mealbot-2.herokuapp.com/"
    auth0_jwks_url: str = "https://mealbot.auth0.com/.well-known/jwks.json"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Singleton settings instance for use by other modules
settings = get_settings()

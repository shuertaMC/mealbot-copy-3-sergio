"""Configuration module using Pydantic Settings.

This module provides centralized configuration management for the Mealbot application,
replacing Go's environment variable access patterns with Pydantic-settings.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        port: Server port (default: 8080)
        database_url: PostgreSQL connection string
        mailgun_smtp_login: Mailgun SMTP login credential
        mailgun_domain: Mailgun domain for sending emails
        mailgun_api_key: Mailgun API key
        auth0_issuer: Auth0 JWT issuer URL
        auth0_audience: Auth0 JWT audience
        auth0_jwks_url: Auth0 JWKS endpoint URL
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server configuration
    port: int = 8080

    # Database configuration (required - must be set via environment variable)
    database_url: str

    # Mailgun configuration
    mailgun_smtp_login: Optional[str] = None
    mailgun_domain: Optional[str] = None
    mailgun_api_key: Optional[str] = None

    # Auth0 configuration (defaults match Go constants in auth.go)
    auth0_issuer: str = "https://mealbot.auth0.com/"
    auth0_audience: str = "https://mealbot-2.herokuapp.com/"
    auth0_jwks_url: str = "https://mealbot.auth0.com/.well-known/jwks.json"


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings.

    Returns:
        Settings: Application settings instance
    """
    return Settings()

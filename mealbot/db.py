"""Database connection helper (migrated from db.go + vendor/dbconn.go)."""

import os

import psycopg2

# Error message when user tries to insert row with duplicate key
DUPLICATE_KEY_ERR = "duplicate key value violates unique constraint"


def get_db_connection():
    """Create and return a new psycopg2 database connection.

    Uses DATABASE_URL environment variable when available (Heroku production).
    Falls back to a local connection string otherwise.
    """
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)

    # Local development fallback
    return psycopg2.connect(
        user=os.environ.get("DB_USER", "johnamadeodaniswara"),
        dbname=os.environ.get("DB_NAME", "mealbot"),
        host=os.environ.get("DB_HOST", "localhost"),
        sslmode="disable",
    )

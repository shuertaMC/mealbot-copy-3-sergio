"""
Database connection helpers.

Ported from db.go + vendor/github.com/johnamadeo/server/dbconn.go.
Provides PostgreSQL connection management using psycopg2, with support
for Heroku's DATABASE_URL environment variable.
"""

import os
import logging

import psycopg2

logger = logging.getLogger(__name__)

# Error message substring for duplicate key constraint violations
# (matches Go constant DuplicateKeyErr)
DUPLICATE_KEY_ERR = "duplicate key value violates unique constraint"

# Local development defaults (mirrors Go LocalDBConnection struct)
LOCAL_DB_USER = "johnamadeodaniswara"
LOCAL_DB_NAME = "mealbot"


def get_db_connection():
    """
    Create and return a new psycopg2 database connection.

    In production (Heroku), uses the DATABASE_URL environment variable.
    In local development, constructs a connection string from defaults.

    Mirrors the behavior of server.CreateDBConnection() in Go.

    Returns:
        psycopg2 connection object
    """
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        # Heroku may use 'postgres://' scheme which psycopg2 doesn't support;
        # normalize to 'postgresql://'
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        dsn = database_url
    else:
        # Local development fallback (mirrors createLocalDBUrl in Go)
        dsn = f"user={LOCAL_DB_USER} dbname={LOCAL_DB_NAME} sslmode=disable"

    try:
        conn = psycopg2.connect(dsn)
        return conn
    except Exception as e:
        logger.error("Failed to connect to database: %s", e)
        raise

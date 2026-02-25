"""
Database connection helper.

Migrated from: db.go, vendor/github.com/johnamadeo/server/dbconn.go

Provides request-scoped PostgreSQL connections using psycopg2 and Flask's
g object. Connections are automatically closed at the end of each request
via teardown_appcontext.
"""

import os

import psycopg2
from flask import g


# Error message when user tries to insert row with duplicate key
DUPLICATE_KEY_ERR = "duplicate key value violates unique constraint"


def get_db_connection():
    """
    Get a database connection for the current request.

    If DATABASE_URL environment variable is set (e.g. on Heroku),
    use it directly. Otherwise, build a local connection string.

    Returns a psycopg2 connection stored on Flask's g object for
    request-scoped lifecycle management.
    """
    if "db" not in g:
        database_url = os.environ.get("DATABASE_URL")

        if database_url:
            g.db = psycopg2.connect(database_url)
        else:
            # Local development fallback
            g.db = psycopg2.connect(
                user=os.environ.get("DB_USER", ""),
                dbname=os.environ.get("DB_NAME", "mealbot"),
                host=os.environ.get("DB_HOST", "localhost"),
                port=os.environ.get("DB_PORT", "5432"),
                sslmode="disable",
            )

    return g.db


def close_db(e=None):
    """
    Close the database connection at the end of the request.

    This is registered as a teardown_appcontext handler in the app factory.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """
    Register the database teardown handler with the Flask app.

    Called from the app factory to ensure connections are properly
    cleaned up after each request.
    """
    app.teardown_appcontext(close_db)

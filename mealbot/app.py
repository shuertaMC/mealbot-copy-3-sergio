"""
Flask application factory and route registration.

Migrated from: server.go

Creates and configures the Flask application with:
- CORS middleware (from cors.go)
- JWT authentication middleware (from auth.go)
- Route registration for all endpoints
- Static file serving
- CLI commands for 'pair' and 'migrate'

Usage:
    # Development
    export FLASK_APP=mealbot.app:create_app
    flask run --port=5000

    # Production (via Procfile)
    gunicorn "mealbot.app:create_app()"
"""

import logging
import os

import click
from flask import Flask

from mealbot.auth import init_auth
from mealbot.cors import init_cors
from mealbot.db import init_app as init_db


def create_app(test_config=None):
    """
    Flask application factory.

    Creates and configures the Flask app instance. Equivalent to the Go
    main() function's setup logic in server.go.

    Args:
        test_config: Optional dict of configuration overrides for testing.
                     If provided, TESTING is set to True and auth middleware
                     is skipped.

    Returns:
        A configured Flask application instance.
    """
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
    )

    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
    )

    if test_config is not None:
        app.config.update(test_config)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if app.debug else logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    # Initialize database teardown
    init_db(app)

    # Initialize CORS
    init_cors(app)

    # Initialize JWT authentication (skip in test mode)
    if not app.config.get("TESTING"):
        init_auth(app)

    # Register blueprints
    from mealbot.models.orgs import orgs_bp

    app.register_blueprint(orgs_bp)

    # Root route serves static files (matching Go's http.FileServer)
    # Flask's static file handler takes care of /static/...
    # For the root path, serve the index or redirect to static
    @app.route("/")
    def index():
        """Serve static files from root, matching Go's FileServer behavior."""
        return app.send_static_file("privacy.html")

    # Health check endpoint
    @app.route("/health")
    def health():
        """Health check endpoint for monitoring."""
        return {"status": "ok"}, 200

    # CLI commands (skeleton for future milestones)
    @app.cli.command("pair")
    def pair_command():
        """Run pairing rounds (equivalent to Go's 'pair' subcommand)."""
        click.echo("Pairing command - to be implemented in a future milestone")

    @app.cli.command("migrate")
    def migrate_command():
        """Run data migrations (equivalent to Go's 'migrate' subcommand)."""
        click.echo("Migrate command - to be implemented in a future milestone")

    return app

"""
Flask application factory and route registration.

Ported from server.go. Creates the Flask application, registers all routes,
applies CORS middleware, and serves static files. The CLI dispatch (pair,
migrate subcommands) is deferred to Milestone 4.
"""

import os
import logging

from flask import Flask, send_from_directory
from dotenv import load_dotenv

# Load .env file in development
load_dotenv()

# Configure logging at module level
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def create_app():
    """
    Flask application factory.

    Creates and configures the Flask app with:
    - CORS middleware (from cors.py)
    - All HTTP routes (organization endpoints for this milestone)
    - Static file serving at /

    Returns:
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
    )

    # Initialize CORS middleware (mirrors Go GetCorsHandler)
    from mealbot.cors import init_cors

    init_cors(app)

    # Register routes
    _register_routes(app)

    return app


def _register_routes(app):
    """
    Register all HTTP route handlers on the Flask app.

    Mirrors the serveMux.Handle() calls in Go main().
    Routes for members, rounds, pairs, and round are deferred to later milestones.
    """
    from mealbot.models.orgs import (
        get_organizations_handler,
        create_organization_handler,
        cross_match_trait_handler,
    )

    # Organization endpoints
    app.add_url_rule(
        "/orgs",
        endpoint="orgs",
        view_func=get_organizations_handler,
        methods=["GET", "OPTIONS"],
    )

    app.add_url_rule(
        "/org",
        endpoint="org",
        view_func=create_organization_handler,
        methods=["POST", "OPTIONS"],
    )

    app.add_url_rule(
        "/crossmatchtrait",
        endpoint="crossmatchtrait",
        view_func=cross_match_trait_handler,
        methods=["POST", "OPTIONS"],
    )

    # Static file serving at root /
    # In Go, this is: serveMux.Handle("/", http.FileServer(http.Dir("./static")))
    # Flask's static file handling serves files from the static folder.
    # We add a catch-all route for / to serve index files.
    @app.route("/")
    def serve_root():
        """Serve the root static page (privacy.html as the index)."""
        return send_from_directory(app.static_folder, "privacy.html")

    @app.route("/<path:filename>")
    def serve_static_file(filename):
        """
        Serve static files from the static directory.

        Mirrors Go's http.FileServer(http.Dir("./static")).
        """
        return send_from_directory(app.static_folder, filename)


# Create the app instance for Gunicorn (Procfile: web: gunicorn mealbot.app:app)
app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    logger.info("Starting mealbot on port %d", port)
    app.run(host="0.0.0.0", port=port, debug=True)

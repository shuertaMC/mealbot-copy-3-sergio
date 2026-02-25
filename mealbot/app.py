"""Flask app factory and route registration (migrated from server.go).

Provides create_app() which creates and configures the Flask application
with all middleware (auth, CORS, logging) and routes for this milestone.
"""

import logging

from flask import Flask

from mealbot.auth import init_auth
from mealbot.cors import init_cors
from mealbot.models.orgs import (
    create_organization_handler,
    cross_match_trait_handler,
    get_organizations_handler,
)


def create_app(test_config=None):
    """Flask application factory.

    Creates the Flask app, applies configuration, registers middleware,
    and sets up all route handlers.

    Args:
        test_config: Optional dict of configuration overrides for testing.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
    )

    # Load configuration
    if test_config is not None:
        app.config.update(test_config)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    # Initialize CORS (from cors.go)
    init_cors(app)

    # Initialize JWT authentication (from auth.go)
    if not app.config.get("TESTING"):
        init_auth(app)

    # --- Route registration (from server.go serveMux) ---

    # Organization routes (from org.go)
    app.add_url_rule(
        "/orgs",
        "get_organizations",
        get_organizations_handler,
        methods=["GET", "OPTIONS"],
    )
    app.add_url_rule(
        "/org",
        "create_organization",
        create_organization_handler,
        methods=["POST", "OPTIONS"],
    )
    app.add_url_rule(
        "/crossmatchtrait",
        "cross_match_trait",
        cross_match_trait_handler,
        methods=["POST", "OPTIONS"],
    )

    # Root route serves static files (from server.go: "/" -> FileServer("./static"))
    @app.route("/")
    def index():
        return app.send_static_file("privacy.html")

    return app

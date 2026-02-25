"""CORS configuration (migrated from cors.go).

Uses Flask-CORS to replicate the Go CORS handler behavior:
- Reflects the request Origin back as Access-Control-Allow-Origin
- Allows Authorization, Content-Type, Origin, Accept, token headers
- Allows GET, POST, DELETE methods
"""

from flask_cors import CORS


def init_cors(app):
    """Configure CORS on the Flask app.

    Equivalent to Go's GetCorsHandler which reflects the request Origin
    and sets allowed headers/methods.
    """
    CORS(
        app,
        origins="*",
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Origin",
            "Accept",
            "token",
        ],
        methods=["GET", "POST", "DELETE", "OPTIONS"],
    )

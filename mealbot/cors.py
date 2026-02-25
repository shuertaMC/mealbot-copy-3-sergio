"""
CORS configuration.

Migrated from: cors.go

The Go implementation reflects the request's Origin header back as
Access-Control-Allow-Origin, effectively allowing all origins. It also
sets specific allowed headers and methods, and returns early on OPTIONS
(preflight) requests.

Flask-CORS is configured to replicate this exact behavior.
"""

from flask_cors import CORS

# Allowed headers - matches Go's AccessControlAllowHeaders constant
ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "Origin",
    "Accept",
    "token",
]

# Allowed methods - matches Go's Access-Control-Allow-Methods
ALLOWED_METHODS = ["GET", "POST", "DELETE", "OPTIONS"]


def init_cors(app):
    """
    Initialize CORS on the Flask app.

    Configures Flask-CORS to match the Go CORS middleware behavior:
    - Reflects the request Origin (origins="*" with supports_credentials=False)
    - Allows specific headers matching the Go AccessControlAllowHeaders constant
    - Allows GET, POST, DELETE methods
    - Handles OPTIONS preflight requests automatically

    Args:
        app: The Flask application instance.
    """
    CORS(
        app,
        origins="*",
        allow_headers=ALLOWED_HEADERS,
        methods=ALLOWED_METHODS,
        supports_credentials=False,
    )

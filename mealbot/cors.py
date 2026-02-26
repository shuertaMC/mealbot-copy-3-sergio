"""
CORS middleware.

Ported from cors.go. Implements a custom after_request handler that exactly
replicates the Go CORS behavior: echoing the request Origin header as
Access-Control-Allow-Origin, setting allowed headers and methods, and
handling OPTIONS preflight requests.
"""

# Allowed headers (mirrors Go AccessControlAllowHeaders constant)
ACCESS_CONTROL_ALLOW_HEADERS = "Authorization, Content-Type, Origin, Accept, token"


def init_cors(app):
    """
    Initialize CORS handling on the Flask app.

    Registers an after_request handler that sets CORS headers on every response,
    exactly mirroring the Go GetCorsHandler behavior:
    - Access-Control-Allow-Origin is set to the request's Origin header value
    - Access-Control-Allow-Headers includes Authorization, Content-Type, Origin, Accept, token
    - Access-Control-Allow-Methods allows GET, POST, DELETE
    - OPTIONS preflight requests return 200 with empty body

    Args:
        app: The Flask application instance.
    """

    @app.after_request
    def set_cors_headers(response):
        from flask import request

        origin = request.headers.get("Origin", "")
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = ACCESS_CONTROL_ALLOW_HEADERS
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE"
        return response

    @app.before_request
    def handle_preflight():
        from flask import request, Response

        if request.method == "OPTIONS":
            # Return empty 200 response for preflight; CORS headers added by after_request
            return Response("", status=200)

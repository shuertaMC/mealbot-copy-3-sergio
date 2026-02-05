"""CORS middleware implementation matching the Go implementation's permissive approach."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Headers allowed in CORS requests
ACCESS_CONTROL_ALLOW_HEADERS = "Authorization, Content-Type, Origin, Accept, token"

# Methods allowed in CORS requests
ACCESS_CONTROL_ALLOW_METHODS = "GET, POST, DELETE"


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware that mirrors the Go implementation's permissive policy.

    This middleware sets Access-Control-Allow-Origin to reflect the request's
    Origin header, effectively allowing any origin. This matches the original
    Go implementation's behavior.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle CORS headers for all requests.

        For OPTIONS (preflight) requests, returns an empty response with CORS headers.
        For other requests, processes normally and adds CORS headers to the response.
        """
        # Get the Origin header from the request
        origin = request.headers.get("origin", "")

        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            response = Response(content="", status_code=200)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = ACCESS_CONTROL_ALLOW_HEADERS
            response.headers["Access-Control-Allow-Methods"] = ACCESS_CONTROL_ALLOW_METHODS
            return response

        # Process the actual request
        response = await call_next(request)

        # Add CORS headers to the response
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = ACCESS_CONTROL_ALLOW_HEADERS
        response.headers["Access-Control-Allow-Methods"] = ACCESS_CONTROL_ALLOW_METHODS

        return response

"""CORS middleware configuration.

This module implements CORS handling that mirrors the behavior from Go's cors.go:
- Reflects the request Origin header back in Access-Control-Allow-Origin
- Allows specific headers: Authorization, Content-Type, Origin, Accept, token
- Allows methods: GET, POST, DELETE
- OPTIONS preflight requests are handled automatically
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


# Headers allowed in CORS requests (from Go's AccessControlAllowHeaders constant)
ALLOWED_HEADERS = [
    "Authorization",
    "Content-Type",
    "Origin",
    "Accept",
    "token",
]

# HTTP methods allowed in CORS requests (from Go's cors.go)
ALLOWED_METHODS = [
    "GET",
    "POST",
    "DELETE",
    "OPTIONS",
]


def add_cors_middleware(app: FastAPI) -> None:
    """Add CORS middleware to the FastAPI application.

    This configures CORS to match the Go implementation behavior:
    - Uses allow_origin_regex=".*" to effectively reflect any origin
      (mimicking Go's: w.Header().Set("Access-Control-Allow-Origin", r.Header.Get("Origin")))
    - Allows specified headers and methods
    - Handles OPTIONS preflight requests automatically

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        # Allow all origins by using regex, effectively reflecting back any Origin header
        # This matches Go's behavior: w.Header().Set("Access-Control-Allow-Origin", r.Header.Get("Origin"))
        allow_origin_regex=".*",
        allow_credentials=True,
        allow_methods=ALLOWED_METHODS,
        allow_headers=ALLOWED_HEADERS,
    )

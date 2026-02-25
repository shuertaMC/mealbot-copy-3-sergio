"""
JWT authentication middleware.

Migrated from: auth.go

Implements JWT validation as a Flask before_request hook using PyJWT.
Validates RS256-signed tokens from Auth0 with audience and issuer checks.
Uses PyJWT's PyJWKClient for JWKS fetching and key caching (improvement
over the Go implementation which fetched JWKS on every request).

OPTIONS (preflight) requests are passed through without authentication,
matching the Go behavior.
"""

import logging
import os

import jwt
from flask import g, jsonify, make_response, request
from jwt import PyJWKClient

logger = logging.getLogger("mealbot.auth")

# Default values matching the Go hardcoded constants (auth.go)
# These can be overridden via environment variables
DEFAULT_ISSUER = "https://mealbot.auth0.com/"
DEFAULT_AUDIENCE = "https://mealbot-2.herokuapp.com/"
DEFAULT_JWKS_URL = "https://mealbot.auth0.com/.well-known/jwks.json"

# Message constants matching Go
INVALID_ACCESS_TOKEN = "Invalid access token"

# Module-level JWKS client (initialized lazily)
_jwks_client = None


def _get_jwks_client():
    """
    Get or initialize the PyJWKClient for fetching JWKS keys.

    The client is created lazily on first use and cached at module level.
    PyJWKClient handles key caching internally, improving on the Go
    implementation's per-request JWKS fetch.
    """
    global _jwks_client
    if _jwks_client is None:
        jwks_url = os.environ.get("AUTH0_JWKS_URL", DEFAULT_JWKS_URL)
        _jwks_client = PyJWKClient(jwks_url)
    return _jwks_client


def _get_auth_config():
    """
    Get Auth0 configuration from environment variables with defaults.

    Returns:
        Tuple of (issuer, audience).
    """
    issuer = os.environ.get("AUTH0_ISSUER", DEFAULT_ISSUER)
    audience = os.environ.get("AUTH0_AUDIENCE", DEFAULT_AUDIENCE)
    return issuer, audience


def check_jwt():
    """
    Validate the JWT from the Authorization header.

    This function is registered as a Flask before_request hook.
    It performs the following checks (matching the Go CustomJWTMiddleware):

    1. Pass through OPTIONS requests (preflight)
    2. Extract Bearer token from Authorization header
    3. Fetch the signing key from JWKS using the token's kid header
    4. Validate the token with RS256, checking audience and issuer

    Returns:
        None if authentication succeeds (allows request to proceed).
        A Flask Response with 401 status if authentication fails.
    """
    # Pass through preflight requests (matches Go behavior)
    if request.method == "OPTIONS":
        return None

    # Pass through static file requests (matches Go "/" file server)
    if request.path == "/" or request.path.startswith("/static"):
        return None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        logger.warning("No authorization header")
        return make_response(
            jsonify({"Message": "No authorization header"}), 401
        )

    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("Invalid authorization header format")
        return make_response(
            jsonify(
                {"Message": "Authorization header format must be Bearer {token}"}
            ),
            401,
        )

    token = parts[1]
    issuer, audience = _get_auth_config()

    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
        )

        # Store decoded token on g for handler access if needed
        g.jwt_payload = decoded

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return make_response(
            jsonify({"Message": INVALID_ACCESS_TOKEN}), 401
        )
    except jwt.InvalidAudienceError:
        logger.warning("Invalid audience")
        return make_response(
            jsonify({"Message": "Invalid audience"}), 401
        )
    except jwt.InvalidIssuerError:
        logger.warning("Invalid issuer")
        return make_response(
            jsonify({"Message": "Invalid issuer"}), 401
        )
    except jwt.PyJWKClientError as e:
        logger.error("JWKS key fetch failed: %s", str(e))
        return make_response(
            jsonify({"Message": "Unable to find appropriate key"}), 401
        )
    except jwt.InvalidTokenError as e:
        logger.warning("Token validation failed: %s", str(e))
        return make_response(
            jsonify({"Message": INVALID_ACCESS_TOKEN}), 401
        )
    except Exception as e:
        logger.error("Unexpected auth error: %s", str(e))
        return make_response(
            jsonify({"Message": INVALID_ACCESS_TOKEN}), 401
        )

    return None


def init_auth(app):
    """
    Register JWT authentication middleware with the Flask app.

    Args:
        app: The Flask application instance.
    """
    app.before_request(check_jwt)


def reset_jwks_client():
    """
    Reset the JWKS client (useful for testing).
    """
    global _jwks_client
    _jwks_client = None

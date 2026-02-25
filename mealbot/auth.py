"""JWT authentication middleware (migrated from auth.go).

Implements Auth0 JWT validation using PyJWT with RS256 signing.
JWKS keys are fetched from Auth0 and cached via PyJWT's PyJWKClient.
"""

import os
import logging

import jwt
from jwt import PyJWKClient
from flask import request, g

logger = logging.getLogger("mealbot")

# Lazy-initialized PyJWKClient (caches JWKS keys)
_jwk_client = None


def _get_jwk_client():
    """Return a cached PyJWKClient instance for JWKS fetching."""
    global _jwk_client
    if _jwk_client is None:
        jwks_url = os.environ.get(
            "AUTH0_JWKS_URL",
            "https://mealbot.auth0.com/.well-known/jwks.json",
        )
        _jwk_client = PyJWKClient(jwks_url)
    return _jwk_client


def init_auth(app):
    """Register JWT authentication as a Flask before_request hook.

    Equivalent to Go's GetAuthHandler middleware wrapper.
    """

    @app.before_request
    def check_jwt():
        # Passthrough OPTIONS requests (preflight)
        if request.method == "OPTIONS":
            return None

        # Static file routes do not require authentication
        if request.path == "/" or request.path.startswith("/static"):
            return None

        auth_header = request.headers.get("Authorization", "")
        if not auth_header:
            logger.error("No authorization header")
            return {"Message": "No authorization header"}, 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.error("Authorization header format must be Bearer {token}")
            return {
                "Message": "Authorization header format must be Bearer {token}"
            }, 401

        token = parts[1]

        try:
            issuer = os.environ.get(
                "AUTH0_ISSUER", "https://mealbot.auth0.com/"
            )
            audience = os.environ.get(
                "AUTH0_AUDIENCE", "https://mealbot-2.herokuapp.com/"
            )

            jwk_client = _get_jwk_client()
            signing_key = jwk_client.get_signing_key_from_jwt(token)

            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=audience,
                issuer=issuer,
            )
            g.jwt_claims = decoded

        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return {"Message": "Token has expired"}, 401
        except jwt.InvalidAudienceError:
            logger.error("Invalid audience")
            return {"Message": "Invalid audience"}, 401
        except jwt.InvalidIssuerError:
            logger.error("Invalid issuer")
            return {"Message": "Invalid issuer"}, 401
        except jwt.PyJWTError as e:
            logger.error("Token is invalid: %s", e)
            return {"Message": "Token is invalid"}, 401
        except Exception as e:
            logger.error("Authentication error: %s", e)
            return {"Message": "Authentication error"}, 401

        return None

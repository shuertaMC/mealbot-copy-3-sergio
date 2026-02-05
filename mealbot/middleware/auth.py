"""JWT authentication middleware using Auth0.

This module implements JWT validation that mirrors the behavior from Go's auth.go:
- Extracts Bearer token from Authorization header
- Validates JWT signature using JWKS from Auth0
- Verifies issuer matches the configured Auth0 domain
- Verifies audience includes the configured audience
- Verifies RS256 signing algorithm
- OPTIONS requests bypass authentication
"""

import logging
from typing import Any, Optional

import httpx
import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..config import Settings, get_settings

logger = logging.getLogger(__name__)

# Cache for JWKS to avoid repeated HTTP calls
_jwks_cache: Optional[dict[str, Any]] = None


class JWKSError(Exception):
    """Error fetching or parsing JWKS."""

    pass


class TokenValidationError(Exception):
    """Error validating JWT token."""

    pass


async def fetch_jwks(jwks_url: str) -> dict[str, Any]:
    """Fetch JSON Web Key Set from Auth0.

    Args:
        jwks_url: URL to the JWKS endpoint

    Returns:
        dict: Parsed JWKS containing public keys

    Raises:
        JWKSError: If fetching or parsing JWKS fails
    """
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_url)
            response.raise_for_status()
            _jwks_cache = response.json()
            return _jwks_cache
    except httpx.HTTPError as e:
        raise JWKSError(f"Failed to fetch JWKS: {e}")
    except Exception as e:
        raise JWKSError(f"Failed to parse JWKS: {e}")


def get_pem_certificate(jwks: dict[str, Any], kid: str) -> str:
    """Extract PEM certificate from JWKS for the given key ID.

    This mirrors the Go getPEMCertificate function.

    Args:
        jwks: Parsed JWKS data
        kid: Key ID from JWT header

    Returns:
        str: PEM-formatted certificate

    Raises:
        JWKSError: If no matching key is found
    """
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            x5c = key.get("x5c", [])
            if x5c:
                return f"-----BEGIN CERTIFICATE-----\n{x5c[0]}\n-----END CERTIFICATE-----"

    raise JWKSError("Unable to find appropriate key")


def verify_audience(claims: dict[str, Any], expected_audience: str) -> bool:
    """Verify the audience claim contains the expected value.

    This mirrors the Go verifyAudience function, handling both string and array audience claims.

    Args:
        claims: JWT claims dictionary
        expected_audience: Expected audience value

    Returns:
        bool: True if audience is valid
    """
    aud = claims.get("aud")
    if aud is None:
        return False

    # Handle both string and list audience claims
    if isinstance(aud, str):
        return aud == expected_audience
    elif isinstance(aud, list):
        return expected_audience in aud

    return False


# Security scheme for extracting Bearer token
http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
    settings: Settings = Depends(get_settings),
) -> Optional[dict[str, Any]]:
    """FastAPI dependency for JWT authentication.

    This dependency validates the JWT token and returns the decoded claims.
    It mirrors the behavior of Go's GetAuthHandler middleware.

    Args:
        request: FastAPI request object
        credentials: Extracted Bearer credentials
        settings: Application settings

    Returns:
        dict: Decoded JWT claims if valid

    Raises:
        HTTPException: If token is invalid or missing
    """
    # OPTIONS requests bypass authentication (preflight)
    if request.method == "OPTIONS":
        return None

    # Check for authorization header
    if credentials is None:
        logger.warning("No authorization header provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # Fetch JWKS
        jwks = await fetch_jwks(settings.auth0_jwks_url)

        # Decode header to get kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise TokenValidationError("Token header missing 'kid'")

        # Verify signing algorithm
        alg = unverified_header.get("alg")
        if alg != "RS256":
            raise TokenValidationError("Token must use RS256 signing algorithm")

        # Get PEM certificate (mirrors Go's getPEMCertificate approach)
        pem_cert = get_pem_certificate(jwks, kid)

        # Parse RSA public key from PEM certificate
        # This mirrors Go's jwt.ParseRSAPublicKeyFromPEM([]byte(cert))
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend

        cert = x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())
        public_key = cert.public_key()

        decoded = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.auth0_audience,
            issuer=settings.auth0_issuer,
        )

        # Additional audience verification (mirrors Go behavior)
        if not verify_audience(decoded, settings.auth0_audience):
            raise TokenValidationError("Invalid audience")

        return decoded

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidAudienceError:
        logger.warning("Invalid audience")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid audience",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidIssuerError:
        logger.warning("Invalid issuer")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid issuer",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWKSError as e:
        logger.error(f"JWKS error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service unavailable",
        )
    except TokenValidationError as e:
        logger.warning(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def clear_jwks_cache() -> None:
    """Clear the JWKS cache. Useful for testing or when keys rotate."""
    global _jwks_cache
    _jwks_cache = None

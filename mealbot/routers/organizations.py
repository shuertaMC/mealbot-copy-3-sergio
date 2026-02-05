"""FastAPI router for organization-related endpoints.

This module implements the organization management endpoints,
mirroring the Go handlers from org.go:
- GET /orgs?admin=X - Retrieve all organizations for an admin
- POST /org?admin=X - Create a new organization
- POST /crossmatchtrait?org=X - Set the cross-match trait for an organization
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..middleware.auth import get_current_user
from ..models.organization import Organization

logger = logging.getLogger(__name__)

router = APIRouter(tags=["organizations"])


# Request/Response schemas
class CreateOrganizationRequest(BaseModel):
    """Request body for creating a new organization.

    Mirrors Go's CreateOrganizationRequestBody struct.
    Uses alias to match the Go JSON field name "org".
    """

    org: str


class SetCrossMatchTraitRequest(BaseModel):
    """Request body for setting cross-match trait.

    Mirrors Go's SetCrossMatchTraitRequestBody struct.
    """

    trait: str


class OrgsResponse(BaseModel):
    """Response schema for GET /orgs endpoint."""

    orgs: list[str]


class MessageResponse(BaseModel):
    """Response schema for success messages."""

    message: str


@router.get("/orgs", response_model=OrgsResponse)
async def get_organizations(
    admin: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _user: Optional[dict[str, Any]] = Depends(get_current_user),
) -> dict[str, list[str]]:
    """Retrieve all organizations for a given admin.

    This mirrors Go's GetOrganizationsHandler function.

    Args:
        admin: Admin identifier (required query parameter)
        db: Database session dependency
        _user: Authenticated user (unused but required for auth)

    Returns:
        dict with "orgs" key containing list of organization names

    Raises:
        HTTPException: 400 if admin parameter is missing
    """
    if admin is None:
        logger.warning("Missing admin query parameter in GET /orgs")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="request query parameters must contain 'admin'",
        )

    # Query organizations by admin - mirrors Go's getOrganizations function
    organizations = (
        db.query(Organization.name).filter(Organization.admin == admin).all()
    )

    # Extract organization names from query result
    org_names = [org.name for org in organizations]

    return {"orgs": org_names}


@router.post("/org", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    body: CreateOrganizationRequest,
    admin: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _user: Optional[dict[str, Any]] = Depends(get_current_user),
) -> dict[str, str]:
    """Create a new organization.

    This mirrors Go's CreateOrganizationHandler function.

    Args:
        body: Request body with organization name
        admin: Admin identifier (required query parameter)
        db: Database session dependency
        _user: Authenticated user (unused but required for auth)

    Returns:
        dict with success message

    Raises:
        HTTPException: 400 if admin parameter is missing or org name is empty
        HTTPException: 500 if database insert fails
    """
    if admin is None:
        logger.warning("Missing admin query parameter in POST /org")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="request query parameters must contain 'admin'",
        )

    # Validate organization name is not empty - mirrors Go's createOrganization validation
    if not body.org or body.org.strip() == "":
        logger.warning("Empty organization name in POST /org")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name cannot be an empty string",
        )

    try:
        # Create and insert organization - mirrors Go's createOrganization function
        new_org = Organization(name=body.org, admin=admin)
        db.add(new_org)
        db.commit()

        logger.info(f"Created organization: {body.org} for admin: {admin}")
        return {"message": "Successfully created new organization"}

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database error creating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e.orig) if e.orig else "Database error",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating organization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/crossmatchtrait", response_model=MessageResponse, status_code=status.HTTP_201_CREATED
)
async def set_cross_match_trait(
    body: SetCrossMatchTraitRequest,
    org: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _user: Optional[dict[str, Any]] = Depends(get_current_user),
) -> dict[str, str]:
    """Set the cross-match trait for an organization.

    This mirrors Go's CrossMatchTraitHandler function.

    Args:
        body: Request body with trait value
        org: Organization name (required query parameter)
        db: Database session dependency
        _user: Authenticated user (unused but required for auth)

    Returns:
        dict with success message

    Raises:
        HTTPException: 400 if org parameter is missing
        HTTPException: 500 if database update fails
    """
    if org is None:
        logger.warning("Missing org query parameter in POST /crossmatchtrait")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request query parameters must contain org",
        )

    try:
        # Update cross_match_trait - mirrors Go's setCrossMatchTrait function
        result = (
            db.query(Organization)
            .filter(Organization.name == org)
            .update({Organization.cross_match_trait: body.trait})
        )
        db.commit()

        if result == 0:
            logger.warning(f"Organization not found: {org}")
            # Go code doesn't check for this, but still returns success
            # We'll match Go behavior and return success regardless

        logger.info(f"Set cross match trait for org: {org} to: {body.trait}")
        return {"message": "Successfully set the cross match trait"}

    except Exception as e:
        db.rollback()
        logger.error(f"Error setting cross match trait: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def get_cross_match_trait(org_name: str, db: Session) -> str:
    """Retrieve the cross-match trait for an organization.

    This mirrors Go's GetCrossMatchTrait function and is used by the
    pairing algorithm in future milestones.

    Args:
        org_name: Name of the organization
        db: Database session

    Returns:
        str: The cross_match_trait value, or empty string if NULL
    """
    organization = (
        db.query(Organization.cross_match_trait)
        .filter(Organization.name == org_name)
        .first()
    )

    if organization is None or organization.cross_match_trait is None:
        return ""

    return organization.cross_match_trait

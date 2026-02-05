"""Organization API endpoints.

This module implements the HTTP handlers for organization management:
- GET /orgs - Retrieve organizations for an admin
- POST /org - Create a new organization
- POST /crossmatchtrait - Set cross-match trait for an organization
"""

import logging

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from mealbot.database import get_db
from mealbot.models.organization import Organization
from mealbot.schemas.organization import (
    CreateOrganizationRequest,
    OrganizationsResponse,
    SetCrossMatchTraitRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/orgs", response_model=OrganizationsResponse)
def get_organizations(
    admin: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> OrganizationsResponse | Response:
    """Retrieve organizations for a given admin email.

    Args:
        admin: Email address of the admin to filter organizations by.
        db: Database session dependency.

    Returns:
        OrganizationsResponse with list of organization names.
    """
    if admin is None:
        logger.error("GetOrganizationsHandler: request query parameters must contain 'admin'")
        return PlainTextResponse(
            content="request query parameters must contain 'admin'",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        stmt = select(Organization.name).where(Organization.admin == admin)
        result = db.execute(stmt)
        organizations = [row[0] for row in result.fetchall()]
        return OrganizationsResponse(orgs=organizations)
    except SQLAlchemyError as e:
        logger.error(f"GetOrganizationsHandler: database error: {e}")
        return PlainTextResponse(
            content=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/org", status_code=status.HTTP_201_CREATED)
def create_organization(
    body: CreateOrganizationRequest,
    admin: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Response:
    """Create a new organization.

    Args:
        body: Request body containing the organization name.
        admin: Email address of the admin creating the organization.
        db: Database session dependency.

    Returns:
        Plain text success message with 201 status code.
    """
    if admin is None:
        logger.error("CreateOrganizationHandler: request query parameters must contain 'admin'")
        return PlainTextResponse(
            content="request query parameters must contain 'admin'",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    org_name = body.org
    if org_name == "":
        logger.error("CreateOrganizationHandler: Organization name cannot be an empty string")
        return PlainTextResponse(
            content="Organization name cannot be an empty string",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    logger.info(f"{org_name} {admin}")

    try:
        organization = Organization(name=org_name, admin=admin)
        db.add(organization)
        db.commit()
        return PlainTextResponse(
            content="Successfully created new organization",
            status_code=status.HTTP_201_CREATED,
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"CreateOrganizationHandler: database error: {e}")
        return PlainTextResponse(
            content=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post("/crossmatchtrait", status_code=status.HTTP_201_CREATED)
def set_cross_match_trait(
    body: SetCrossMatchTraitRequest,
    org: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> Response:
    """Set the cross-match trait for an organization.

    Args:
        body: Request body containing the trait value.
        org: Name of the organization to update.
        db: Database session dependency.

    Returns:
        Plain text success message with 201 status code.
    """
    if org is None:
        logger.error("CrossMatchTraitHandler: request query parameters must contain 'org'")
        return PlainTextResponse(
            content="request query parameters must contain 'org'",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        stmt = select(Organization).where(Organization.name == org)
        result = db.execute(stmt)
        organization = result.scalar_one_or_none()

        if organization is None:
            return PlainTextResponse(
                content=f"Organization '{org}' not found",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        organization.cross_match_trait = body.trait
        db.commit()
        return PlainTextResponse(
            content="Successfully set the cross match trait",
            status_code=status.HTTP_201_CREATED,
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"CrossMatchTraitHandler: database error: {e}")
        return PlainTextResponse(
            content=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

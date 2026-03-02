"""Organization management HTTP endpoints.

Implements the endpoints from the Go application's org.go:
- GET /orgs?admin=<email> - list organizations by admin
- POST /org?admin=<email> - create a new organization
- POST /crossmatchtrait?org=<name> - set cross-match trait
"""

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from core.organizations import (
    create_organization,
    get_organizations,
    set_cross_match_trait,
)
from infra.db import get_db
from mealbot_api.schemas.orgs import (
    CreateOrganizationRequest,
    SetCrossMatchTraitRequest,
)
from mealbot_api.schemas.responses import (
    log_and_error,
    log_and_respond,
    message_response,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/orgs")
def get_organizations_handler(request: Request, db: Session = Depends(get_db)):
    """List organizations by admin.

    Equivalent to Go's GetOrganizationsHandler.
    Expects query param: admin=<email>
    Returns: {"orgs": ["org1", "org2", ...]}
    """
    function = "GetOrganizationsHandler"

    # Validate admin query parameter
    admin_values = request.query_params.getlist("admin")
    if len(admin_values) == 0 or len(admin_values) > 1:
        return log_and_error(
            "request query parameters must contain 'admin'",
            400,
            function,
        )

    admin = admin_values[0]

    try:
        organizations = get_organizations(db, admin)
    except Exception as e:
        return log_and_error(e, 500, function)

    return log_and_respond({"orgs": organizations}, 200, function)


@router.post("/org", status_code=201)
def create_organization_handler(
    request: Request,
    body: CreateOrganizationRequest,
    db: Session = Depends(get_db),
):
    """Create a new organization.

    Equivalent to Go's CreateOrganizationHandler.
    Expects query param: admin=<email>
    Expects body: {"org": "<name>"}
    Returns: {"Message": "Successfully created new organization"}
    """
    function = "CreateOrganizationHandler"

    # Validate admin query parameter
    admin_values = request.query_params.getlist("admin")
    if len(admin_values) == 0 or len(admin_values) > 1:
        return log_and_error(
            "request query parameters must contain 'admin'",
            400,
            function,
        )

    admin = admin_values[0]

    try:
        create_organization(db, body.org, admin)
    except ValueError as e:
        return log_and_error(e, 500, function)
    except Exception as e:
        return log_and_error(e, 500, function)

    return message_response(
        "Successfully created new organization",
        status_code=201,
    )


@router.post("/crossmatchtrait", status_code=201)
def cross_match_trait_handler(
    request: Request,
    body: SetCrossMatchTraitRequest,
    db: Session = Depends(get_db),
):
    """Set the cross-match trait for an organization.

    Equivalent to Go's CrossMatchTraitHandler.
    Expects query param: org=<name>
    Expects body: {"trait": "<value>"}
    Returns: {"Message": "Successfully set the cross match trait"}
    """
    function = "CrossMatchTraitHandler"

    # Validate org query parameter
    org_values = request.query_params.getlist("org")
    if len(org_values) == 0 or len(org_values) > 1:
        return log_and_error(
            "Request query parameters must contain org",
            400,
            function,
        )

    orgname = org_values[0]

    try:
        set_cross_match_trait(db, orgname, body.trait)
    except Exception as e:
        return log_and_error(e, 500, function)

    return message_response(
        "Successfully set the cross match trait",
        status_code=201,
    )

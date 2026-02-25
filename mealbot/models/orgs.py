"""
Organization domain handlers and queries.

Migrated from: org.go

Implements HTTP handlers and backing SQL queries for organization
management:
- GET /orgs - Fetch organizations for an admin
- POST /org - Create a new organization
- POST /crossmatchtrait - Set cross-match trait for an organization

Also exports get_cross_match_trait() which is consumed by the pairing
algorithm in a future milestone.
"""

import json
import logging

from flask import Blueprint, request

from mealbot.db import get_db_connection
from mealbot.log import (
    log_and_write,
    log_and_write_err,
    log_and_write_status_bad_request,
    log_and_write_status_internal_server_error,
)
from mealbot.utils import get_query_param

logger = logging.getLogger("mealbot.orgs")

orgs_bp = Blueprint("orgs", __name__)


@orgs_bp.route("/orgs", methods=["GET"])
def get_organizations_handler():
    """
    HTTP Handler for fetching all the organizations an admin manages.

    Equivalent to Go's GetOrganizationsHandler.

    Query params:
        admin: The admin email to filter organizations by.

    Returns:
        200: {"orgs": ["org1", "org2", ...]}
        400: If admin query param is missing
        405: If method is not GET
        500: On database errors
    """
    function = "GetOrganizationsHandler"

    if request.method != "GET":
        return log_and_write_err(
            "Only GET requests are allowed at this route",
            405,
            function,
        )

    # Extract admin query parameter
    admin_values = request.args.getlist("admin")
    if len(admin_values) == 0 or len(admin_values) > 1:
        return log_and_write_err(
            "request query parameters must contain 'admin'",
            400,
            function,
        )
    admin = admin_values[0]

    try:
        organizations = get_organizations(admin)
    except Exception as e:
        return log_and_write_status_internal_server_error(e, function)

    resp = {"orgs": organizations}
    return log_and_write(resp, 200, function)


@orgs_bp.route("/org", methods=["POST"])
def create_organization_handler():
    """
    HTTP handler for creating a new organization.

    Equivalent to Go's CreateOrganizationHandler.

    Query params:
        admin: The admin email for the organization.

    Request body (JSON):
        {"org": "organization_name"}

    Returns:
        201: {"Message": "Successfully created new organization"}
        400: If body is malformed or admin param is missing
        405: If method is not POST
        500: On database errors
    """
    function = "CreateOrganizationHandler"

    if request.method != "POST":
        return log_and_write_err(
            "Only POST requests are allowed at this route",
            405,
            function,
        )

    # Parse request body
    try:
        body = request.get_json(force=True)
    except Exception as e:
        return log_and_write_status_bad_request(e, function)

    if body is None:
        return log_and_write_status_bad_request(
            "Invalid request body", function
        )

    org_name = body.get("org", "")

    # Extract admin query parameter
    admin_values = request.args.getlist("admin")
    if len(admin_values) == 0 or len(admin_values) > 1:
        return log_and_write_err(
            "request query parameters must contain 'admin'",
            400,
            function,
        )
    admin = admin_values[0]

    logger.info("%s %s", org_name, admin)

    try:
        create_organization(org_name, admin)
    except Exception as e:
        return log_and_write_status_internal_server_error(e, function)

    return log_and_write(
        "Successfully created new organization", 201, function
    )


@orgs_bp.route("/crossmatchtrait", methods=["POST"])
def cross_match_trait_handler():
    """
    HTTP handler for setting a cross-match trait for an organization.

    Equivalent to Go's CrossMatchTraitHandler.

    Query params:
        org: The organization name.

    Request body (JSON):
        {"trait": "trait_name"}

    Returns:
        201: {"Message": "Successfully set the cross match trait"}
        400: If body is malformed or org param is missing
        405: If method is not POST
        500: On database errors
    """
    function = "CrossMatchTraitHandler"

    if request.method != "POST":
        return log_and_write_err(
            "Only POST requests are allowed at this route",
            405,
            function,
        )

    try:
        orgname = get_query_param("org")
    except ValueError as e:
        return log_and_write_status_bad_request(e, function)

    try:
        body = request.get_json(force=True)
    except Exception:
        return log_and_write_err("Malformed body.", 400, function)

    if body is None:
        return log_and_write_err(
            "Request body is malformed", 400, function
        )

    trait = body.get("trait", "")
    if trait is None:
        return log_and_write_err(
            "Request body is malformed", 400, function
        )

    try:
        set_cross_match_trait(orgname, trait)
    except Exception as e:
        return log_and_write_status_internal_server_error(e, function)

    return log_and_write(
        "Successfully set the cross match trait", 201, function
    )


# ---------------------------------------------------------------------------
# Database query functions
# ---------------------------------------------------------------------------


def get_organizations(admin):
    """
    Fetch all organization names for the given admin.

    Equivalent to Go's getOrganizations.

    Args:
        admin: The admin email.

    Returns:
        A list of organization name strings.
    """
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT name FROM organizations WHERE admin = %s",
            (admin,),
        )
        rows = cursor.fetchall()
        organizations = [row[0] for row in rows]
        return organizations
    finally:
        cursor.close()


def create_organization(name, admin):
    """
    Create a new organization.

    Equivalent to Go's createOrganization.

    Args:
        name: The organization name.
        admin: The admin email.

    Raises:
        ValueError: If the organization name is empty.
        Exception: On database errors.
    """
    if not name:
        raise ValueError("Organization name cannot be an empty string")

    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO organizations (name, admin) VALUES (%s, %s)",
            (name, admin),
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()


def get_cross_match_trait(orgname):
    """
    Get the cross-match trait for an organization.

    Equivalent to Go's GetCrossMatchTrait. Returns an empty string
    if the trait is NULL in the database.

    Args:
        orgname: The organization name.

    Returns:
        The cross-match trait string, or empty string if not set.
    """
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT cross_match_trait FROM organizations WHERE name = %s",
            (orgname,),
        )
        row = cursor.fetchone()
        if row is None:
            return ""
        cross_match_trait = row[0]
        if cross_match_trait is None:
            return ""
        return cross_match_trait
    finally:
        cursor.close()


def set_cross_match_trait(orgname, cross_match_trait):
    """
    Set the cross-match trait for an organization.

    Equivalent to Go's setCrossMatchTrait.

    Args:
        orgname: The organization name.
        cross_match_trait: The trait value to set.

    Raises:
        Exception: On database errors.
    """
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "UPDATE organizations SET cross_match_trait = %s WHERE name = %s",
            (cross_match_trait, orgname),
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

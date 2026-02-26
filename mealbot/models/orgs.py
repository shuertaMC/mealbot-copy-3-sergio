"""
Organization management endpoints and database functions.

Ported from org.go. Provides HTTP handlers for:
- GET /orgs   — fetch organizations by admin email
- POST /org   — create a new organization
- POST /crossmatchtrait — set the cross-match trait for an organization

Also exports get_cross_match_trait() for use by other modules (pairing, members).
"""

import json
import logging

from flask import request

from mealbot.db import get_db_connection
from mealbot.log import (
    log_and_write,
    log_and_write_err,
    log_and_write_status_bad_request,
    log_and_write_status_internal_server_error,
)
from mealbot.utils import str_to_bytes, err_to_bytes, get_query_param

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Database functions
# ---------------------------------------------------------------------------


def get_organizations(admin):
    """
    Query all organization names managed by the given admin email.

    Mirrors Go getOrganizations().

    Args:
        admin: The admin email address.

    Returns:
        List of organization name strings.

    Raises:
        Exception on database errors.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT name FROM organizations WHERE admin = %s",
                (admin,),
            )
            rows = cur.fetchall()
            return [row[0] for row in rows]
    finally:
        conn.close()


def create_organization(name, admin):
    """
    Insert a new organization into the database.

    Mirrors Go createOrganization().

    Args:
        name: Organization name (must not be empty).
        admin: Admin email address.

    Raises:
        ValueError if name is empty.
        Exception on database errors (including duplicate key).
    """
    if not name:
        raise ValueError("Organization name cannot be an empty string")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO organizations (name, admin) VALUES (%s, %s)",
                (name, admin),
            )
        conn.commit()
    finally:
        conn.close()


def get_cross_match_trait(orgname):
    """
    Get the cross-match trait for an organization.

    Mirrors Go GetCrossMatchTrait(). Returns an empty string if the trait is
    NULL in the database.

    This function is exported for use by the pairing algorithm (Milestone 3)
    and the members GET handler (Milestone 2).

    Args:
        orgname: Organization name.

    Returns:
        The cross-match trait string, or empty string if not set.

    Raises:
        Exception on database errors.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT cross_match_trait FROM organizations WHERE name = %s",
                (orgname,),
            )
            row = cur.fetchone()
            if row is None:
                return ""
            # Handle SQL NULL — row[0] will be None if cross_match_trait is NULL
            return row[0] if row[0] is not None else ""
    finally:
        conn.close()


def set_cross_match_trait(orgname, cross_match_trait):
    """
    Update the cross-match trait for an organization.

    Mirrors Go setCrossMatchTrait().

    Args:
        orgname: Organization name.
        cross_match_trait: The trait value to set.

    Raises:
        Exception on database errors.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE organizations SET cross_match_trait = %s WHERE name = %s",
                (cross_match_trait, orgname),
            )
        conn.commit()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# HTTP Handlers
# ---------------------------------------------------------------------------


def get_organizations_handler():
    """
    HTTP Handler for GET /orgs — fetch all organizations an admin manages.

    Query params:
        admin (required): The admin email address.

    Returns:
        JSON response: {"orgs": ["org1", "org2", ...]}

    Mirrors Go GetOrganizationsHandler.
    """
    function = "GetOrganizationsHandler"

    if request.method != "GET":
        return log_and_write_err(
            "Only GET requests are allowed at this route",
            405,
            function,
        )

    # Validate 'admin' query parameter — mirror Go behavior:
    # Check using getlist to detect missing or multiple values
    queries = request.args.getlist("admin")
    if len(queries) == 0 or len(queries) > 1:
        return log_and_write_err(
            "request query parameters must contain 'admin'",
            400,
            function,
        )

    admin = queries[0]

    try:
        organizations = get_organizations(admin)
    except Exception as e:
        return log_and_write_status_internal_server_error(e, function)

    resp = json.dumps({"orgs": organizations})
    return log_and_write(resp, 200, function)


def create_organization_handler():
    """
    HTTP Handler for POST /org — create a new organization.

    Query params:
        admin (required): The admin email address.

    Request body (JSON):
        {"org": "organization_name"}

    Returns:
        JSON response: {"Message": "Successfully created new organization"}
        with status 201 on success.

    Mirrors Go CreateOrganizationHandler.
    """
    function = "CreateOrganizationHandler"

    if request.method != "POST":
        return log_and_write_err(
            "Only POST requests are allowed at this route",
            405,
            function,
        )

    # Parse JSON body
    try:
        body = request.get_json(force=True)
        if body is None:
            raise ValueError("Empty or invalid JSON body")
    except Exception as e:
        return log_and_write_status_bad_request(e, function)

    # Validate 'admin' query parameter
    queries = request.args.getlist("admin")
    if len(queries) == 0 or len(queries) > 1:
        return log_and_write_err(
            "request query parameters must contain 'admin'",
            400,
            function,
        )
    admin = queries[0]

    org_name = body.get("org", "")
    logger.info("%s %s", org_name, admin)

    try:
        create_organization(org_name, admin)
    except Exception as e:
        return log_and_write_status_internal_server_error(e, function)

    return log_and_write(
        str_to_bytes("Successfully created new organization"),
        201,
        function,
    )


def cross_match_trait_handler():
    """
    HTTP Handler for POST /crossmatchtrait — set/update the cross-match trait
    for an organization.

    Query params:
        org (required): The organization name.

    Request body (JSON):
        {"trait": "trait_name"}

    Returns:
        JSON response: {"Message": "Successfully set the cross match trait"}
        with status 201 on success.

    Mirrors Go CrossMatchTraitHandler.
    """
    function = "CrossMatchTraitHandler"

    if request.method != "POST":
        return log_and_write_err(
            "Only POST requests are allowed at this route",
            405,
            function,
        )

    orgname, err = get_query_param("org")
    if err:
        return log_and_write_status_bad_request(err, function)

    # Parse JSON body
    try:
        body = request.get_json(force=True)
        if body is None:
            raise ValueError("Malformed body.")
    except Exception:
        return log_and_write_err("Malformed body.", 400, function)

    if not isinstance(body, dict) or "trait" not in body:
        return log_and_write_err("Request body is malformed", 400, function)

    trait = body["trait"]

    try:
        set_cross_match_trait(orgname, trait)
    except Exception as e:
        return log_and_write_err(str(e), 500, function)

    return log_and_write(
        str_to_bytes("Successfully set the cross match trait"),
        201,
        function,
    )

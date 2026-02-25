"""Organization queries and handlers (migrated from org.go).

Provides HTTP route handlers for:
- GET /orgs — fetch organizations by admin
- POST /org — create a new organization
- POST /crossmatchtrait — set/update cross-match trait for an organization

Also provides the get_cross_match_trait() function used by the pairing
algorithm in future milestones.
"""

import json

from flask import request

from mealbot.db import get_db_connection
from mealbot.log import (
    log_and_write,
    log_and_write_err,
    log_and_write_status_bad_request,
    log_and_write_status_internal_server_error,
    str_to_bytes,
)
from mealbot.utils import get_query_param


def get_organizations_handler():
    """HTTP handler for fetching all organizations an admin manages.

    Equivalent to Go's GetOrganizationsHandler.

    GET /orgs?admin=<admin_email>
    Response: {"orgs": ["org1", "org2", ...]}
    """
    function = "GetOrganizationsHandler"

    if request.method != "GET":
        return log_and_write_err(
            "Only GET requests are allowed at this route",
            405,
            function,
        )

    admin = request.args.get("admin")
    if admin is None:
        return log_and_write_err(
            "request query parameters must contain 'admin'",
            400,
            function,
        )

    try:
        organizations = _get_organizations(admin)
    except Exception as e:
        return log_and_write_status_internal_server_error(e, function)

    resp = json.dumps({"orgs": organizations})
    return log_and_write(resp, 200, function)


def create_organization_handler():
    """HTTP handler for creating a new organization.

    Equivalent to Go's CreateOrganizationHandler.

    POST /org?admin=<admin_email>
    Body: {"org": "<org_name>"}
    Response: {"Message": "Successfully created new organization"}
    """
    function = "CreateOrganizationHandler"

    if request.method != "POST":
        return log_and_write_err(
            "Only POST requests are allowed at this route",
            405,
            function,
        )

    try:
        body = request.get_json(force=True)
    except Exception as e:
        return log_and_write_status_bad_request(e, function)

    if body is None:
        return log_and_write_status_bad_request(
            "Malformed request body", function
        )

    org_name = body.get("org", "")

    admin = request.args.get("admin")
    if admin is None:
        return log_and_write_err(
            "request query parameters must contain 'admin'",
            400,
            function,
        )

    try:
        _create_organization(org_name, admin)
    except Exception as e:
        return log_and_write_status_internal_server_error(e, function)

    return log_and_write(
        str_to_bytes("Successfully created new organization"),
        201,
        function,
    )


def cross_match_trait_handler():
    """HTTP handler for setting a cross-match trait for an organization.

    Equivalent to Go's CrossMatchTraitHandler.

    POST /crossmatchtrait?org=<org_name>
    Body: {"trait": "<trait_value>"}
    Response: {"Message": "Successfully set the cross match trait"}
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

    try:
        body = request.get_json(force=True)
    except Exception:
        return log_and_write_err("Malformed body.", 400, function)

    if body is None:
        return log_and_write_err(
            "Request body is malformed", 400, function
        )

    trait = body.get("trait", "")

    try:
        _set_cross_match_trait(orgname, trait)
    except Exception as e:
        return log_and_write_status_internal_server_error(e, function)

    return log_and_write(
        str_to_bytes("Successfully set the cross match trait"),
        201,
        function,
    )


# --- Database query functions ---


def _get_organizations(admin):
    """Fetch all organization names for a given admin.

    Equivalent to Go's getOrganizations.
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


def _create_organization(name, admin):
    """Create a new organization.

    Equivalent to Go's createOrganization.
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
    """Retrieve the cross-match trait for an organization.

    Returns an empty string if the trait is NULL.

    Equivalent to Go's GetCrossMatchTrait. Exported for use by the
    pairing algorithm in future milestones.
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
            return row[0] if row[0] is not None else ""
    finally:
        conn.close()


def _set_cross_match_trait(orgname, cross_match_trait):
    """Update the cross-match trait for an organization.

    Equivalent to Go's setCrossMatchTrait.
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

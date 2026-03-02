"""Organization management business logic.

Implements the database operations from the Go application's org.go:
- getOrganizations: list organizations by admin
- createOrganization: create a new organization
- GetCrossMatchTrait: get the cross-match trait for an org
- setCrossMatchTrait: set the cross-match trait for an org
"""

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from infra.models import Organization


def get_organizations(db: Session, admin: str) -> list[str]:
    """Get all organization names for a given admin.

    Equivalent to Go's getOrganizations function.

    Args:
        db: SQLAlchemy session.
        admin: Admin email address.

    Returns:
        List of organization names.
    """
    stmt = select(Organization.name).where(Organization.admin == admin)
    result = db.execute(stmt)
    return [row[0] for row in result.all()]


def create_organization(db: Session, name: str, admin: str) -> None:
    """Create a new organization.

    Equivalent to Go's createOrganization function.

    Args:
        db: SQLAlchemy session.
        name: Organization name (must not be empty).
        admin: Admin email address.

    Raises:
        ValueError: If name is empty.
    """
    if not name:
        raise ValueError("Organization name cannot be an empty string")

    org = Organization(name=name, admin=admin)
    db.add(org)
    db.commit()


def get_cross_match_trait(db: Session, orgname: str) -> str:
    """Get the cross-match trait for an organization.

    Equivalent to Go's GetCrossMatchTrait function.
    Returns empty string if the trait is NULL or the org is not found.

    Args:
        db: SQLAlchemy session.
        orgname: Organization name.

    Returns:
        The cross-match trait string, or empty string if not set.
    """
    stmt = select(Organization.cross_match_trait).where(
        Organization.name == orgname
    )
    result = db.execute(stmt).first()
    if result is None or result[0] is None:
        return ""
    return result[0]


def set_cross_match_trait(db: Session, orgname: str, trait: str) -> None:
    """Set the cross-match trait for an organization.

    Equivalent to Go's setCrossMatchTrait function.

    Args:
        db: SQLAlchemy session.
        orgname: Organization name.
        trait: The trait value to set.
    """
    stmt = (
        update(Organization)
        .where(Organization.name == orgname)
        .values(cross_match_trait=trait)
    )
    db.execute(stmt)
    db.commit()

"""Pydantic schemas for organization API operations."""

from pydantic import BaseModel


class CreateOrganizationRequest(BaseModel):
    """Request body for creating a new organization.

    Attributes:
        org: The name of the organization to create.
    """

    org: str


class SetCrossMatchTraitRequest(BaseModel):
    """Request body for setting a cross-match trait on an organization.

    Attributes:
        trait: The cross-match trait value to set.
    """

    trait: str


class OrganizationsResponse(BaseModel):
    """Response body for listing organizations.

    Attributes:
        orgs: List of organization names.
    """

    orgs: list[str]

"""Pydantic schemas for organization-related request/response models.

Matches the Go application's request body structures:
- CreateOrganizationRequestBody: {"org": "<name>"}
- SetCrossMatchTraitRequestBody: {"trait": "<value>"}
"""

from pydantic import BaseModel


class CreateOrganizationRequest(BaseModel):
    """Request body for creating a new organization.

    Matches Go's CreateOrganizationRequestBody struct:
        type CreateOrganizationRequestBody struct {
            Organization string `json:"org"`
        }
    """

    org: str


class SetCrossMatchTraitRequest(BaseModel):
    """Request body for setting the cross-match trait.

    Matches Go's SetCrossMatchTraitRequestBody struct:
        type SetCrossMatchTraitRequestBody struct {
            Trait string `json:"trait"`
        }
    """

    trait: str

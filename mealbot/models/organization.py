"""SQLAlchemy ORM model for organizations."""

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


class Organization(Base):
    """Organization model mapping to the organizations table.

    Organizations are the top-level entity in Mealbot. Each organization
    is managed by an admin (identified by email) and can have members,
    rounds, and pair configurations.

    Attributes:
        name: Primary key, unique name for the organization.
        admin: Email of the admin user who manages this organization.
        cross_match_trait: Optional trait name used for cross-matching during pairing.
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    admin: Mapped[str] = mapped_column(String, nullable=False)
    cross_match_trait: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (CheckConstraint("length(admin) > 0", name="admin_not_empty"),)

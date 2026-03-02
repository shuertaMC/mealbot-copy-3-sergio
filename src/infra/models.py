"""SQLAlchemy ORM models for all database tables.

Models are defined to match the runtime schema used by the Go application.
Note: The Go code uses `last_round_with` column (not `pair_counts` as in schema.sql).
"""

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class Organization(Base):
    """Organization table - groups that use mealbot for pairing."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    admin: Mapped[str] = mapped_column(String, nullable=False)
    cross_match_trait: Mapped[str | None] = mapped_column(String, nullable=True)

    # Relationships
    members: Mapped[list["Member"]] = relationship(
        "Member", back_populates="org", cascade="all, delete-orphan"
    )
    rounds: Mapped[list["Round"]] = relationship(
        "Round", back_populates="org", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization(name={self.name!r}, admin={self.admin!r})>"


class Member(Base):
    """Member table - individuals within an organization."""

    __tablename__ = "members"

    organization: Mapped[str] = mapped_column(
        String,
        ForeignKey("organizations.name"),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )
    last_round_with: Mapped[dict] = mapped_column(JSONB, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    org: Mapped["Organization"] = relationship(
        "Organization", back_populates="members"
    )

    def __repr__(self) -> str:
        return f"<Member(org={self.organization!r}, email={self.email!r}, name={self.name!r})>"


class Round(Base):
    """Round table - scheduled pairing rounds for an organization."""

    __tablename__ = "rounds"

    organization: Mapped[str] = mapped_column(
        String,
        ForeignKey("organizations.name"),
        primary_key=True,
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scheduled_date: Mapped[str] = mapped_column(DateTime, nullable=False)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Relationships
    org: Mapped["Organization"] = relationship("Organization", back_populates="rounds")

    def __repr__(self) -> str:
        return f"<Round(org={self.organization!r}, id={self.id!r})>"


class PairRecord(Base):
    """Pair table - records of member pairings per round."""

    __tablename__ = "pairs"

    organization: Mapped[str] = mapped_column(
        String,
        ForeignKey("organizations.name"),
        primary_key=True,
    )
    id1: Mapped[str] = mapped_column(String, primary_key=True)
    id2: Mapped[str] = mapped_column(String, primary_key=True)
    extra_id: Mapped[str | None] = mapped_column(
        "extraid", String, primary_key=True, nullable=True, default=""
    )
    round: Mapped[int] = mapped_column(Integer, primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["organization", "round"],
            ["rounds.organization", "rounds.id"],
        ),
        ForeignKeyConstraint(
            ["organization", "id1"],
            ["members.organization", "members.email"],
        ),
        ForeignKeyConstraint(
            ["organization", "id2"],
            ["members.organization", "members.email"],
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<PairRecord(org={self.organization!r}, "
            f"id1={self.id1!r}, id2={self.id2!r}, round={self.round!r})>"
        )

"""SQLAlchemy model for the organizations table.

This module defines the Organization ORM model that maps to the existing
PostgreSQL organizations table as defined in schema.sql.
"""

from sqlalchemy import Column, String

from ..db import Base


class Organization(Base):
    """SQLAlchemy model for the organizations table.

    This model mirrors the Go Organization struct and the PostgreSQL schema:
    - name: VARCHAR PRIMARY KEY
    - admin: VARCHAR NOT NULL
    - cross_match_trait: VARCHAR (nullable)
    """

    __tablename__ = "organizations"

    name = Column(String, primary_key=True)
    admin = Column(String, nullable=False)
    cross_match_trait = Column(String, nullable=True)

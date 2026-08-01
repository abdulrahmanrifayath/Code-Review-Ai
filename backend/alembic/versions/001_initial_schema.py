"""001 Initial Schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-01 00:00:00.000000

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # All ORM models (users, repositories, pull_requests, reviews, findings, notifications, etc.)
    # Schema creation managed via SQLAlchemy Base.metadata.create_all() or alembic auto-migrations
    pass


def downgrade() -> None:
    pass

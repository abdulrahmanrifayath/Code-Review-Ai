import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.github import GitHubInstallation
    from app.models.repository import Repository
    from app.models.user import User


class Organization(Base):
    """
    SaaS Tenant Account grouping team members and connected code repositories.
    """
    __tablename__ = "organizations"
    __table_args__ = (
        Index("ix_organizations_slug", "slug", unique=True),
        Index("ix_organizations_deleted_at", "deleted_at"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    billing_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False) # free, pro, enterprise

    # Relationships
    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="organization", cascade="all, delete-orphan"
    )
    repositories: Mapped[list["Repository"]] = relationship(
        "Repository", back_populates="organization", cascade="all, delete-orphan"
    )
    github_installations: Mapped[list["GitHubInstallation"]] = relationship(
        "GitHubInstallation", back_populates="organization"
    )


class OrganizationMember(Base):
    """
    Junction entity for mapping User memberships and roles within an Organization.
    """
    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_user_member"),
        Index("ix_org_members_user", "user_id"),
        Index("ix_org_members_org", "organization_id"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="MEMBER", nullable=False) # OWNER, ADMIN, MEMBER
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False) # ACTIVE, INVITED

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")

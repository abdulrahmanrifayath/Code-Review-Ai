import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, BigInteger, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.repository import Repository
    from app.models.user import User


class GitHubInstallation(Base):
    """
    GitHub App installation metadata, authorization tokens, and webhook secrets.
    """
    __tablename__ = "github_installations"

    installation_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False) # User, Organization

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), index=True, nullable=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )

    permissions: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    events: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    webhook_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="github_installations")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="github_installations")
    repositories: Mapped[list["Repository"]] = relationship("Repository", back_populates="github_installation")

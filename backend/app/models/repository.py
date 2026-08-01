import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, BigInteger, Boolean, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.github import GitHubInstallation
    from app.models.organization import Organization
    from app.models.pull_request import PullRequest


class Repository(Base):
    """
    Connected code repository registered for automated AI code reviews.
    """
    __tablename__ = "repositories"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=True
    )
    github_installation_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("github_installations.id", ondelete="SET NULL"), nullable=True
    )

    github_repo_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    owner_login: Mapped[str] = mapped_column(String(100), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(100), default="main", nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True)

    stargazers_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    forks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    open_issues_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    settings: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="repositories")
    github_installation: Mapped[Optional["GitHubInstallation"]] = relationship("GitHubInstallation", back_populates="repositories")
    pull_requests: Mapped[list["PullRequest"]] = relationship("PullRequest", back_populates="repository", cascade="all, delete-orphan")

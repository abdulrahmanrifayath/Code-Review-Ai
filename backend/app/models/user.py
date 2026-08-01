from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.activity import ActivityLog
    from app.models.github import GitHubInstallation
    from app.models.notification import Notification
    from app.models.notification_preference import NotificationPreference
    from app.models.organization import OrganizationMember
    from app.models.session import UserSession


class User(Base):
    """
    Platform User model for authentication, profile info, and workspace authorization.
    """
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email", unique=True),
        Index("ix_users_username", "username", unique=True),
        Index("ix_users_github_user_id", "github_user_id", unique=True),
    )

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="DEVELOPER", nullable=False) # ADMIN, REVIEWER, DEVELOPER
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # GitHub OAuth & Integration (Encrypted)
    github_user_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    encrypted_github_token: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    sessions: Mapped[list[UserSession]] = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    memberships: Mapped[list[OrganizationMember]] = relationship(
        "OrganizationMember", back_populates="user", cascade="all, delete-orphan"
    )
    github_installations: Mapped[list[GitHubInstallation]] = relationship(
        "GitHubInstallation", back_populates="user"
    )
    notifications: Mapped[list[Notification]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    notification_preference: Mapped[NotificationPreference | None] = relationship(
        "NotificationPreference", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    activity_logs: Mapped[list[ActivityLog]] = relationship(
        "ActivityLog", back_populates="user"
    )

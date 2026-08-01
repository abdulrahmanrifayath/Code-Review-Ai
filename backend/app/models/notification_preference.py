import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class NotificationPreference(Base):
    """
    User notification preferences for multi-channel dispatches (GitHub, Email, Slack, Discord, In-App).
    """
    __tablename__ = "notification_preferences"
    __table_args__ = (
        Index("ix_notification_preferences_user_id", "user_id", unique=True),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    slack_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    slack_webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    discord_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    discord_webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    github_comments_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notification_preference")

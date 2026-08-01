import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest
    from app.models.user import User


class ActivityLog(Base):
    """
    Platform-wide audit log tracking user operations, API calls, and system events.
    """
    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_user_id", "user_id"),
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # repo_connected, review_requested
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False) # repository, pull_request, user
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)

    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="activity_logs")


class ReviewHistory(Base):
    """
    Timeline audit log capturing state transitions and review iterations for a Pull Request.
    """
    __tablename__ = "review_histories"
    __table_args__ = (
        Index("ix_review_histories_pr_id", "pull_request_id"),
    )

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # status_change, re_review, comment_posted
    previous_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    new_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    actor: Mapped[str | None] = mapped_column(String(150), nullable=True) # system, bot, user
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="review_histories")

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.repository import Repository


class WebhookEvent(Base):
    """
    Audit log and idempotency model for incoming GitHub Webhook events.
    """
    __tablename__ = "webhook_events"

    delivery_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # pull_request, push, ping
    action: Mapped[str | None] = mapped_column(String(100), nullable=True) # opened, synchronize, closed, reopened

    repository_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("repositories.id", ondelete="SET NULL"), nullable=True
    )

    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="RECEIVED", nullable=False, index=True) # RECEIVED, PROCESSED, DUPLICATE, FAILED, IGNORED
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    repository: Mapped[Optional["Repository"]] = relationship("Repository")

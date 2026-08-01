import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest
    from app.models.review_job import ReviewJob


class AIReview(Base):
    """
    AI-generated overall Pull Request code review summary and inline review comments.
    """
    __tablename__ = "ai_reviews"
    __table_args__ = (
        Index("ix_ai_reviews_pr_id", "pull_request_id"),
        Index("ix_ai_reviews_job_id", "review_job_id"),
    )

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False
    )
    review_job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("review_jobs.id", ondelete="SET NULL"), nullable=True
    )

    summary: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=100, nullable=False) # Quality score 0 - 100
    recommendation: Mapped[str] = mapped_column(String(50), default="COMMENT", nullable=False) # APPROVE, REQUEST_CHANGES, COMMENT

    inline_comments: Mapped[list[dict[str, Any]] | None] = mapped_column(JSON, nullable=True) # Line comments array
    llm_model: Mapped[str] = mapped_column(String(100), default="gpt-4o", nullable=False)
    token_usage: Mapped[dict[str, int] | None] = mapped_column(JSON, nullable=True)

    posted_to_github: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="ai_reviews")
    review_job: Mapped[Optional["ReviewJob"]] = relationship("ReviewJob", back_populates="ai_reviews")

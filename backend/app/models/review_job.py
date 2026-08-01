import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ai_review import AIReview
    from app.models.analysis import AnalysisResult
    from app.models.pull_request import PullRequest


class ReviewJob(Base):
    """
    Asynchronous background job tracking automated code review analysis execution.
    """
    __tablename__ = "review_jobs"
    __table_args__ = (
        Index("ix_review_jobs_pr_id", "pull_request_id"),
    )

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="QUEUED", nullable=False, index=True) # QUEUED, PROCESSING, COMPLETED, FAILED
    trigger_event: Mapped[str] = mapped_column(String(50), default="pr_opened", nullable=False)
    worker_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    traceback: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="review_jobs")
    analysis_results: Mapped[list["AnalysisResult"]] = relationship("AnalysisResult", back_populates="review_job", cascade="all, delete-orphan")
    ai_reviews: Mapped[list["AIReview"]] = relationship("AIReview", back_populates="review_job")

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest
    from app.models.repository import Repository


class QualityHistory(Base):
    """
    Stores historical snapshots of code quality metrics for repositories and pull requests over time.
    """
    __tablename__ = "quality_history"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), index=True, nullable=False
    )
    pull_request_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), index=True, nullable=True
    )

    maintainability_score: Mapped[int] = mapped_column(Integer, nullable=False, default=85)
    technical_debt_hours: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    complexity_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    doc_coverage_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=100.0)
    architecture_score: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    overall_quality_score: Mapped[int] = mapped_column(Integer, nullable=False, default=88)
    grade: Mapped[str] = mapped_column(String(10), nullable=False, default="A")

    # Relationships
    repository: Mapped["Repository"] = relationship("Repository")
    pull_request: Mapped[Optional["PullRequest"]] = relationship("PullRequest")

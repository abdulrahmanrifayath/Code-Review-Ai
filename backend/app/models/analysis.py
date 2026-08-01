import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.findings import CodeSmell, PerformanceFinding, SecurityFinding
    from app.models.review_job import ReviewJob


class AnalysisResult(Base):
    """
    Static analysis parser output (Tree-sitter ASTs, ESLint/Pylint diagnostics).
    """
    __tablename__ = "analysis_results"
    __table_args__ = (
        Index("ix_analysis_results_job_id", "review_job_id"),
    )

    review_job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("review_jobs.id", ondelete="CASCADE"), nullable=False
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # tree-sitter, eslint, pylint, checkstyle
    category: Mapped[str] = mapped_column(String(50), nullable=False) # ast_parse, linter, static_analysis

    raw_output: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    parsed_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    review_job: Mapped["ReviewJob"] = relationship("ReviewJob", back_populates="analysis_results")
    security_findings: Mapped[list["SecurityFinding"]] = relationship("SecurityFinding", back_populates="analysis_result", cascade="all, delete-orphan")
    performance_findings: Mapped[list["PerformanceFinding"]] = relationship("PerformanceFinding", back_populates="analysis_result", cascade="all, delete-orphan")
    code_smells: Mapped[list["CodeSmell"]] = relationship("CodeSmell", back_populates="analysis_result", cascade="all, delete-orphan")

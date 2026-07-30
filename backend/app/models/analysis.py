import uuid
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import ForeignKey, Index, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.review_job import ReviewJob
    from app.models.findings import SecurityFinding, PerformanceFinding, CodeSmell


class AnalysisResult(Base):
    """
    Static analysis parser output (Tree-sitter ASTs, ESLint/Pylint diagnostics).
    """
    __tablename__ = "analysis_results"
    __table_args__ = (
        Index("ix_analysis_results_job_id", "review_job_id"),
        Index("ix_analysis_results_tool", "tool_name"),
    )

    review_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("review_jobs.id", ondelete="CASCADE"), nullable=False
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # tree-sitter, eslint, pylint, checkstyle
    category: Mapped[str] = mapped_column(String(50), nullable=False) # ast_parse, linter, static_analysis
    
    raw_output: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    parsed_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    review_job: Mapped["ReviewJob"] = relationship("ReviewJob", back_populates="analysis_results")
    security_findings: Mapped[List["SecurityFinding"]] = relationship("SecurityFinding", back_populates="analysis_result", cascade="all, delete-orphan")
    performance_findings: Mapped[List["PerformanceFinding"]] = relationship("PerformanceFinding", back_populates="analysis_result", cascade="all, delete-orphan")
    code_smells: Mapped[List["CodeSmell"]] = relationship("CodeSmell", back_populates="analysis_result", cascade="all, delete-orphan")

import uuid
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.analysis import AnalysisResult


class SecurityFinding(Base):
    """
    Detected SAST security vulnerability or secret leakage finding.
    """
    __tablename__ = "security_findings"
    __table_args__ = (
        Index("ix_sec_findings_analysis_id", "analysis_result_id"),
        Index("ix_sec_findings_severity", "severity"),
        Index("ix_sec_findings_cwe", "cwe_id"),
    )

    analysis_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False
    )
    rule_id: Mapped[str] = mapped_column(String(150), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="HIGH", nullable=False, index=True) # CRITICAL, HIGH, MEDIUM, LOW
    cwe_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # e.g. CWE-89
    
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    start_column: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    end_column: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    code_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    remediation_suggestion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    analysis_result: Mapped["AnalysisResult"] = relationship("AnalysisResult", back_populates="security_findings")


class PerformanceFinding(Base):
    """
    Detected performance bottleneck (e.g. O(N^2) loops, memory leak risks, missing DB index hints).
    """
    __tablename__ = "performance_findings"
    __table_args__ = (
        Index("ix_perf_findings_analysis_id", "analysis_result_id"),
        Index("ix_perf_findings_impact", "impact_level"),
    )

    analysis_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    impact_level: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False) # HIGH, MEDIUM, LOW
    complexity_delta: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # e.g., O(N) -> O(N^2)
    
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    
    code_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    optimization_suggestion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    analysis_result: Mapped["AnalysisResult"] = relationship("AnalysisResult", back_populates="performance_findings")


class CodeSmell(Base):
    """
    Code quality maintenance smell (high complexity, duplication, dead code).
    """
    __tablename__ = "code_smells"
    __table_args__ = (
        Index("ix_code_smells_analysis_id", "analysis_result_id"),
        Index("ix_code_smells_type", "smell_type"),
    )

    analysis_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("analysis_results.id", ondelete="CASCADE"), nullable=False
    )
    smell_type: Mapped[str] = mapped_column(String(100), nullable=False) # cyclomatic_complexity, duplicated_code, long_method
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="WARNING", nullable=False) # INFO, WARNING, ERROR
    
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    
    refactoring_tip: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    analysis_result: Mapped["AnalysisResult"] = relationship("AnalysisResult", back_populates="code_smells")

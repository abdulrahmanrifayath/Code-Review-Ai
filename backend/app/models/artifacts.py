import uuid
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import Boolean, ForeignKey, Index, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest


class GeneratedTest(Base):
    """
    AI-generated unit or integration test cases targeting changed source code files.
    """
    __tablename__ = "generated_tests"
    __table_args__ = (
        Index("ix_generated_tests_pr_id", "pull_request_id"),
        Index("ix_generated_tests_target", "target_file"),
    )

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False
    )
    test_framework: Mapped[str] = mapped_column(String(50), default="pytest", nullable=False) # pytest, jest, unittest
    target_file: Mapped[str] = mapped_column(String(500), nullable=False)
    generated_code: Mapped[str] = mapped_column(Text, nullable=False)
    is_passing: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="generated_tests")


class GeneratedDocumentation(Base):
    """
    AI-generated code documentation (docstrings, OpenAPI updates, changelog entries).
    """
    __tablename__ = "generated_docs"
    __table_args__ = (
        Index("ix_generated_docs_pr_id", "pull_request_id"),
        Index("ix_generated_docs_type", "doc_type"),
    )

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False
    )
    doc_type: Mapped[str] = mapped_column(String(50), default="docstring", nullable=False) # docstring, api_ref, changelog
    target_file: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="generated_docs")


class ReviewReport(Base):
    """
    Exportable executive review report (Markdown, PDF, or JSON).
    """
    __tablename__ = "review_reports"
    __table_args__ = (
        Index("ix_review_reports_pr_id", "pull_request_id"),
        Index("ix_review_reports_type", "report_type"),
    )

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False
    )
    report_type: Mapped[str] = mapped_column(String(50), default="MARKDOWN", nullable=False) # MARKDOWN, PDF, JSON
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="review_reports")

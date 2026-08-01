import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, Boolean, ForeignKey, Index, String, Text, Uuid
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

    pull_request_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=True
    )
    test_framework: Mapped[str] = mapped_column(String(50), default="pytest", nullable=False) # pytest, jest, junit
    test_category: Mapped[str] = mapped_column(String(50), default="comprehensive", nullable=False) # positive, negative, boundary, mock, comprehensive
    test_name: Mapped[str | None] = mapped_column(String(255), nullable=True) # e.g. test_user_service.py
    target_file: Mapped[str] = mapped_column(String(500), nullable=False)
    generated_code: Mapped[str] = mapped_column(Text, nullable=False)
    workflow_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_passing: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="generated_tests")


class GeneratedDocumentation(Base):
    """
    AI-generated code documentation (docstrings, javadoc, readme, api_doc, missing_comments, function_description, usage_examples).
    """
    __tablename__ = "generated_docs"
    __table_args__ = (
        Index("ix_generated_docs_pr_id", "pull_request_id"),
        Index("ix_generated_docs_type", "doc_type"),
    )

    pull_request_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=True
    )
    doc_type: Mapped[str] = mapped_column(String(50), default="docstring", nullable=False) # docstring, javadoc, readme, api_doc, missing_comments, function_description, usage_examples
    doc_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_file: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    pull_request: Mapped[Optional["PullRequest"]] = relationship("PullRequest", back_populates="generated_docs")


class ReviewReport(Base):
    """
    Exportable executive review report (PDF, MARKDOWN, HTML, JSON).
    """
    __tablename__ = "review_reports"
    __table_args__ = (
        Index("ix_review_reports_pr_id", "pull_request_id"),
        Index("ix_review_reports_type", "report_type"),
    )

    pull_request_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=True
    )
    report_type: Mapped[str] = mapped_column(String(50), default="MARKDOWN", nullable=False) # MARKDOWN, PDF, HTML, JSON
    report_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Relationships
    pull_request: Mapped[Optional["PullRequest"]] = relationship("PullRequest", back_populates="review_reports")

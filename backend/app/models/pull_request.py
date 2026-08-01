import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.activity import ReviewHistory
    from app.models.ai_review import AIReview
    from app.models.artifacts import GeneratedDocumentation, GeneratedTest, ReviewReport
    from app.models.repository import Repository
    from app.models.review_job import ReviewJob


class PullRequest(Base):
    """
    GitHub Pull Request entity under review.
    """
    __tablename__ = "pull_requests"
    __table_args__ = (
        UniqueConstraint("repository_id", "pr_number", name="uq_repo_pr_number"),
        Index("ix_pull_requests_repo_pr", "repository_id", "pr_number"),
        Index("ix_pull_requests_head_sha", "head_sha"),
    )

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False
    )
    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str] = mapped_column(String(50), default="open", nullable=False) # open, closed, merged
    head_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    base_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    head_sha: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    author_login: Mapped[str] = mapped_column(String(100), nullable=False)
    html_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    additions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deletions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    changed_files_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    repository: Mapped["Repository"] = relationship("Repository", back_populates="pull_requests")
    commits: Mapped[list["Commit"]] = relationship("Commit", back_populates="pull_request", cascade="all, delete-orphan")
    changed_files: Mapped[list["ChangedFile"]] = relationship("ChangedFile", back_populates="pull_request", cascade="all, delete-orphan")
    review_jobs: Mapped[list["ReviewJob"]] = relationship("ReviewJob", back_populates="pull_request", cascade="all, delete-orphan")
    ai_reviews: Mapped[list["AIReview"]] = relationship("AIReview", back_populates="pull_request", cascade="all, delete-orphan")
    generated_tests: Mapped[list["GeneratedTest"]] = relationship("GeneratedTest", back_populates="pull_request", cascade="all, delete-orphan")
    generated_docs: Mapped[list["GeneratedDocumentation"]] = relationship("GeneratedDocumentation", back_populates="pull_request", cascade="all, delete-orphan")
    review_reports: Mapped[list["ReviewReport"]] = relationship("ReviewReport", back_populates="pull_request", cascade="all, delete-orphan")
    review_histories: Mapped[list["ReviewHistory"]] = relationship("ReviewHistory", back_populates="pull_request", cascade="all, delete-orphan")


class Commit(Base):
    """
    Individual git commit associated with a Pull Request.
    """
    __tablename__ = "commits"
    __table_args__ = (
        Index("ix_commits_pr_id", "pull_request_id"),
        Index("ix_commits_sha", "commit_sha"),
    )

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False
    )
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    author_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    commit_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    additions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deletions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="commits")


class ChangedFile(Base):
    """
    Individual modified file patch/diff in a Pull Request.
    """
    __tablename__ = "changed_files"
    __table_args__ = (
        Index("ix_changed_files_pr_id", "pull_request_id"),
        Index("ix_changed_files_filename", "filename"),
        Index("ix_changed_files_language", "language"),
    )

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pull_requests.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="modified", nullable=False) # added, modified, removed, renamed
    previous_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    language: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)

    additions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deletions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    patch: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_diff: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    raw_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationships
    pull_request: Mapped["PullRequest"] = relationship("PullRequest", back_populates="changed_files")

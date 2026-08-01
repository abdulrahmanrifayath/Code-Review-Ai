from typing import Any

from sqlalchemy import JSON, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CodeReview(Base):
    __tablename__ = "code_reviews"

    repository_id: Mapped[int] = mapped_column(Integer, ForeignKey("repositories.id"), nullable=False)
    pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False) # PENDING, IN_PROGRESS, COMPLETED, FAILED
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    findings: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CodeReviewBase(BaseModel):
    repository_id: int
    pr_number: int
    commit_sha: str


class CodeReviewCreate(CodeReviewBase):
    pass


class CodeReviewResponse(CodeReviewBase):
    id: int
    status: str
    summary: str | None = None
    findings: dict[str, Any] | None = None
    metrics: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

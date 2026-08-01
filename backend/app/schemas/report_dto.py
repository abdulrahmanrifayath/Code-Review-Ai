import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ReportGenerationRequest(BaseModel):
    repository_full_name: str
    pull_request_id: uuid.UUID | None = None
    pr_number: int | None = 1
    format: str = "MARKDOWN" # PDF, MARKDOWN, HTML, JSON


class ReviewReportItem(BaseModel):
    id: uuid.UUID | None = None
    pull_request_id: uuid.UUID | None = None
    report_type: str
    report_title: str | None = None
    content: str | None = None
    report_metadata: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportGeneratorResponse(BaseModel):
    report_id: uuid.UUID
    repository_full_name: str
    pr_number: int | None = 1
    report_type: str
    report_title: str
    content: str
    report_metadata: dict[str, Any]
    download_url: str
    created_at: datetime

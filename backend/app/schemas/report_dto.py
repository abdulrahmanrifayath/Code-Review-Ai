import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class ReportGenerationRequest(BaseModel):
    repository_full_name: str
    pull_request_id: Optional[uuid.UUID] = None
    pr_number: Optional[int] = 1
    format: str = "MARKDOWN" # PDF, MARKDOWN, HTML, JSON


class ReviewReportItem(BaseModel):
    id: Optional[uuid.UUID] = None
    pull_request_id: Optional[uuid.UUID] = None
    report_type: str
    report_title: Optional[str] = None
    content: Optional[str] = None
    report_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportGeneratorResponse(BaseModel):
    report_id: uuid.UUID
    repository_full_name: str
    pr_number: Optional[int] = 1
    report_type: str
    report_title: str
    content: str
    report_metadata: Dict[str, Any]
    download_url: str
    created_at: datetime

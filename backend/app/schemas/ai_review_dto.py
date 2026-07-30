import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class AIFindingItem(BaseModel):
    severity: str # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str # BUG, SECURITY, PERFORMANCE, NAMING, ARCHITECTURE, MAINTAINABILITY, SOLID_PRINCIPLE
    explanation: str
    suggested_fix: Optional[str] = None
    confidence_score: float
    file_path: str
    line_number: int


class AIInlineComment(BaseModel):
    path: str
    line: int
    body: str
    suggestion: Optional[str] = None


class AIReviewResponse(BaseModel):
    id: uuid.UUID
    pull_request_id: uuid.UUID
    summary: str
    quality_score: int
    recommendation: str # APPROVE, REQUEST_CHANGES, COMMENT
    findings: List[AIFindingItem]
    inline_comments: List[AIInlineComment]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GenerateReviewRequest(BaseModel):
    force_refresh: bool = False

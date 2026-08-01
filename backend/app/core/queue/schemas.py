from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class QueueType(str, Enum):
    WEBHOOK_PROCESSING = "webhook_processing"
    AI_ANALYSIS = "ai_analysis"
    STATIC_ANALYSIS = "static_analysis"
    REPORT_GENERATION = "report_generation"
    NOTIFICATIONS = "notifications"


class JobPayload(BaseModel):
    job_id: str
    queue_type: QueueType
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: JobStatus = JobStatus.QUEUED
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    worker_id: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class QueueStats(BaseModel):
    queue_name: str
    pending_jobs: int
    processing_jobs: int
    completed_jobs: int
    failed_jobs: int
    dlq_jobs: int
    retrying_jobs: int

from enum import Enum
from typing import Any

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
    payload: dict[str, Any] = Field(default_factory=dict)
    status: JobStatus = JobStatus.QUEUED
    created_at: str
    started_at: str | None = None
    completed_at: str | None = None
    worker_id: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: str | None = None
    traceback: str | None = None
    result: dict[str, Any] | None = None


class QueueStats(BaseModel):
    queue_name: str
    pending_jobs: int
    processing_jobs: int
    completed_jobs: int
    failed_jobs: int
    dlq_jobs: int
    retrying_jobs: int

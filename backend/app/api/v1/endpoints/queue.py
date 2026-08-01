from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.core.queue.redis_queue import queue_manager
from app.core.queue.schemas import JobPayload, JobStatus, QueueStats, QueueType

router = APIRouter()


class EnqueueJobRequest(BaseModel):
    queue_type: QueueType
    action: str
    payload: dict[str, Any]
    max_retries: int | None = 3


class QueuePurgeRequest(BaseModel):
    queue_type: QueueType | None = None
    dlq: bool = False


@router.get("/stats", response_model=list[QueueStats], status_code=status.HTTP_200_OK)
async def get_queue_statistics():
    """
    Returns real-time depth metrics, active workers, completed/failed job counts,
    and DLQ size across all Redis queues.
    """
    try:
        return await queue_manager.get_all_queue_stats()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve queue stats: {exc!s}",
        )


@router.get("/jobs", response_model=list[JobPayload], status_code=status.HTTP_200_OK)
async def list_jobs(
    status_filter: JobStatus | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
):
    """
    Lists Redis background jobs filtered by status (queued, processing, completed, failed, retrying).
    """
    try:
        return await queue_manager.list_jobs_by_status(status=status_filter, limit=limit)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list queue jobs: {exc!s}",
        )


@router.get("/jobs/{job_id}", response_model=JobPayload, status_code=status.HTTP_200_OK)
async def get_job_details(job_id: str):
    """
    Retrieves full execution details, retry count, traceback, and result of a job.
    """
    job = await queue_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{job_id}' not found.",
        )
    return job


@router.post("/jobs", response_model=JobPayload, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_new_job(req: EnqueueJobRequest):
    """
    Manually enqueues a new background job into Redis.
    """
    try:
        return await queue_manager.enqueue_job(
            queue_type=req.queue_type,
            action=req.action,
            payload=req.payload,
            max_retries=req.max_retries or 3,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enqueue job: {exc!s}",
        )


@router.post("/jobs/{job_id}/retry", response_model=JobPayload, status_code=status.HTTP_200_OK)
async def retry_failed_job(job_id: str):
    """
    Manually triggers re-enqueuing of a failed or DLQ job.
    """
    job = await queue_manager.retry_failed_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed or DLQ job with ID '{job_id}' not found.",
        )
    return job


@router.post("/purge", status_code=status.HTTP_200_OK)
async def purge_queue(req: QueuePurgeRequest):
    """
    Purges jobs from a specific queue or Dead Letter Queue.
    """
    purged_count = await queue_manager.purge_queue(queue_type=req.queue_type, dlq=req.dlq)
    return {
        "message": f"Successfully purged {purged_count} job(s).",
        "purged_count": purged_count,
        "queue_type": req.queue_type.value if req.queue_type else None,
        "dlq": req.dlq,
    }

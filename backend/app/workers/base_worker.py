import asyncio
import logging
import traceback
import uuid
from typing import Any

from app.core.queue.redis_queue import RedisQueueManager, queue_manager
from app.core.queue.schemas import JobPayload, JobStatus, QueueType

logger = logging.getLogger("reviewai.worker")


class BaseWorker:
    """
    Base asynchronous background worker handling loop popping, task execution,
    exception handling, performance logging, and exponential retry backoff.
    """

    def __init__(
        self,
        queue_type: QueueType,
        worker_id: str | None = None,
        queue_mgr: RedisQueueManager | None = None,
        poll_interval: float = 1.0,
    ):
        self.queue_type = queue_type
        self.worker_id = worker_id or f"worker_{queue_type.value}_{uuid.uuid4().hex[:6]}"
        self.queue_mgr = queue_mgr or queue_manager
        self.poll_interval = poll_interval
        self._running = False

    async def start(self):
        """
        Starts the worker polling loop.
        """
        self._running = True
        logger.info("Starting worker '%s' for queue '%s'...", self.worker_id, self.queue_type.value)
        while self._running:
            try:
                job = await self.queue_mgr.pop_job(self.queue_type, timeout=int(self.poll_interval))
                if job:
                    await self._process_job_safe(job)
                else:
                    await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                logger.info("Worker '%s' received cancellation.", self.worker_id)
                self._running = False
                break
            except Exception as exc:
                logger.error("Error in worker '%s' main loop: %s", self.worker_id, exc, exc_info=True)
                await asyncio.sleep(2.0)

    def stop(self):
        """
        Signals the worker loop to stop.
        """
        self._running = False

    async def _process_job_safe(self, job: JobPayload):
        """
        Executes a job with exception safety, metrics tracking, and retry backoff.
        """
        job_id = job.job_id
        logger.info("Worker '%s' processing job '%s' (action: %s)", self.worker_id, job_id, job.action)

        await self.queue_mgr.update_job_status(
            job_id=job_id,
            status=JobStatus.PROCESSING,
            worker_id=self.worker_id,
        )

        try:
            result = await self.process(job.action, job.payload)
            await self.queue_mgr.update_job_status(
                job_id=job_id,
                status=JobStatus.COMPLETED,
                result=result or {"status": "success"},
            )
            logger.info("Job '%s' completed successfully by worker '%s'.", job_id, self.worker_id)

        except Exception as exc:
            tb_str = traceback.format_exc()
            err_msg = str(exc)
            logger.error(
                "Job '%s' failed in worker '%s': %s",
                job_id, self.worker_id, err_msg
            )

            # Schedule Exponential Backoff Retry or DLQ
            is_retrying, _ = await self.queue_mgr.schedule_retry(
                job_id=job_id,
                error_message=err_msg,
                traceback_str=tb_str,
            )
            if not is_retrying:
                logger.error("Job '%s' moved to DLQ permanently.", job_id)

    async def process(self, action: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        """
        Abstract method to be overridden by specialized worker implementations.
        """
        raise NotImplementedError("Subclasses must implement process()")

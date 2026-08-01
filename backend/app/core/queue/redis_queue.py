import logging
import time
import uuid
from datetime import UTC, datetime
from typing import Any

try:
    import redis.asyncio as redis
except ImportError:
    redis = None  # Handled at runtime when connecting
from app.core.config import settings
from app.core.queue.schemas import JobPayload, JobStatus, QueueStats, QueueType

logger = logging.getLogger("reviewai.queue")


class RedisQueueManager:
    """
    Asynchronous Redis Queue Manager providing job enqueueing, execution state tracking,
    exponential backoff retry scheduling, dead-letter queue (DLQ) routing, and metrics monitoring.
    """

    def __init__(self, redis_url: str | None = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self._redis_client: redis.Redis | None = None

    async def get_redis(self):
        """
        Retrieves or initializes the async Redis client connection.
        """
        if self._redis_client is None:
            if redis is None:
                raise RuntimeError("redis package is not installed. Run 'pip install redis>=5.0.4'.")
            self._redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
            )
        return self._redis_client

    async def close(self):
        """
        Closes the Redis client connection.
        """
        if self._redis_client is not None:
            await self._redis_client.close()
            self._redis_client = None

    def _get_queue_key(self, queue_type: str) -> str:
        return f"queue:{queue_type}"

    def _get_job_key(self, job_id: str) -> str:
        return f"job:{job_id}"

    def _get_retry_zset_key(self) -> str:
        return "queue:retry_zset"

    def _get_dlq_key(self) -> str:
        return "queue:dlq"

    async def enqueue_job(
        self,
        queue_type: QueueType,
        action: str,
        payload: dict[str, Any],
        max_retries: int = 3,
        job_id: str | None = None,
    ) -> JobPayload:
        """
        Enqueues a new background job into Redis.
        """
        client = await self.get_redis()
        j_id = job_id or f"job_{uuid.uuid4().hex[:12]}"
        now_str = datetime.now(UTC).isoformat()

        job_data = JobPayload(
            job_id=j_id,
            queue_type=queue_type,
            action=action,
            payload=payload,
            status=JobStatus.QUEUED,
            created_at=now_str,
            max_retries=max_retries,
            retry_count=0,
        )

        job_key = self._get_job_key(j_id)
        queue_key = self._get_queue_key(queue_type.value)

        # Store job details hash
        await client.hset(job_key, mapping={
            "data": job_data.model_dump_json(),
            "status": JobStatus.QUEUED.value,
            "created_at": now_str,
        })

        # Push to FIFO Redis List
        await client.rpush(queue_key, j_id)

        # Track in active set for statistics
        await client.sadd(f"jobs:status:{JobStatus.QUEUED.value}", j_id)

        logger.info("Enqueued job '%s' into '%s' (action: %s)", j_id, queue_key, action)
        return job_data

    async def pop_job(
        self, queue_type: QueueType, timeout: int = 2
    ) -> JobPayload | None:
        """
        Pops a job from the specified Redis list (BLPOP/LPOP).
        """
        client = await self.get_redis()
        queue_key = self._get_queue_key(queue_type.value)

        # Non-blocking pop if timeout=0, otherwise blpop
        if timeout > 0:
            res = await client.blpop(queue_key, timeout=timeout)
            if not res:
                return None
            _, job_id = res
        else:
            job_id = await client.lpop(queue_key)
            if not job_id:
                return None

        return await self.get_job(job_id)

    async def get_job(self, job_id: str) -> JobPayload | None:
        """
        Fetches job payload by job ID.
        """
        client = await self.get_redis()
        job_key = self._get_job_key(job_id)
        raw_json = await client.hget(job_key, "data")
        if not raw_json:
            return None
        try:
            return JobPayload.model_validate_json(raw_json)
        except Exception as exc:
            logger.error("Failed to parse job payload for '%s': %s", job_id, exc)
            return None

    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        worker_id: str | None = None,
        error_message: str | None = None,
        traceback_str: str | None = None,
        result: dict[str, Any] | None = None,
    ) -> JobPayload | None:
        """
        Updates the status, execution metadata, and result of a job.
        """
        client = await self.get_redis()
        job = await self.get_job(job_id)
        if not job:
            return None

        old_status = job.status
        job.status = status
        now_str = datetime.now(UTC).isoformat()

        if status == JobStatus.PROCESSING:
            job.started_at = now_str
            if worker_id:
                job.worker_id = worker_id
        elif status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            job.completed_at = now_str
            if result:
                job.result = result
            if error_message:
                job.error_message = error_message
            if traceback_str:
                job.traceback = traceback_str

        # Update Redis Hash
        job_key = self._get_job_key(job_id)
        await client.hset(job_key, mapping={
            "data": job.model_dump_json(),
            "status": status.value,
            "updated_at": now_str,
        })

        # Update status tracking sets
        await client.srem(f"jobs:status:{old_status.value}", job_id)
        await client.sadd(f"jobs:status:{status.value}", job_id)

        return job

    async def schedule_retry(
        self,
        job_id: str,
        error_message: str,
        traceback_str: str | None = None,
        base_delay_seconds: float = 2.0,
    ) -> tuple[bool, JobPayload | None]:
        """
        Schedules a failed job for exponential backoff retry, or routes to DLQ if max retries reached.
        Returns (is_retrying, updated_job)
        """
        client = await self.get_redis()
        job = await self.get_job(job_id)
        if not job:
            return False, None

        job.retry_count += 1
        if job.retry_count <= job.max_retries:
            job.status = JobStatus.RETRYING
            job.error_message = error_message
            job.traceback = traceback_str

            # Calculate Exponential Backoff delay: base * (2 ** (retry_count - 1))
            delay = base_delay_seconds * (2 ** (job.retry_count - 1))
            execute_at_timestamp = time.time() + delay

            # Update job hash
            job_key = self._get_job_key(job_id)
            await client.hset(job_key, mapping={
                "data": job.model_dump_json(),
                "status": JobStatus.RETRYING.value,
            })

            # Add to retry sorted set with timestamp score
            zset_key = self._get_retry_zset_key()
            await client.zadd(zset_key, {job_id: execute_at_timestamp})
            await client.sadd(f"jobs:status:{JobStatus.RETRYING.value}", job_id)

            logger.warning(
                "Scheduled retry #%d for job '%s' in %.2f seconds.",
                job.retry_count, job_id, delay
            )
            return True, job
        else:
            # Max retries exhausted -> Route to Dead Letter Queue (DLQ)
            job.status = JobStatus.FAILED
            job.error_message = f"Exhausted {job.max_retries} retries. Final error: {error_message}"
            job.traceback = traceback_str
            job.completed_at = datetime.now(UTC).isoformat()

            job_key = self._get_job_key(job_id)
            await client.hset(job_key, mapping={
                "data": job.model_dump_json(),
                "status": JobStatus.FAILED.value,
            })

            # SADD to DLQ
            dlq_key = self._get_dlq_key()
            await client.sadd(dlq_key, job_id)
            await client.sadd(f"jobs:status:{JobStatus.FAILED.value}", job_id)

            logger.error(
                "Job '%s' failed permanently after %d attempts. Moved to DLQ.",
                job_id, job.retry_count
            )
            return False, job

    async def process_due_retries(self) -> int:
        """
        Polls retry sorted set and moves ready jobs back to their primary queues.
        Returns count of re-enqueued jobs.
        """
        client = await self.get_redis()
        zset_key = self._get_retry_zset_key()
        now_ts = time.time()

        # Fetch jobs with score <= current timestamp
        due_job_ids = await client.zrangebyscore(zset_key, min=0, max=now_ts)
        requeued_count = 0

        for j_id in due_job_ids:
            job = await self.get_job(j_id)
            if job:
                # Remove from ZSet
                removed = await client.zrem(zset_key, j_id)
                if removed:
                    job.status = JobStatus.QUEUED
                    job_key = self._get_job_key(j_id)
                    await client.hset(job_key, mapping={
                        "data": job.model_dump_json(),
                        "status": JobStatus.QUEUED.value,
                    })

                    queue_key = self._get_queue_key(job.queue_type.value)
                    await client.rpush(queue_key, j_id)
                    await client.srem(f"jobs:status:{JobStatus.RETRYING.value}", j_id)
                    await client.sadd(f"jobs:status:{JobStatus.QUEUED.value}", j_id)
                    requeued_count += 1
                    logger.info("Re-enqueued retried job '%s' into '%s'", j_id, queue_key)

        return requeued_count

    async def retry_failed_job(self, job_id: str) -> JobPayload | None:
        """
        Manually re-enqueues a failed or DLQ job.
        """
        client = await self.get_redis()
        job = await self.get_job(job_id)
        if not job:
            return None

        # Reset retry counter and status
        job.retry_count = 0
        job.status = JobStatus.QUEUED
        job.error_message = None
        job.traceback = None
        job.completed_at = None

        job_key = self._get_job_key(job_id)
        await client.hset(job_key, mapping={
            "data": job.model_dump_json(),
            "status": JobStatus.QUEUED.value,
        })

        # Remove from DLQ if present
        dlq_key = self._get_dlq_key()
        await client.srem(dlq_key, job_id)
        await client.srem(f"jobs:status:{JobStatus.FAILED.value}", job_id)

        # Push to primary queue
        queue_key = self._get_queue_key(job.queue_type.value)
        await client.rpush(queue_key, job_id)
        await client.sadd(f"jobs:status:{JobStatus.QUEUED.value}", job_id)

        logger.info("Manually re-enqueued failed job '%s' into '%s'", job_id, queue_key)
        return job

    async def get_all_queue_stats(self) -> list[QueueStats]:
        """
        Collects real-time statistics across all queues.
        """
        client = await self.get_redis()
        stats_list: list[QueueStats] = []
        dlq_count = await client.scard(self._get_dlq_key())

        for q_type in QueueType:
            queue_key = self._get_queue_key(q_type.value)
            pending_count = await client.llen(queue_key)

            # Retrieve counts by status for this queue type if stored or total status sets
            _queued_set = await client.scard(f"jobs:status:{JobStatus.QUEUED.value}")
            proc_set = await client.scard(f"jobs:status:{JobStatus.PROCESSING.value}")
            comp_set = await client.scard(f"jobs:status:{JobStatus.COMPLETED.value}")
            fail_set = await client.scard(f"jobs:status:{JobStatus.FAILED.value}")
            retry_set = await client.scard(f"jobs:status:{JobStatus.RETRYING.value}")

            stats_list.append(
                QueueStats(
                    queue_name=q_type.value,
                    pending_jobs=pending_count,
                    processing_jobs=proc_set,
                    completed_jobs=comp_set,
                    failed_jobs=fail_set,
                    dlq_jobs=dlq_count,
                    retrying_jobs=retry_set,
                )
            )

        return stats_list

    async def list_jobs_by_status(
        self, status: JobStatus | None = None, limit: int = 50
    ) -> list[JobPayload]:
        """
        Lists stored jobs filtered by status.
        """
        client = await self.get_redis()
        if status:
            job_ids = list(await client.smembers(f"jobs:status:{status.value}"))[:limit]
        else:
            # Match all job keys
            keys = await client.keys("job:*")
            job_ids = [k.replace("job:", "") for k in keys][:limit]

        jobs: list[JobPayload] = []
        for j_id in job_ids:
            j = await self.get_job(j_id)
            if j:
                jobs.append(j)

        return sorted(jobs, key=lambda x: x.created_at, reverse=True)

    async def purge_queue(self, queue_type: QueueType | None = None, dlq: bool = False) -> int:
        """
        Purges jobs from a specific queue or Dead Letter Queue.
        """
        client = await self.get_redis()
        purged = 0

        if dlq:
            dlq_key = self._get_dlq_key()
            dlq_jobs = await client.smembers(dlq_key)
            for j_id in dlq_jobs:
                await client.delete(self._get_job_key(j_id))
                await client.srem(dlq_key, j_id)
                purged += 1
            return purged

        if queue_type:
            queue_key = self._get_queue_key(queue_type.value)
            while True:
                j_id = await client.lpop(queue_key)
                if not j_id:
                    break
                await client.delete(self._get_job_key(j_id))
                purged += 1

        return purged


# Global Singleton queue manager instance
queue_manager = RedisQueueManager()

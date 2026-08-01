import asyncio
import logging

from app.core.queue.redis_queue import RedisQueueManager, queue_manager

logger = logging.getLogger("reviewai.worker.retry_scheduler")


class RetrySchedulerWorker:
    """
    Background worker service that periodically scans Redis retry sorted set (queue:retry_zset)
    and re-enqueues ready jobs whose exponential backoff delay timestamp has elapsed.
    """

    def __init__(self, queue_mgr: RedisQueueManager | None = None, interval: float = 1.0):
        self.queue_mgr = queue_mgr or queue_manager
        self.interval = interval
        self._running = False

    async def start(self):
        """
        Starts the retry scheduler loop.
        """
        self._running = True
        logger.info("Starting Retry Scheduler Service (interval: %.1fs)...", self.interval)
        while self._running:
            try:
                count = await self.queue_mgr.process_due_retries()
                if count > 0:
                    logger.info("Retry Scheduler re-enqueued %d due retry job(s).", count)
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                logger.info("Retry Scheduler received cancellation signal.")
                self._running = False
                break
            except Exception as exc:
                logger.error("Error in Retry Scheduler loop: %s", exc, exc_info=True)
                await asyncio.sleep(2.0)

    def stop(self):
        """
        Stops the retry scheduler loop.
        """
        self._running = False

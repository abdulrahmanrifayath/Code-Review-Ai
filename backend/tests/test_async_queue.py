import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.queue.redis_queue import RedisQueueManager
from app.core.queue.schemas import JobPayload, JobStatus, QueueType
from app.workers.ai_analysis_worker import AIAnalysisWorker
from app.workers.notifications_worker import NotificationsWorker
from app.workers.report_generation_worker import ReportGenerationWorker
from app.workers.retry_scheduler import RetrySchedulerWorker
from app.workers.static_analysis_worker import StaticAnalysisWorker
from app.workers.webhook_worker import WebhookWorker


class MockAsyncRedis:
    def __init__(self):
        self.hashes = {}
        self.lists = {}
        self.sets = {}
        self.zsets = {}

    async def hset(self, name, mapping=None, **kwargs):
        if name not in self.hashes:
            self.hashes[name] = {}
        if mapping:
            self.hashes[name].update(mapping)

    async def hget(self, name, key):
        return self.hashes.get(name, {}).get(key)

    async def rpush(self, name, *values):
        if name not in self.lists:
            self.lists[name] = []
        self.lists[name].extend(values)

    async def lpop(self, name):
        if name in self.lists and self.lists[name]:
            return self.lists[name].pop(0)
        return None

    async def blpop(self, name, timeout=0):
        val = await self.lpop(name)
        if val:
            return (name, val)
        return None

    async def sadd(self, name, *values):
        if name not in self.sets:
            self.sets[name] = set()
        self.sets[name].update(values)

    async def srem(self, name, *values):
        if name in self.sets:
            self.sets[name].difference_update(values)

    async def scard(self, name):
        return len(self.sets.get(name, set()))

    async def smembers(self, name):
        return self.sets.get(name, set())

    async def llen(self, name):
        return len(self.lists.get(name, []))

    async def zadd(self, name, mapping):
        if name not in self.zsets:
            self.zsets[name] = {}
        self.zsets[name].update(mapping)

    async def zrangebyscore(self, name, min, max):
        if name not in self.zsets:
            return []
        res = []
        for item, score in self.zsets[name].items():
            if min <= score <= max:
                res.append(item)
        return res

    async def zrem(self, name, *values):
        count = 0
        if name in self.zsets:
            for val in values:
                if val in self.zsets[name]:
                    del self.zsets[name][val]
                    count += 1
        return count

    async def delete(self, name):
        self.hashes.pop(name, None)
        self.lists.pop(name, None)
        self.sets.pop(name, None)
        self.zsets.pop(name, None)

    async def keys(self, pattern):
        return list(self.hashes.keys())

    async def close(self):
        pass


class TestAsyncQueueSystem(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_redis = MockAsyncRedis()
        self.queue_mgr = RedisQueueManager()
        self.queue_mgr._redis_client = self.mock_redis

    async def test_enqueue_and_pop_job(self):
        """Test enqueuing and popping jobs for all 5 worker queue types."""
        for q_type in QueueType:
            job = await self.queue_mgr.enqueue_job(
                queue_type=q_type,
                action="test_action",
                payload={"key": f"value_{q_type.value}"},
            )
            self.assertIsNotNone(job.job_id)
            self.assertEqual(job.queue_type, q_type)
            self.assertEqual(job.status, JobStatus.QUEUED)

            popped = await self.queue_mgr.pop_job(q_type, timeout=0)
            self.assertIsNotNone(popped)
            self.assertEqual(popped.job_id, job.job_id)
            self.assertEqual(popped.payload["key"], f"value_{q_type.value}")

    async def test_exponential_backoff_and_dlq(self):
        """Test retry exponential backoff scheduling and Dead Letter Queue transition."""
        job = await self.queue_mgr.enqueue_job(
            queue_type=QueueType.STATIC_ANALYSIS,
            action="fail_task",
            payload={},
            max_retries=2,
        )

        # Retry #1
        is_retrying, updated_job = await self.queue_mgr.schedule_retry(
            job_id=job.job_id,
            error_message="Transient network error",
            base_delay_seconds=0.1,
        )
        self.assertTrue(is_retrying)
        self.assertEqual(updated_job.retry_count, 1)
        self.assertEqual(updated_job.status, JobStatus.RETRYING)

        # Sleep past the 0.1s backoff delay
        await asyncio.sleep(0.15)

        # Process due retries
        count = await self.queue_mgr.process_due_retries()
        self.assertEqual(count, 1)

        # Pop re-enqueued job
        popped = await self.queue_mgr.pop_job(QueueType.STATIC_ANALYSIS, timeout=0)
        self.assertEqual(popped.job_id, job.job_id)
        self.assertEqual(popped.status, JobStatus.QUEUED)

        # Retry #2
        is_retrying, _ = await self.queue_mgr.schedule_retry(
            job_id=job.job_id,
            error_message="Second transient failure",
            base_delay_seconds=0.1,
        )
        self.assertTrue(is_retrying)

        # Retry #3 (Exceeds max_retries=2 -> DLQ)
        is_retrying, dlq_job = await self.queue_mgr.schedule_retry(
            job_id=job.job_id,
            error_message="Fatal crash after retries",
        )
        self.assertFalse(is_retrying)
        self.assertEqual(dlq_job.status, JobStatus.FAILED)
        self.assertIn("Exhausted 2 retries", dlq_job.error_message)

        # Check DLQ stats
        stats = await self.queue_mgr.get_all_queue_stats()
        static_stats = next(s for s in stats if s.queue_name == QueueType.STATIC_ANALYSIS.value)
        self.assertEqual(static_stats.dlq_jobs, 1)

    async def test_manual_retry_failed_job(self):
        """Test manually re-enqueuing a job from DLQ."""
        job = await self.queue_mgr.enqueue_job(
            queue_type=QueueType.AI_ANALYSIS,
            action="llm_task",
            payload={},
            max_retries=1,
        )
        # Move to DLQ
        await self.queue_mgr.schedule_retry(job.job_id, "Err 1")
        await self.queue_mgr.schedule_retry(job.job_id, "Err 2")

        # Manually retry
        retried_job = await self.queue_mgr.retry_failed_job(job.job_id)
        self.assertIsNotNone(retried_job)
        self.assertEqual(retried_job.status, JobStatus.QUEUED)
        self.assertEqual(retried_job.retry_count, 0)

    async def test_workers_instantiation_and_process(self):
        """Test process execution for all 5 background worker implementations."""
        # 1. Report Generation Worker
        r_worker = ReportGenerationWorker(worker_id="test_report_w")
        r_res = await r_worker.process("generate_pdf", {"repo_full_name": "acme/repo", "format": "PDF"})
        self.assertEqual(r_res["format"], "PDF")
        self.assertIn("title", r_res)

        # 2. Notifications Worker
        n_worker = NotificationsWorker(worker_id="test_notif_w")
        n_res = await n_worker.process("send_comment", {"repo_full_name": "acme/repo", "pr_number": 5})
        self.assertEqual(n_res["status"], "delivered")

        # 3. Static Analysis Worker (mocked DB service)
        s_worker = StaticAnalysisWorker(worker_id="test_static_w")
        with patch("app.services.analysis_service.AnalysisService.run_static_analysis", new_callable=AsyncMock) as mock_sa:
            mock_sa.return_value = {"quality_score": 95}
            with patch("app.core.database.AsyncSessionLocal"):
                sa_res = await s_worker.process("analyze", {"repo_full_name": "acme/repo", "pr_number": 10})
                self.assertEqual(sa_res["quality_score"], 95)

        # 4. AI Analysis Worker (mocked DB service)
        ai_worker = AIAnalysisWorker(worker_id="test_ai_w", queue_mgr=self.queue_mgr)
        from app.services.ai_review_service import AIReviewService

        with patch.object(AIReviewService, "generate_ai_review", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = {"id": "123", "summary": "Great PR!"}
            with patch("app.core.database.AsyncSessionLocal"):
                with patch("app.workers.ai_analysis_worker.queue_manager", self.queue_mgr):
                    ai_res = await ai_worker.process("generate", {"repo_full_name": "acme/repo", "pr_number": 12})
                    self.assertEqual(ai_res["summary"], "Great PR!")

        # 5. Webhook Worker (mocked DB service)
        wh_worker = WebhookWorker(worker_id="test_wh_w", queue_mgr=self.queue_mgr)
        with patch("app.services.github_webhook.GitHubWebhookService.process_incoming_webhook", new_callable=AsyncMock) as mock_wh:
            mock_wh.return_value = ("PROCESSED", "Success", "opened")
            with patch("app.core.database.AsyncSessionLocal"):
                with patch("app.workers.webhook_worker.queue_manager", self.queue_mgr):
                    wh_res = await wh_worker.process("handle", {"delivery_id": "del_123", "event_type": "pull_request"})
                    self.assertEqual(wh_res["status"], "PROCESSED")


if __name__ == "__main__":
    unittest.main()

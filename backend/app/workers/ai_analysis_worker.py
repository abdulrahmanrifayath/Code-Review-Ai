import logging
from typing import Any, Dict, Optional

from app.core.database import AsyncSessionLocal
from app.core.queue.redis_queue import queue_manager
from app.core.queue.schemas import QueueType
from app.workers.base_worker import BaseWorker

logger = logging.getLogger("reviewai.worker.ai_analysis")


class AIAnalysisWorker(BaseWorker):
    """
    Background worker for asynchronous AI Analysis.
    Fetches PR diff context, invokes LLM / AI review engine,
    saves generated AI reviews, and enqueues notifications.
    """

    def __init__(self, worker_id: Optional[str] = None, queue_mgr: Optional[Any] = None):
        super().__init__(queue_type=QueueType.AI_ANALYSIS, worker_id=worker_id, queue_mgr=queue_mgr)

    async def process(self, action: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        repo_full_name = payload.get("repo_full_name")
        pr_number = payload.get("pr_number")

        logger.info("Executing AI Analysis for PR #%s in '%s' (action: %s)", pr_number, repo_full_name, action)

        async with AsyncSessionLocal() as db:
            from app.services.ai_review_service import AIReviewService
            service = AIReviewService(db)

            # Generate AI Code Review
            review_res = await service.generate_ai_review(
                user=payload.get("user"),
                repository_id=payload.get("repository_id"),
                pr_number=pr_number,
            )
            await db.commit()

            # Enqueue Notification job upon completion
            if review_res and "id" in review_res:
                await queue_manager.enqueue_job(
                    queue_type=QueueType.NOTIFICATIONS,
                    action="send_pr_review_notification",
                    payload={
                        "repo_full_name": repo_full_name,
                        "pr_number": pr_number,
                        "review_id": str(review_res["id"]),
                        "summary": review_res.get("summary", "AI Review completed."),
                    },
                )

        return review_res

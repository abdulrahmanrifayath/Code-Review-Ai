import logging
from typing import Any, Dict, Optional

from app.core.database import AsyncSessionLocal
from app.core.queue.redis_queue import queue_manager
from app.core.queue.schemas import QueueType
from app.workers.base_worker import BaseWorker

logger = logging.getLogger("reviewai.worker.webhook")


class WebhookWorker(BaseWorker):
    """
    Background worker for asynchronous Webhook Processing.
    Handles incoming GitHub webhooks, audit logging, PR record sync,
    and enqueues downstream AI analysis & static analysis jobs.
    """

    def __init__(self, worker_id: Optional[str] = None, queue_mgr: Optional[Any] = None):
        super().__init__(queue_type=QueueType.WEBHOOK_PROCESSING, worker_id=worker_id, queue_mgr=queue_mgr)

    async def process(self, action: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        delivery_id = payload.get("delivery_id", "unknown_delivery")
        event_type = payload.get("event_type", "unknown_event")
        payload_data = payload.get("payload_data", {})

        logger.info("Processing webhook delivery '%s' (event: %s, action: %s)", delivery_id, event_type, action)

        async with AsyncSessionLocal() as db:
            from app.services.github_webhook import GitHubWebhookService
            service = GitHubWebhookService(db)
            
            # Execute webhook business logic
            status_str, message, pr_action = await service.process_incoming_webhook(
                delivery_id=delivery_id,
                event_type=event_type,
                raw_payload_bytes=payload.get("raw_payload", b""),
                payload_json=payload_data,
                signature_header=payload.get("signature_header"),
            )
            await db.commit()

            # Enqueue downstream analysis jobs if pull request event is active
            if event_type == "pull_request" and pr_action in ("opened", "synchronize", "reopened", "review_requested"):
                pr_data = payload_data.get("pull_request", {})
                pr_number = pr_data.get("number")
                repo_full_name = payload_data.get("repository", {}).get("full_name")

                if pr_number and repo_full_name:
                    # 1. Enqueue Static Analysis Job
                    await queue_manager.enqueue_job(
                        queue_type=QueueType.STATIC_ANALYSIS,
                        action="run_static_analysis",
                        payload={
                            "repo_full_name": repo_full_name,
                            "pr_number": pr_number,
                            "head_sha": pr_data.get("head", {}).get("sha"),
                        },
                    )

                    # 2. Enqueue AI Analysis Job
                    await queue_manager.enqueue_job(
                        queue_type=QueueType.AI_ANALYSIS,
                        action="generate_ai_review",
                        payload={
                            "repo_full_name": repo_full_name,
                            "pr_number": pr_number,
                            "head_sha": pr_data.get("head", {}).get("sha"),
                        },
                    )

        return {
            "delivery_id": delivery_id,
            "status": status_str,
            "message": message,
            "pr_action": pr_action,
        }

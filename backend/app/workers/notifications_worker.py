import logging
from typing import Any

from app.core.database import AsyncSessionLocal
from app.core.queue.schemas import QueueType
from app.workers.base_worker import BaseWorker

logger = logging.getLogger("reviewai.worker.notifications")


class NotificationsWorker(BaseWorker):
    """
    Background worker for asynchronous Notifications dispatch.
    Invokes NotificationService to deliver alerts across all user-configured channels
    (GitHub comments, Email, Slack, Discord, and In-App notifications).
    Supported by Redis exponential backoff retries on delivery errors.
    """

    def __init__(self, worker_id: str | None = None, queue_mgr: Any | None = None):
        super().__init__(queue_type=QueueType.NOTIFICATIONS, worker_id=worker_id, queue_mgr=queue_mgr)

    async def process(self, action: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        user_id_str = payload.get("user_id")
        repo_full_name = payload.get("repo_full_name")
        pr_number = payload.get("pr_number")
        title = payload.get("title", f"Code Review Update for PR #{pr_number}" if pr_number else "Code Review AI Alert")
        summary = payload.get("summary", "Review complete.")
        link_url = payload.get("link_url", f"https://github.com/{repo_full_name}/pull/{pr_number}" if repo_full_name and pr_number else None)

        logger.info("Processing notification dispatch for PR #%s (action: %s)", pr_number, action)

        async with AsyncSessionLocal() as db:
            from app.services.notification_service import NotificationService
            service = NotificationService(db)

            # If user_id provided, parse UUID; otherwise fallback or query default user
            target_user_id = None
            if user_id_str:
                import uuid
                target_user_id = uuid.UUID(user_id_str) if isinstance(user_id_str, str) else user_id_str
            else:
                from sqlalchemy import select

                from app.models.user import User
                user_res = await db.execute(select(User).limit(1))
                first_user = user_res.scalars().first()
                if first_user:
                    target_user_id = first_user.id

            if not target_user_id:
                logger.warning("No target user found for notification dispatch.")
                return {"status": "skipped", "reason": "No user ID available"}

            notification_obj, statuses = await service.dispatch_notification(
                user_id=target_user_id,
                title=title,
                message=summary,
                notification_type=payload.get("notification_type", "review_completed"),
                link_url=link_url,
                payload=payload,
            )
            await db.commit()

            # Check if any remote channel failed with critical error
            failed_channels = [ch for ch, st in statuses.items() if st.startswith("failed")]
            if failed_channels:
                logger.warning("Notification delivery failed on channels: %s", failed_channels)
                # Raise error to trigger Redis worker exponential retry logic
                raise RuntimeError(f"Notification channel failure: {', '.join(failed_channels)}")

        return {
            "status": "completed",
            "repo_full_name": repo_full_name,
            "pr_number": pr_number,
            "channels": statuses,
        }

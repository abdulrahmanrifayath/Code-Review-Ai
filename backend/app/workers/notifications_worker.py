import logging
from typing import Any, Dict, Optional

from app.core.database import AsyncSessionLocal
from app.core.queue.schemas import QueueType
from app.workers.base_worker import BaseWorker

logger = logging.getLogger("reviewai.worker.notifications")


class NotificationsWorker(BaseWorker):
    """
    Background worker for asynchronous Notifications dispatch.
    Posts automated code review comments to GitHub PRs and dispatches alert webhooks.
    """

    def __init__(self, worker_id: Optional[str] = None, queue_mgr: Optional[Any] = None):
        super().__init__(queue_type=QueueType.NOTIFICATIONS, worker_id=worker_id, queue_mgr=queue_mgr)

    async def process(self, action: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        repo_full_name = payload.get("repo_full_name")
        pr_number = payload.get("pr_number")
        summary = payload.get("summary", "Review complete.")

        logger.info(
            "Dispatching notification for PR #%s in '%s' (action: %s)",
            pr_number, repo_full_name, action
        )

        async with AsyncSessionLocal() as db:
            access_token = payload.get("access_token")
            if access_token and repo_full_name and pr_number:
                from app.services.github_api import GitHubAPIService
                service = GitHubAPIService(access_token=access_token)
                parts = repo_full_name.split("/")
                if len(parts) == 2:
                    owner, repo = parts
                    comment_body = f"## 🤖 ReviewAI Analysis Result\n\n{summary}"
                    await service._execute_request_with_retry(
                        "POST", f"/repos/{owner}/{repo}/issues/{pr_number}/comments", json_data={"body": comment_body}
                    )
                    logger.info("Posted automated review comment to PR #%s", pr_number)

        return {
            "status": "delivered",
            "repo_full_name": repo_full_name,
            "pr_number": pr_number,
            "action": action,
        }

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import UnauthorizedError, ValidationError
from app.core.logging import logger
from app.models.pull_request import PullRequest
from app.models.repository import Repository
from app.models.review_job import ReviewJob
from app.models.webhook import WebhookEvent
from app.services.webhook_security import verify_github_signature


class GitHubWebhookService:
    """
    Service for processing incoming GitHub Webhooks, enforcing idempotency,
    storing audit events, updating PR database entities, and queuing AI ReviewJobs.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_incoming_webhook(
        self,
        delivery_id: str,
        event_type: str,
        raw_payload_bytes: bytes,
        payload_json: dict[str, Any],
        signature_header: str | None,
    ) -> tuple[str, str, str | None]:
        """
        Process incoming webhook.
        Returns: (status, message, action)
        """
        # 1. Idempotency Check
        stmt = select(WebhookEvent).where(WebhookEvent.delivery_id == delivery_id)
        res = await self.db.execute(stmt)
        existing_event = res.scalars().first()

        if existing_event:
            logger.info("Duplicate webhook delivery_id '%s' ignored.", delivery_id)
            return "DUPLICATE", "Duplicate webhook delivery ignored.", existing_event.action

        # 2. HMAC Signature Verification
        if not verify_github_signature(raw_payload_bytes, signature_header):
            raise UnauthorizedError("Invalid X-Hub-Signature-256 HMAC signature.")

        action = payload_json.get("action")
        repo_data = payload_json.get("repository", {})
        github_repo_id = repo_data.get("id")

        # Find matching repository in DB if exists
        repository: Repository | None = None
        if github_repo_id:
            repo_stmt = select(Repository).where(Repository.github_repo_id == github_repo_id)
            repo_res = await self.db.execute(repo_stmt)
            repository = repo_res.scalars().first()

        # 3. Create WebhookEvent audit record
        webhook_event = WebhookEvent(
            delivery_id=delivery_id,
            event_type=event_type,
            action=action,
            repository_id=repository.id if repository else None,
            payload=payload_json,
            status="RECEIVED",
        )
        self.db.add(webhook_event)
        await self.db.flush()

        try:
            # 4. Handle Event Types
            if event_type == "pull_request":
                await self._handle_pull_request_event(payload_json, repository, webhook_event)
            elif event_type == "push":
                await self._handle_push_event(payload_json, repository, webhook_event)
            elif event_type == "ping":
                webhook_event.status = "PROCESSED"
                logger.info("Received GitHub ping webhook for repo '%s'.", repo_data.get("full_name"))
            else:
                webhook_event.status = "IGNORED"

            await self.db.flush()
            return webhook_event.status, f"Successfully processed event '{event_type}'.", action

        except Exception as exc:
            webhook_event.status = "FAILED"
            webhook_event.error_message = str(exc)
            await self.db.flush()
            logger.error("Failed to process webhook '%s': %s", delivery_id, str(exc), exc_info=True)
            raise ValidationError(f"Error processing webhook: {exc!s}")

    async def _handle_pull_request_event(
        self, payload: dict[str, Any], repository: Repository | None, webhook_event: WebhookEvent
    ) -> None:
        """
        Handle pull_request webhook events (opened, synchronize, closed, reopened, review_requested).
        """
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})
        if not pr_data or not repository:
            webhook_event.status = "IGNORED"
            return

        pr_number = pr_data["number"]
        title = pr_data.get("title", "")
        body = pr_data.get("body", "")
        state = pr_data.get("state", "open")
        is_merged = pr_data.get("merged", False)
        head_branch = pr_data["head"]["ref"]
        base_branch = pr_data["base"]["ref"]
        head_sha = pr_data["head"]["sha"]
        author_login = pr_data["user"]["login"]
        html_url = pr_data.get("html_url")

        # Upsert PullRequest in DB
        pr_stmt = select(PullRequest).where(
            PullRequest.repository_id == repository.id, PullRequest.pr_number == pr_number
        )
        pr_res = await self.db.execute(pr_stmt)
        pr = pr_res.scalars().first()

        pr_state = "merged" if (action == "closed" and is_merged) else state

        if pr:
            pr.title = title
            pr.body = body
            pr.state = pr_state
            pr.head_branch = head_branch
            pr.base_branch = base_branch
            pr.head_sha = head_sha
            pr.author_login = author_login
            pr.html_url = html_url
            self.db.add(pr)
        else:
            pr = PullRequest(
                repository_id=repository.id,
                pr_number=pr_number,
                title=title,
                body=body,
                state=pr_state,
                head_branch=head_branch,
                base_branch=base_branch,
                head_sha=head_sha,
                author_login=author_login,
                html_url=html_url,
            )
            self.db.add(pr)

        await self.db.flush()

        # Queue AI ReviewJob for analysis-relevant actions
        if action in ("opened", "synchronize", "reopened", "review_requested"):
            job = ReviewJob(
                pull_request_id=pr.id,
                status="QUEUED",
                trigger_event=f"pr_{action}",
            )
            self.db.add(job)
            logger.info("Queued ReviewJob (id=%s) for PR #%s on %s", job.id, pr_number, repository.full_name)

        webhook_event.status = "PROCESSED"

    async def _handle_push_event(
        self, payload: dict[str, Any], repository: Repository | None, webhook_event: WebhookEvent
    ) -> None:
        """Handle push webhook events."""
        if not repository:
            webhook_event.status = "IGNORED"
            return

        ref = payload.get("ref", "")
        commits = payload.get("commits", [])
        logger.info("Processed push event on %s (%s, %d commits)", repository.full_name, ref, len(commits))
        webhook_event.status = "PROCESSED"

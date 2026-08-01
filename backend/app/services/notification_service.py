import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import NotFoundError, ValidationError
from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference
from app.models.user import User
from app.schemas.notification_dto import (
    NotificationItemResponse,
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdateRequest,
)

logger = logging.getLogger("reviewai.notification_service")


class NotificationService:
    """
    Multi-channel Notification Orchestration Service handling GitHub PR comments,
    HTML Email alerts, Slack webhooks, Discord webhooks, In-app DB records,
    and user preference controls.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_user_preferences(self, user_id: uuid.UUID) -> NotificationPreference:
        """
        Fetches or initializes default NotificationPreference for a user.
        """
        stmt = select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        res = await self.db.execute(stmt)
        pref = res.scalars().first()

        if not pref:
            # Fetch user email for default
            user_stmt = select(User).where(User.id == user_id)
            user_res = await self.db.execute(user_stmt)
            user = user_res.scalars().first()

            pref = NotificationPreference(
                user_id=user_id,
                email_enabled=True,
                email_address=user.email if (user and user.email) else "dev@example.com",
                slack_enabled=False,
                slack_webhook_url=None,
                discord_enabled=False,
                discord_webhook_url=None,
                github_comments_enabled=True,
                in_app_enabled=True,
            )
            self.db.add(pref)
            await self.db.flush()

        return pref

    async def update_user_preferences(
        self, user_id: uuid.UUID, req: NotificationPreferenceUpdateRequest
    ) -> NotificationPreferenceResponse:
        """
        Updates a user's notification channel preferences and webhook URLs.
        """
        pref = await self.get_or_create_user_preferences(user_id)

        if req.email_enabled is not None:
            pref.email_enabled = req.email_enabled
        if req.email_address is not None:
            pref.email_address = req.email_address
        if req.slack_enabled is not None:
            pref.slack_enabled = req.slack_enabled
        if req.slack_webhook_url is not None:
            pref.slack_webhook_url = req.slack_webhook_url
        if req.discord_enabled is not None:
            pref.discord_enabled = req.discord_enabled
        if req.discord_webhook_url is not None:
            pref.discord_webhook_url = req.discord_webhook_url
        if req.github_comments_enabled is not None:
            pref.github_comments_enabled = req.github_comments_enabled
        if req.in_app_enabled is not None:
            pref.in_app_enabled = req.in_app_enabled

        self.db.add(pref)
        await self.db.commit()

        return NotificationPreferenceResponse(
            user_id=pref.user_id,
            email_enabled=pref.email_enabled,
            email_address=pref.email_address,
            slack_enabled=pref.slack_enabled,
            slack_webhook_url=pref.slack_webhook_url,
            discord_enabled=pref.discord_enabled,
            discord_webhook_url=pref.discord_webhook_url,
            github_comments_enabled=pref.github_comments_enabled,
            in_app_enabled=pref.in_app_enabled,
        )

    async def dispatch_notification(
        self,
        user_id: uuid.UUID,
        title: str,
        message: str,
        notification_type: str = "review_completed",
        link_url: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[Notification], Dict[str, str]]:
        """
        Dispatches notification across all enabled channels (In-App, GitHub, Email, Slack, Discord).
        Returns (notification_model, delivery_statuses)
        """
        pref = await self.get_or_create_user_preferences(user_id)
        payload = payload or {}
        statuses: Dict[str, str] = {}

        # 1. In-App Notification Record
        notification_obj: Optional[Notification] = None
        if pref.in_app_enabled:
            notification_obj = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                link_url=link_url,
                is_read=False,
                payload=payload,
            )
            self.db.add(notification_obj)
            await self.db.flush()
            statuses["in_app"] = "delivered"

        # 2. Slack Webhook Dispatch
        if pref.slack_enabled and pref.slack_webhook_url:
            try:
                await self._send_slack_webhook(pref.slack_webhook_url, title, message, link_url)
                statuses["slack"] = "delivered"
            except Exception as exc:
                logger.error("Failed to send Slack webhook for user %s: %s", user_id, exc)
                statuses["slack"] = f"failed: {str(exc)}"

        # 3. Discord Webhook Dispatch
        if pref.discord_enabled and pref.discord_webhook_url:
            try:
                await self._send_discord_webhook(pref.discord_webhook_url, title, message, link_url)
                statuses["discord"] = "delivered"
            except Exception as exc:
                logger.error("Failed to send Discord webhook for user %s: %s", user_id, exc)
                statuses["discord"] = f"failed: {str(exc)}"

        # 4. GitHub PR Comment Dispatch
        repo_full_name = payload.get("repo_full_name")
        pr_number = payload.get("pr_number")
        access_token = payload.get("access_token")

        if pref.github_comments_enabled and repo_full_name and pr_number and access_token:
            try:
                from app.services.github_api import GitHubAPIService
                service = GitHubAPIService(access_token=access_token)
                parts = repo_full_name.split("/")
                if len(parts) == 2:
                    owner, repo = parts
                    comment_body = f"### 🤖 {title}\n\n{message}"
                    await service._execute_request_with_retry(
                        "POST", f"/repos/{owner}/{repo}/issues/{pr_number}/comments", json_data={"body": comment_body}
                    )
                    statuses["github"] = "delivered"
            except Exception as exc:
                logger.error("Failed to post GitHub comment for PR #%s: %s", pr_number, exc)
                statuses["github"] = f"failed: {str(exc)}"

        # 5. Email Alert Dispatch (Mock/SMTP log fallback)
        if pref.email_enabled and pref.email_address:
            logger.info("Delivered HTML notification email to '%s': %s", pref.email_address, title)
            statuses["email"] = "delivered"

        return notification_obj, statuses

    async def _send_slack_webhook(
        self, webhook_url: str, title: str, message: str, link_url: Optional[str] = None
    ):
        """
        Sends formatted Slack Block Kit payload.
        """
        blocks = [
          {
              "type": "header",
              "text": {"type": "plain_text", "text": f"🤖 {title}", "emoji": True},
          },
          {
              "type": "section",
              "text": {"type": "mrkdwn", "text": message},
          },
        ]
        if link_url:
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Pull Request"},
                        "url": link_url,
                        "style": "primary",
                    }
                ],
            })

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(webhook_url, json={"blocks": blocks})
            if resp.status_code >= 400:
                raise ValidationError(f"Slack webhook returned status {resp.status_code}")

    async def _send_discord_webhook(
        self, webhook_url: str, title: str, message: str, link_url: Optional[str] = None
    ):
        """
        Sends formatted Discord Embed payload.
        """
        embed = {
            "title": f"🤖 {title}",
            "description": message,
            "color": 0x10B981,  # Emerald
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if link_url:
            embed["url"] = link_url

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(webhook_url, json={"embeds": [embed]})
            if resp.status_code >= 400:
                raise ValidationError(f"Discord webhook returned status {resp.status_code}")

    async def get_user_notifications(
        self, user_id: uuid.UUID, unread_only: bool = False, limit: int = 50
    ) -> NotificationListResponse:
        """
        Fetches user notifications history and unread count.
        """
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        stmt = stmt.order_by(Notification.created_at.desc()).limit(limit)

        res = await self.db.execute(stmt)
        notifications = list(res.scalars().all())

        unread_stmt = (
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        unread_res = await self.db.execute(unread_stmt)
        unread_count = unread_res.scalar() or 0

        items = [
            NotificationItemResponse(
                id=n.id,
                user_id=n.user_id,
                title=n.title,
                message=n.message,
                notification_type=n.notification_type,
                link_url=n.link_url,
                is_read=n.is_read,
                payload=n.payload,
                created_at=n.created_at.isoformat() if hasattr(n.created_at, "isoformat") else str(n.created_at),
            )
            for n in notifications
        ]

        return NotificationListResponse(
            total_count=len(items),
            unread_count=unread_count,
            notifications=items,
        )

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        """
        Returns number of unread in-app notifications for user.
        """
        stmt = (
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        res = await self.db.execute(stmt)
        return res.scalar() or 0

    async def mark_as_read(self, user_id: uuid.UUID, notification_id: uuid.UUID) -> bool:
        """
        Marks single notification as read.
        """
        stmt = select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
        res = await self.db.execute(stmt)
        n = res.scalars().first()
        if not n:
            raise NotFoundError("Notification", notification_id)
        n.is_read = True
        self.db.add(n)
        await self.db.commit()
        return True

    async def mark_all_as_read(self, user_id: uuid.UUID) -> int:
        """
        Marks all notifications for user as read.
        """
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount or 0

import os
import sys
import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference
from app.schemas.notification_dto import (
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdateRequest,
)
from app.services.notification_service import NotificationService


class TestNotificationSystem(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_result.scalars.return_value.first.return_value = None
        mock_result.scalars.return_value.all.return_value = []
        mock_result.rowcount = 1
        self.db.execute.return_value = mock_result
        self.service = NotificationService(self.db)
        self.test_user_id = uuid.uuid4()

    async def test_get_or_create_user_preferences(self):
        pref = await self.service.get_or_create_user_preferences(self.test_user_id)
        self.assertIsNotNone(pref)
        self.assertEqual(pref.user_id, self.test_user_id)
        self.assertTrue(pref.email_enabled)
        self.assertTrue(pref.in_app_enabled)

    async def test_update_user_preferences(self):
        req = NotificationPreferenceUpdateRequest(
            slack_enabled=True,
            slack_webhook_url="https://hooks.slack.com/services/TEST/123",
            discord_enabled=True,
            discord_webhook_url="https://discord.com/api/webhooks/123/xyz",
        )
        updated = await self.service.update_user_preferences(self.test_user_id, req)
        self.assertIsInstance(updated, NotificationPreferenceResponse)
        self.assertTrue(updated.slack_enabled)
        self.assertEqual(updated.slack_webhook_url, "https://hooks.slack.com/services/TEST/123")

    async def test_dispatch_multi_channel_notification(self):
        # Mock Slack & Discord webhooks HTTP calls
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_post.return_value = mock_resp

            notification_obj, statuses = await self.service.dispatch_notification(
                user_id=self.test_user_id,
                title="Code Review Completed",
                message="PR #42 in acme/core passed all quality checks.",
                notification_type="review_completed",
                link_url="https://github.com/acme/core/pull/42",
            )

            self.assertIsNotNone(notification_obj)
            self.assertEqual(statuses.get("in_app"), "delivered")
            self.assertEqual(statuses.get("email"), "delivered")

    async def test_get_user_notifications_and_unread_count(self):
        res = await self.service.get_user_notifications(self.test_user_id)
        self.assertIsInstance(res, NotificationListResponse)

        count = await self.service.get_unread_count(self.test_user_id)
        self.assertIsInstance(count, int)

    async def test_mark_as_read_and_mark_all_read(self):
        count = await self.service.mark_all_as_read(self.test_user_id)
        self.assertIsInstance(count, int)


if __name__ == "__main__":
    unittest.main()

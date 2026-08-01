import uuid
from typing import Any

from pydantic import BaseModel, Field


class NotificationItemResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str
    notification_type: str  # e.g., "review_completed", "security_alert", "system"
    link_url: str | None = None
    is_read: bool
    payload: dict[str, Any] | None = None
    created_at: str


class NotificationListResponse(BaseModel):
    total_count: int
    unread_count: int
    notifications: list[NotificationItemResponse]


class UnreadCountResponse(BaseModel):
    unread_count: int


class NotificationPreferenceResponse(BaseModel):
    user_id: uuid.UUID
    email_enabled: bool
    email_address: str | None = None
    slack_enabled: bool
    slack_webhook_url: str | None = None
    discord_enabled: bool
    discord_webhook_url: str | None = None
    github_comments_enabled: bool
    in_app_enabled: bool


class NotificationPreferenceUpdateRequest(BaseModel):
    email_enabled: bool | None = None
    email_address: str | None = None
    slack_enabled: bool | None = None
    slack_webhook_url: str | None = None
    discord_enabled: bool | None = None
    discord_webhook_url: str | None = None
    github_comments_enabled: bool | None = None
    in_app_enabled: bool | None = None


class TestNotificationRequest(BaseModel):
    channel: str = Field("all", description="Target channel: all, slack, discord, email, github, in_app")
    title: str | None = "Test Notification from ReviewAI"
    message: str | None = "This is a test notification confirming your notification channel configuration is working correctly."

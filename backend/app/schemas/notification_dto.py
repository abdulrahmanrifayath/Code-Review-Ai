import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NotificationItemResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str
    notification_type: str  # e.g., "review_completed", "security_alert", "system"
    link_url: Optional[str] = None
    is_read: bool
    payload: Optional[Dict[str, Any]] = None
    created_at: str


class NotificationListResponse(BaseModel):
    total_count: int
    unread_count: int
    notifications: List[NotificationItemResponse]


class UnreadCountResponse(BaseModel):
    unread_count: int


class NotificationPreferenceResponse(BaseModel):
    user_id: uuid.UUID
    email_enabled: bool
    email_address: Optional[str] = None
    slack_enabled: bool
    slack_webhook_url: Optional[str] = None
    discord_enabled: bool
    discord_webhook_url: Optional[str] = None
    github_comments_enabled: bool
    in_app_enabled: bool


class NotificationPreferenceUpdateRequest(BaseModel):
    email_enabled: Optional[bool] = None
    email_address: Optional[str] = None
    slack_enabled: Optional[bool] = None
    slack_webhook_url: Optional[str] = None
    discord_enabled: Optional[bool] = None
    discord_webhook_url: Optional[str] = None
    github_comments_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None


class TestNotificationRequest(BaseModel):
    channel: str = Field("all", description="Target channel: all, slack, discord, email, github, in_app")
    title: Optional[str] = "Test Notification from ReviewAI"
    message: Optional[str] = "This is a test notification confirming your notification channel configuration is working correctly."

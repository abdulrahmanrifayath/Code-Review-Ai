import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.queue.redis_queue import queue_manager
from app.core.queue.schemas import QueueType
from app.models.user import User
from app.schemas.notification_dto import (
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdateRequest,
    TestNotificationRequest,
    UnreadCountResponse,
)
from app.services.auth import get_current_user
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=NotificationListResponse, status_code=status.HTTP_200_OK)
async def list_user_notifications(
    unread_only: bool = Query(False, description="Filter only unread notifications"),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves user notification history and unread count.
    """
    service = NotificationService(db)
    return await service.get_user_notifications(
        user_id=current_user.id, unread_only=unread_only, limit=limit
    )


@router.get("/unread-count", response_model=UnreadCountResponse, status_code=status.HTTP_200_OK)
async def get_unread_notification_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns unread in-app notification count for live navbar badge.
    """
    service = NotificationService(db)
    count = await service.get_unread_count(user_id=current_user.id)
    return UnreadCountResponse(unread_count=count)


@router.put("/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Marks a single notification as read.
    """
    service = NotificationService(db)
    success = await service.mark_as_read(user_id=current_user.id, notification_id=notification_id)
    return {"message": "Notification marked as read", "success": success}


@router.put("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Marks all notifications for the authenticated user as read.
    """
    service = NotificationService(db)
    count = await service.mark_all_as_read(user_id=current_user.id)
    return {"message": f"Marked {count} notification(s) as read", "count": count}


@router.get("/preferences", response_model=NotificationPreferenceResponse, status_code=status.HTTP_200_OK)
async def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves user notification preferences (GitHub, Email, Slack, Discord, In-App).
    """
    service = NotificationService(db)
    pref = await service.get_or_create_user_preferences(user_id=current_user.id)
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


@router.put("/preferences", response_model=NotificationPreferenceResponse, status_code=status.HTTP_200_OK)
async def update_notification_preferences(
    req: NotificationPreferenceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates user notification channel preferences and webhook URLs.
    """
    service = NotificationService(db)
    return await service.update_user_preferences(user_id=current_user.id, req=req)


@router.post("/test", status_code=status.HTTP_200_OK)
async def send_test_notification(
    req: TestNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Dispatches instant test notification across configured channels.
    """
    service = NotificationService(db)
    _, statuses = await service.dispatch_notification(
        user_id=current_user.id,
        title=req.title or "Test Notification",
        message=req.message or "Testing ReviewAI multi-channel notification engine.",
        notification_type="system_test",
        link_url="http://localhost:5173/analytics",
    )
    await db.commit()
    return {
        "message": "Test notification dispatched across configured channels.",
        "statuses": statuses,
    }


@router.post("/{notification_id}/retry", status_code=status.HTTP_202_ACCEPTED)
async def retry_failed_notification(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Re-enqueues a failed notification dispatch task to Redis Notifications Queue.
    """
    job = await queue_manager.enqueue_job(
        queue_type=QueueType.NOTIFICATIONS,
        action="retry_notification_dispatch",
        payload={
            "user_id": str(current_user.id),
            "notification_id": str(notification_id),
            "title": "Retried Code Review Notification",
        },
    )
    return {
        "message": f"Enqueued notification retry job '{job.job_id}' to Redis.",
        "job_id": job.job_id,
    }

import json

from fastapi import APIRouter, Depends, Header, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.webhook import WebhookResponse
from app.services.github_webhook import GitHubWebhookService

router = APIRouter()


@router.post("/github", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
async def receive_github_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_github_delivery: str = Header(..., alias="X-GitHub-Delivery"),
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256"),
):
    """
    GitHub Webhook receiver endpoint.
    Verifies HMAC-SHA256 signature, prevents duplicate delivery processing,
    stores event audit logs, updates PR database records, and queues AI ReviewJobs.
    """
    raw_body = await request.body()

    try:
        payload_json = json.loads(raw_body.decode("utf-8"))
    except Exception:
        payload_json = {}

    webhook_service = GitHubWebhookService(db)

    status_str, message, action = await webhook_service.process_incoming_webhook(
        delivery_id=x_github_delivery,
        event_type=x_github_event,
        raw_payload_bytes=raw_body,
        payload_json=payload_json,
        signature_header=x_hub_signature_256,
    )

    status_code = status.HTTP_200_OK if status_str in ("PROCESSED", "DUPLICATE", "IGNORED") else status.HTTP_202_ACCEPTED

    return JSONResponse(
        status_code=status_code,
        content={
            "status": status_str,
            "message": message,
            "delivery_id": x_github_delivery,
            "event_type": x_github_event,
            "action": action,
        },
    )

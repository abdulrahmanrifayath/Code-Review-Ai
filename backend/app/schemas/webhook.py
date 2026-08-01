import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WebhookResponse(BaseModel):
    status: str
    message: str
    delivery_id: str
    event_type: str
    action: str | None = None


class WebhookEventItem(BaseModel):
    id: uuid.UUID
    delivery_id: str
    event_type: str
    action: str | None = None
    status: str
    error_message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

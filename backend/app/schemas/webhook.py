import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class WebhookResponse(BaseModel):
    status: str
    message: str
    delivery_id: str
    event_type: str
    action: Optional[str] = None


class WebhookEventItem(BaseModel):
    id: uuid.UUID
    delivery_id: str
    event_type: str
    action: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

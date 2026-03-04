"""Notification DTOs."""

from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    body: str
    notification_type: str
    resource_type: str | None
    resource_id: str | None
    is_read: bool
    is_pushed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationCreate(BaseModel):
    title: str
    body: str
    notification_type: str
    resource_type: str | None = None
    resource_id: str | None = None

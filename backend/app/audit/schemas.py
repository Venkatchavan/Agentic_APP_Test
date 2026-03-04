"""Audit DTOs."""

from datetime import datetime
from pydantic import BaseModel


class AuditEventResponse(BaseModel):
    id: str
    user_id: str | None
    event_type: str
    resource_type: str | None
    resource_id: str | None
    detail: str | None
    ip_address: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditEventCreate(BaseModel):
    event_type: str
    resource_type: str | None = None
    resource_id: str | None = None
    detail: str | None = None

"""
Account-linking Pydantic schemas.
"""

from datetime import datetime
from pydantic import BaseModel


class LinkedAccountResponse(BaseModel):
    id: str
    provider: str
    provider_email: str
    is_active: bool
    scopes: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LinkAccountRequest(BaseModel):
    provider: str  # gmail | outlook | google_calendar | microsoft_calendar
    authorization_code: str
    redirect_uri: str | None = None


class UnlinkAccountRequest(BaseModel):
    account_id: str

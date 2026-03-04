"""
Draft Pydantic schemas.
"""

from datetime import datetime
from pydantic import BaseModel


class DraftReplyResponse(BaseModel):
    id: str
    draft_type: str
    to_addresses_json: str
    subject: str
    body_html: str
    body_text: str
    confidence: float
    is_ai_generated: bool
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GenerateDraftRequest(BaseModel):
    email_id: str | None = None
    meeting_id: str | None = None
    draft_type: str  # email_reply | meeting_followup
    additional_instructions: str = ""


class EditDraftRequest(BaseModel):
    subject: str | None = None
    body_html: str | None = None
    body_text: str | None = None
    to_addresses: list[str] | None = None

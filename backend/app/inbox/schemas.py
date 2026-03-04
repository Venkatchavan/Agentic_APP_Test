"""
Inbox Pydantic schemas — request / response DTOs.
"""

from datetime import datetime
from pydantic import BaseModel


class IngestedEmailResponse(BaseModel):
    id: str
    provider: str
    subject: str
    sender: str
    received_at: datetime
    processed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ExtractedActionResponse(BaseModel):
    id: str
    email_id: str
    action_type: str
    title: str
    description: str
    due_date: datetime | None
    owner: str | None
    confidence: float
    source_span: str
    ambiguity_flags: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class IngestEmailsRequest(BaseModel):
    linked_account_id: str
    max_emails: int = 20


class ProcessEmailRequest(BaseModel):
    email_id: str


class EmailDetailResponse(BaseModel):
    email: IngestedEmailResponse
    actions: list[ExtractedActionResponse]

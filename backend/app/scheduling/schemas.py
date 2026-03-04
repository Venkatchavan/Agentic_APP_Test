"""
Scheduling Pydantic schemas.
"""

from datetime import datetime
from pydantic import BaseModel


class ScheduleProposalResponse(BaseModel):
    id: str
    source_type: str
    title: str
    description: str
    proposed_start: datetime
    proposed_end: datetime
    duration_minutes: int
    attendees_json: str
    calendar_provider: str
    confidence: float
    conflict_detected: bool
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateProposalRequest(BaseModel):
    title: str
    description: str = ""
    proposed_start: datetime
    proposed_end: datetime
    duration_minutes: int = 30
    attendees: list[str] = []
    calendar_provider: str = "google_calendar"
    linked_account_id: str | None = None
    source_type: str = "manual"
    source_id: str | None = None


class FreeSlotResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_minutes: int


class FreeSlotsRequest(BaseModel):
    linked_account_id: str
    start: datetime
    end: datetime
    duration_minutes: int = 30

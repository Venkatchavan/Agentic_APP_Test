"""
Meetings Pydantic schemas.
"""

from datetime import datetime
from pydantic import BaseModel


class TranscriptImportRequest(BaseModel):
    title: str = "Untitled Meeting"
    source_type: str  # audio_upload | transcript_paste | transcript_file
    transcript_text: str | None = None
    meeting_date: datetime | None = None
    participants: list[str] = []


class TranscriptResponse(BaseModel):
    id: str
    title: str
    source_type: str
    duration_seconds: int | None
    meeting_date: datetime | None
    processed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MeetingSummaryResponse(BaseModel):
    id: str
    transcript_id: str
    summary_text: str
    key_points_json: str
    confidence: float
    created_at: datetime

    model_config = {"from_attributes": True}


class DecisionResponse(BaseModel):
    id: str
    decision_text: str
    decided_by: str | None
    confidence: float
    source_span: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ActionItemResponse(BaseModel):
    id: str
    title: str
    description: str
    owner: str | None
    due_date: datetime | None
    confidence: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MeetingDetailResponse(BaseModel):
    transcript: TranscriptResponse
    summary: MeetingSummaryResponse | None
    decisions: list[DecisionResponse]
    action_items: list[ActionItemResponse]

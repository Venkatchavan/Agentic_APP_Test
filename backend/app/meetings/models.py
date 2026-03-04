"""
Meetings DB models — transcripts, summaries, decisions, action items.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MeetingTranscript(Base):
    """Imported meeting audio/transcript record."""

    __tablename__ = "meeting_transcripts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(500), default="Untitled Meeting")
    source_type: Mapped[str] = mapped_column(
        String(30)  # audio_upload | transcript_paste | transcript_file
    )
    artifact_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    transcript_text: Mapped[str] = mapped_column(Text, default="")
    duration_seconds: Mapped[int | None] = mapped_column(nullable=True)
    meeting_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    participants_json: Mapped[str] = mapped_column(Text, default="[]")
    processed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class MeetingSummary(Base):
    """AI-generated meeting summary."""

    __tablename__ = "meeting_summaries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    transcript_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meeting_transcripts.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    summary_text: Mapped[str] = mapped_column(Text, default="")
    key_points_json: Mapped[str] = mapped_column(Text, default="[]")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class MeetingDecision(Base):
    """Extracted decision from a meeting."""

    __tablename__ = "meeting_decisions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    summary_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meeting_summaries.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    decision_text: Mapped[str] = mapped_column(Text)
    decided_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source_span: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class MeetingActionItem(Base):
    """Extracted action item / task from a meeting."""

    __tablename__ = "meeting_action_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    summary_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("meeting_summaries.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source_span: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(
        String(30), default="proposed"  # proposed | approved | rejected | executed
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

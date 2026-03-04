"""
Scheduling DB models — proposed schedule slots.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ScheduleProposal(Base):
    """A proposed meeting/event time slot — requires approval to create."""

    __tablename__ = "schedule_proposals"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    source_type: Mapped[str] = mapped_column(
        String(30)  # email_action | meeting_action | manual
    )
    source_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    proposed_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    proposed_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[int] = mapped_column(default=30)
    attendees_json: Mapped[str] = mapped_column(Text, default="[]")
    calendar_provider: Mapped[str] = mapped_column(
        String(50), default="google_calendar"
    )
    linked_account_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    conflict_detected: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(
        String(30), default="proposed"  # proposed | approved | rejected | created
    )
    provider_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

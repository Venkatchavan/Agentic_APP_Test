"""
Draft DB models — AI-generated reply drafts.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DraftReply(Base):
    """AI-generated email reply draft — requires approval before sending."""

    __tablename__ = "draft_replies"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    email_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("ingested_emails.id"), nullable=True
    )
    meeting_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("meeting_transcripts.id"), nullable=True
    )
    draft_type: Mapped[str] = mapped_column(
        String(30)  # email_reply | meeting_followup
    )
    to_addresses_json: Mapped[str] = mapped_column(Text, default="[]")
    subject: Mapped[str] = mapped_column(Text, default="")
    body_html: Mapped[str] = mapped_column(Text, default="")
    body_text: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    is_ai_generated: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(
        String(30), default="draft"  # draft | approved | sent | rejected
    )
    provider_draft_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

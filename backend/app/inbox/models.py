"""
Inbox DB models — ingested emails and extracted actions.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IngestedEmail(Base):
    """Raw email record after ingestion and sanitisation."""

    __tablename__ = "ingested_emails"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    linked_account_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("linked_accounts.id"), index=True
    )
    provider: Mapped[str] = mapped_column(String(50))
    provider_message_id: Mapped[str] = mapped_column(String(255), index=True)
    thread_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str] = mapped_column(Text, default="")
    sender: Mapped[str] = mapped_column(String(255))
    recipients_json: Mapped[str] = mapped_column(Text, default="[]")
    body_sanitized: Mapped[str] = mapped_column(Text, default="")
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    processed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class ExtractedEmailAction(Base):
    """AI-extracted action from an email."""

    __tablename__ = "extracted_email_actions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("ingested_emails.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    action_type: Mapped[str] = mapped_column(
        String(50)  # task | approval | commitment | schedule_intent | followup
    )
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source_span: Mapped[str] = mapped_column(Text, default="")
    ambiguity_flags: Mapped[str] = mapped_column(Text, default="[]")
    status: Mapped[str] = mapped_column(
        String(30), default="proposed"  # proposed | approved | rejected | executed
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

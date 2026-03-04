"""
Approvals DB models — the approval gate for all side-effecting actions.
Nothing external happens without explicit user approval through this model.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ApprovalRequest(Base):
    """
    Central approval record. Every external side effect (send email,
    create calendar event, etc.) must have an approved ApprovalRequest.
    """

    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    action_type: Mapped[str] = mapped_column(
        String(50)
        # send_email | create_calendar_event | create_task | send_followup
    )
    target_resource_type: Mapped[str] = mapped_column(
        String(50)  # draft_reply | schedule_proposal | email_action | meeting_action
    )
    target_resource_id: Mapped[str] = mapped_column(String(36), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    preview_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(
        String(30), default="pending"
        # pending | approved | rejected | executed | failed
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(100), unique=True, index=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rejected_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    execution_result: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

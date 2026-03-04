"""Audit event ORM model — immutable append-only log."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditEvent(Base):
    """
    Every significant action is logged here. Rows are never updated or
    deleted — this is an append-only audit trail.
    """

    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True,
    )
    # e.g. "email.ingested", "action.extracted", "draft.generated",
    #      "approval.requested", "approval.approved", "approval.rejected",
    #      "execution.success", "execution.failed", "auth.login"

    resource_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True,
    )

    def __repr__(self) -> str:
        return f"<AuditEvent {self.event_type} user={self.user_id}>"

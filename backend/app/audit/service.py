"""Audit service — append-only event logger."""

from __future__ import annotations

import structlog
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.models import AuditEvent

logger = structlog.get_logger()


async def log_event(
    db: AsyncSession,
    *,
    user_id: str | None,
    event_type: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    detail: str | None = None,
    ip_address: str | None = None,
) -> AuditEvent:
    """Create an immutable audit event."""
    event = AuditEvent(
        user_id=user_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail,
        ip_address=ip_address,
    )
    db.add(event)
    await db.flush()
    logger.info(
        "audit.logged",
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    return event


async def list_events(
    db: AsyncSession,
    user_id: str,
    *,
    event_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AuditEvent]:
    """List audit events for a user with optional type filter."""
    stmt = (
        select(AuditEvent)
        .where(AuditEvent.user_id == user_id)
        .order_by(desc(AuditEvent.created_at))
    )
    if event_type:
        stmt = stmt.where(AuditEvent.event_type == event_type)
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_event(db: AsyncSession, event_id: str) -> AuditEvent | None:
    """Get a single audit event by ID."""
    result = await db.execute(
        select(AuditEvent).where(AuditEvent.id == event_id)
    )
    return result.scalar_one_or_none()

"""Notification service — create, list, mark read."""

from __future__ import annotations

import structlog
from sqlalchemy import select, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.models import Notification

logger = structlog.get_logger()


async def create_notification(
    db: AsyncSession,
    *,
    user_id: str,
    title: str,
    body: str,
    notification_type: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
) -> Notification:
    """Create a new notification for a user."""
    notif = Notification(
        user_id=user_id,
        title=title,
        body=body,
        notification_type=notification_type,
        resource_type=resource_type,
        resource_id=resource_id,
    )
    db.add(notif)
    await db.flush()
    logger.info("notification.created", user_id=user_id, type=notification_type)
    return notif


async def list_notifications(
    db: AsyncSession,
    user_id: str,
    *,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[Notification]:
    """List notifications for a user, newest first."""
    stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(desc(Notification.created_at))
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)  # noqa: E712
    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def mark_read(
    db: AsyncSession, user_id: str, notification_id: str,
) -> bool:
    """Mark a single notification as read."""
    stmt = (
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user_id)
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    return result.rowcount > 0


async def mark_all_read(db: AsyncSession, user_id: str) -> int:
    """Mark all notifications as read for user. Returns count."""
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa
        .values(is_read=True)
    )
    result = await db.execute(stmt)
    return result.rowcount


async def unread_count(db: AsyncSession, user_id: str) -> int:
    """Get unread notification count."""
    from sqlalchemy import func
    stmt = (
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa
    )
    result = await db.execute(stmt)
    return result.scalar() or 0

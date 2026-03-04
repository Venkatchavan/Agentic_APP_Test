"""Notification REST endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.common.dependencies import CurrentUser, DbSession
from app.notifications import service
from app.notifications.schemas import NotificationResponse

router = APIRouter()


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    user_id: CurrentUser,
    db: DbSession,
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List notifications for the current user."""
    return await service.list_notifications(
        db, user_id, unread_only=unread_only, limit=limit, offset=offset,
    )


@router.get("/unread-count")
async def unread_count(user_id: CurrentUser, db: DbSession):
    """Get count of unread notifications."""
    count = await service.unread_count(db, user_id)
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    user_id: CurrentUser,
    db: DbSession,
):
    """Mark a notification as read."""
    ok = await service.mark_read(db, user_id, notification_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Notification not found")
    await db.commit()
    return {"status": "read"}


@router.post("/read-all")
async def mark_all_read(user_id: CurrentUser, db: DbSession):
    """Mark all notifications as read."""
    count = await service.mark_all_read(db, user_id)
    await db.commit()
    return {"marked_read": count}

"""Audit REST endpoints — read-only access to the audit trail."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.common.dependencies import CurrentUser, DbSession
from app.audit import service
from app.audit.schemas import AuditEventResponse

router = APIRouter()


@router.get("/events", response_model=list[AuditEventResponse])
async def list_audit_events(
    user_id: CurrentUser,
    db: DbSession,
    event_type: str | None = Query(None, description="Filter by event type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List audit events for the current user."""
    events = await service.list_events(
        db, user_id, event_type=event_type, limit=limit, offset=offset,
    )
    return events


@router.get("/events/{event_id}", response_model=AuditEventResponse)
async def get_audit_event(
    event_id: str,
    user_id: CurrentUser,
    db: DbSession,
):
    """Get a single audit event."""
    event = await service.get_event(db, event_id)
    if not event or event.user_id != user_id:
        raise HTTPException(status_code=404, detail="Audit event not found")
    return event

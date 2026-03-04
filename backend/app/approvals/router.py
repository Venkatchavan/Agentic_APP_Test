"""
Approvals REST endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.approvals import schemas, service
from app.common.dependencies import CurrentUser, DbSession, Pagination
from app.common.exceptions import AppError

router = APIRouter()


@router.get("/pending", response_model=list[schemas.ApprovalRequestResponse])
async def list_pending(user_id: CurrentUser, db: DbSession, page: Pagination):
    """List pending approval requests."""
    return await service.list_pending(db, user_id, page.skip, page.limit)


@router.get("/", response_model=list[schemas.ApprovalRequestResponse])
async def list_all(user_id: CurrentUser, db: DbSession, page: Pagination):
    """List all approval requests."""
    return await service.list_all(db, user_id, page.skip, page.limit)


@router.post("/", response_model=schemas.ApprovalRequestResponse, status_code=201)
async def create_approval(
    req: schemas.CreateApprovalRequest, user_id: CurrentUser, db: DbSession
):
    """Create a new approval request."""
    try:
        return await service.create_approval(
            db=db, user_id=user_id, **req.model_dump()
        )
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post("/{approval_id}/decide", response_model=schemas.ApprovalRequestResponse)
async def decide(
    approval_id: str,
    req: schemas.ApprovalDecision,
    user_id: CurrentUser,
    db: DbSession,
):
    """Approve or reject a pending request — the critical human-in-the-loop gate."""
    try:
        return await service.decide(db, user_id, approval_id, req.decision)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})

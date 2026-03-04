"""Execution router — trigger execution of approved actions."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.dependencies import CurrentUser, DbSession
from app.approvals.models import ApprovalRequest
from app.execution.service import execute_approved_action

router = APIRouter()


@router.post("/{approval_id}")
async def execute_action(
    approval_id: str,
    user_id: CurrentUser,
    db: DbSession,
):
    """Execute an approved action by its approval ID."""
    stmt = select(ApprovalRequest).where(
        ApprovalRequest.id == approval_id,
        ApprovalRequest.user_id == user_id,
    )
    result = await db.execute(stmt)
    approval = result.scalar_one_or_none()

    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.status != "approved":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute: status is '{approval.status}'",
        )

    outcome = await execute_approved_action(db, approval)
    await db.commit()
    return {"status": "executed", "result": outcome}

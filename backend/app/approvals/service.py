"""
Approval service — the critical gate between proposals and execution.
No external side effect may proceed without an approved record here.
"""

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.approvals.models import ApprovalRequest
from app.common.exceptions import (
    ApprovalRequiredError,
    ConflictError,
    NotFoundError,
    ValidationError,
)

logger = structlog.get_logger()

VALID_ACTIONS = {
    "send_email",
    "create_calendar_event",
    "create_task",
    "send_followup",
}
VALID_DECISIONS = {"approve", "reject"}


async def create_approval(
    db: AsyncSession,
    user_id: str,
    action_type: str,
    target_resource_type: str,
    target_resource_id: str,
    description: str = "",
    preview_json: str = "{}",
) -> ApprovalRequest:
    """Create a pending approval request."""
    if action_type not in VALID_ACTIONS:
        raise ValidationError(f"Invalid action_type: {action_type}")

    idempotency_key = f"{user_id}:{action_type}:{target_resource_id}"

    # Check for existing
    existing = await db.execute(
        select(ApprovalRequest).where(
            ApprovalRequest.idempotency_key == idempotency_key,
            ApprovalRequest.status.in_(["pending", "approved"]),
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Approval already exists for this action")

    approval = ApprovalRequest(
        user_id=user_id,
        action_type=action_type,
        target_resource_type=target_resource_type,
        target_resource_id=target_resource_id,
        description=description,
        preview_json=preview_json,
        idempotency_key=idempotency_key,
    )
    db.add(approval)
    await db.flush()
    logger.info("approval.created", approval_id=approval.id, action=action_type)
    return approval


async def decide(
    db: AsyncSession, user_id: str, approval_id: str, decision: str
) -> ApprovalRequest:
    """Approve or reject a pending request."""
    if decision not in VALID_DECISIONS:
        raise ValidationError(f"Decision must be 'approve' or 'reject'")

    approval = await _get_approval(db, user_id, approval_id)
    if approval.status != "pending":
        raise ConflictError(f"Approval is already '{approval.status}'")

    now = datetime.now(timezone.utc)
    if decision == "approve":
        approval.status = "approved"
        approval.approved_at = now
        logger.info("approval.approved", approval_id=approval_id)
    else:
        approval.status = "rejected"
        approval.rejected_at = now
        logger.info("approval.rejected", approval_id=approval_id)

    await db.flush()
    return approval


async def mark_executed(
    db: AsyncSession, approval_id: str, result: str
) -> ApprovalRequest:
    """Mark an approved request as executed."""
    result_obj = await db.execute(
        select(ApprovalRequest).where(ApprovalRequest.id == approval_id)
    )
    approval = result_obj.scalar_one_or_none()
    if not approval:
        raise NotFoundError("ApprovalRequest", approval_id)
    if approval.status != "approved":
        raise ApprovalRequiredError(approval_id)

    approval.status = "executed"
    approval.executed_at = datetime.now(timezone.utc)
    approval.execution_result = result
    await db.flush()
    return approval


async def list_pending(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 50
) -> list[ApprovalRequest]:
    result = await db.execute(
        select(ApprovalRequest)
        .where(ApprovalRequest.user_id == user_id, ApprovalRequest.status == "pending")
        .order_by(ApprovalRequest.created_at.desc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def list_all(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 50
) -> list[ApprovalRequest]:
    result = await db.execute(
        select(ApprovalRequest)
        .where(ApprovalRequest.user_id == user_id)
        .order_by(ApprovalRequest.created_at.desc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def _get_approval(
    db: AsyncSession, user_id: str, approval_id: str
) -> ApprovalRequest:
    result = await db.execute(
        select(ApprovalRequest).where(
            ApprovalRequest.id == approval_id,
            ApprovalRequest.user_id == user_id,
        )
    )
    a = result.scalar_one_or_none()
    if not a:
        raise NotFoundError("ApprovalRequest", approval_id)
    return a

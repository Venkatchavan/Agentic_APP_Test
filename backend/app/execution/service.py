"""
Execution service — the ONLY layer that performs external side effects.
Every call here MUST verify approval status first.
No direct execution without a matching approved ApprovalRequest.
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.approvals.service import mark_executed
from app.approvals.models import ApprovalRequest
from app.common.exceptions import ApprovalRequiredError, ProviderError

logger = structlog.get_logger()


async def execute_approved_action(
    db: AsyncSession,
    approval: ApprovalRequest,
) -> str:
    """
    Execute an approved action. Routes to the correct provider operation.
    CRITICAL: Only proceeds if approval.status == 'approved'.
    """
    if approval.status != "approved":
        raise ApprovalRequiredError(approval.id)

    logger.info(
        "execution.starting",
        approval_id=approval.id,
        action=approval.action_type,
        target=approval.target_resource_id,
    )

    try:
        result = await _dispatch(approval)
        await mark_executed(db, approval.id, result)
        logger.info("execution.success", approval_id=approval.id, result=result)
        return result
    except Exception as exc:
        approval.status = "failed"
        approval.execution_result = str(exc)[:2000]
        await db.flush()
        logger.error("execution.failed", approval_id=approval.id, error=str(exc))
        raise ProviderError("execution", str(exc))


async def _dispatch(approval: ApprovalRequest) -> str:
    """Route execution to the correct handler based on action_type."""
    action = approval.action_type

    if action == "send_email":
        return await _execute_send_email(approval)
    elif action == "create_calendar_event":
        return await _execute_create_event(approval)
    elif action == "send_followup":
        return await _execute_send_followup(approval)
    elif action == "create_task":
        return await _execute_create_task(approval)
    else:
        raise ProviderError("execution", f"Unknown action type: {action}")


async def _execute_send_email(approval: ApprovalRequest) -> str:
    """
    Send a draft email via the appropriate provider.
    In production, this loads the draft, gets the provider adapter,
    and calls send_draft with the stored access token.
    """
    # TODO: Load draft by target_resource_id
    # TODO: Get linked account and provider adapter
    # TODO: Call adapter.send_draft(token, provider_draft_id)
    logger.info("execution.send_email.stub", target=approval.target_resource_id)
    return f"email_sent:{approval.target_resource_id}"


async def _execute_create_event(approval: ApprovalRequest) -> str:
    """
    Create a calendar event via the appropriate provider.
    """
    # TODO: Load proposal by target_resource_id
    # TODO: Get calendar provider adapter
    # TODO: Call adapter.create_event(token, event)
    logger.info("execution.create_event.stub", target=approval.target_resource_id)
    return f"event_created:{approval.target_resource_id}"


async def _execute_send_followup(approval: ApprovalRequest) -> str:
    """Send a meeting follow-up draft."""
    logger.info("execution.send_followup.stub", target=approval.target_resource_id)
    return f"followup_sent:{approval.target_resource_id}"


async def _execute_create_task(approval: ApprovalRequest) -> str:
    """Create a task in an external system."""
    logger.info("execution.create_task.stub", target=approval.target_resource_id)
    return f"task_created:{approval.target_resource_id}"

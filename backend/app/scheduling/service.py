"""
Scheduling service — proposals and slot management.
"""

import json
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.scheduling.models import ScheduleProposal
from app.common.exceptions import NotFoundError

logger = structlog.get_logger()


async def create_proposal(
    db: AsyncSession, user_id: str, **kwargs
) -> ScheduleProposal:
    """Create a schedule proposal — NOT yet created in calendar."""
    attendees = kwargs.pop("attendees", [])
    proposal = ScheduleProposal(
        user_id=user_id,
        attendees_json=json.dumps(attendees),
        **kwargs,
    )
    db.add(proposal)
    await db.flush()
    logger.info("scheduling.proposal_created", proposal_id=proposal.id)
    return proposal


async def list_proposals(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 50
) -> list[ScheduleProposal]:
    result = await db.execute(
        select(ScheduleProposal)
        .where(ScheduleProposal.user_id == user_id)
        .order_by(ScheduleProposal.proposed_start.asc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_proposal(
    db: AsyncSession, user_id: str, proposal_id: str
) -> ScheduleProposal:
    result = await db.execute(
        select(ScheduleProposal).where(
            ScheduleProposal.id == proposal_id,
            ScheduleProposal.user_id == user_id,
        )
    )
    p = result.scalar_one_or_none()
    if not p:
        raise NotFoundError("ScheduleProposal", proposal_id)
    return p

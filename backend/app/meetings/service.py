"""
Meeting service — import, list, and manage meetings.
"""

import json
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.meetings.models import (
    MeetingActionItem,
    MeetingDecision,
    MeetingSummary,
    MeetingTranscript,
)
from app.common.exceptions import NotFoundError

logger = structlog.get_logger()


async def import_transcript(
    db: AsyncSession,
    user_id: str,
    title: str,
    source_type: str,
    transcript_text: str,
    meeting_date=None,
    participants: list[str] | None = None,
) -> MeetingTranscript:
    """Import a meeting transcript."""
    record = MeetingTranscript(
        user_id=user_id,
        title=title,
        source_type=source_type,
        transcript_text=transcript_text,
        meeting_date=meeting_date,
        participants_json=json.dumps(participants or []),
    )
    db.add(record)
    await db.flush()
    logger.info("meetings.imported", transcript_id=record.id, user_id=user_id)
    return record


async def list_transcripts(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 50
) -> list[MeetingTranscript]:
    result = await db.execute(
        select(MeetingTranscript)
        .where(MeetingTranscript.user_id == user_id)
        .order_by(MeetingTranscript.created_at.desc())
        .offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def get_transcript(
    db: AsyncSession, user_id: str, transcript_id: str
) -> MeetingTranscript:
    result = await db.execute(
        select(MeetingTranscript).where(
            MeetingTranscript.id == transcript_id,
            MeetingTranscript.user_id == user_id,
        )
    )
    t = result.scalar_one_or_none()
    if not t:
        raise NotFoundError("MeetingTranscript", transcript_id)
    return t


async def save_summary(
    db: AsyncSession,
    summary: MeetingSummary,
    decisions: list[MeetingDecision],
    actions: list[MeetingActionItem],
) -> None:
    db.add(summary)
    for d in decisions:
        d.summary_id = summary.id
        db.add(d)
    for a in actions:
        a.summary_id = summary.id
        db.add(a)
    await db.flush()


async def get_summary(
    db: AsyncSession, transcript_id: str
) -> MeetingSummary | None:
    result = await db.execute(
        select(MeetingSummary).where(MeetingSummary.transcript_id == transcript_id)
    )
    return result.scalar_one_or_none()


async def get_decisions(
    db: AsyncSession, summary_id: str
) -> list[MeetingDecision]:
    result = await db.execute(
        select(MeetingDecision).where(MeetingDecision.summary_id == summary_id)
    )
    return list(result.scalars().all())


async def get_action_items(
    db: AsyncSession, summary_id: str
) -> list[MeetingActionItem]:
    result = await db.execute(
        select(MeetingActionItem).where(MeetingActionItem.summary_id == summary_id)
    )
    return list(result.scalars().all())

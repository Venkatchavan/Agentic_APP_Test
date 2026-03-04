"""
Draft service — generate, edit, and manage drafts.
"""

import json
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.drafts.models import DraftReply
from app.ai.client import ai_extract
from app.common.exceptions import NotFoundError

logger = structlog.get_logger()

REPLY_PROMPT = """Draft a professional email reply based on the following context.

ORIGINAL EMAIL SUBJECT: {subject}
FROM: {sender}
BODY:
{body}

ADDITIONAL INSTRUCTIONS: {instructions}

Return JSON:
{{"subject": "Re: ...", "body_html": "<p>...</p>", "body_text": "...", "confidence": 0.0-1.0}}

Be professional, concise, and helpful. Do not fabricate facts.
"""

FOLLOWUP_PROMPT = """Draft a professional follow-up email based on this meeting summary.

MEETING: {title}
SUMMARY: {summary}
DECISIONS: {decisions}
ACTION ITEMS: {actions}

INSTRUCTIONS: {instructions}

Return JSON:
{{"subject": "...", "body_html": "<p>...</p>", "body_text": "...", "confidence": 0.0-1.0}}
"""


async def generate_reply_draft(
    db: AsyncSession,
    user_id: str,
    email_id: str,
    subject: str,
    sender: str,
    body: str,
    instructions: str = "",
) -> DraftReply:
    """Generate an AI draft reply for an email."""
    prompt = REPLY_PROMPT.format(
        subject=subject, sender=sender, body=body[:10000], instructions=instructions
    )
    raw = await ai_extract(prompt=prompt, system="You are a professional email writer.", task_type="draft_reply")
    data = _safe_parse(raw)

    draft = DraftReply(
        user_id=user_id,
        email_id=email_id,
        draft_type="email_reply",
        to_addresses_json=json.dumps([sender]),
        subject=data.get("subject", f"Re: {subject}")[:500],
        body_html=data.get("body_html", "")[:10000],
        body_text=data.get("body_text", "")[:10000],
        confidence=max(0.0, min(1.0, float(data.get("confidence", 0.5)))),
    )
    db.add(draft)
    await db.flush()
    logger.info("drafts.generated", draft_id=draft.id, type="email_reply")
    return draft


async def generate_followup_draft(
    db: AsyncSession, user_id: str, meeting_id: str,
    title: str, summary: str, decisions: str, actions: str,
    instructions: str = "",
) -> DraftReply:
    """Generate a follow-up draft for a meeting."""
    prompt = FOLLOWUP_PROMPT.format(
        title=title, summary=summary, decisions=decisions,
        actions=actions, instructions=instructions,
    )
    raw = await ai_extract(prompt=prompt, system="You are a professional email writer.", task_type="draft_followup")
    data = _safe_parse(raw)

    draft = DraftReply(
        user_id=user_id,
        meeting_id=meeting_id,
        draft_type="meeting_followup",
        subject=data.get("subject", f"Follow-up: {title}")[:500],
        body_html=data.get("body_html", "")[:10000],
        body_text=data.get("body_text", "")[:10000],
        confidence=max(0.0, min(1.0, float(data.get("confidence", 0.5)))),
    )
    db.add(draft)
    await db.flush()
    return draft


async def get_draft(db: AsyncSession, user_id: str, draft_id: str) -> DraftReply:
    result = await db.execute(
        select(DraftReply).where(DraftReply.id == draft_id, DraftReply.user_id == user_id)
    )
    d = result.scalar_one_or_none()
    if not d:
        raise NotFoundError("Draft", draft_id)
    return d


async def list_drafts(db: AsyncSession, user_id: str, skip=0, limit=50) -> list[DraftReply]:
    result = await db.execute(
        select(DraftReply).where(DraftReply.user_id == user_id)
        .order_by(DraftReply.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def update_draft(db: AsyncSession, draft: DraftReply, updates: dict) -> DraftReply:
    for key, val in updates.items():
        if val is not None and hasattr(draft, key):
            setattr(draft, key, val)
    draft.is_ai_generated = False  # User edited
    await db.flush()
    return draft


def _safe_parse(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}

"""
Inbox service — email ingestion and action management.
"""

import json
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.inbox.models import IngestedEmail, ExtractedEmailAction
from app.inbox.sanitizer import sanitize_email_body
from app.providers.base import NormalizedEmail
from app.common.exceptions import NotFoundError

logger = structlog.get_logger()


async def ingest_emails(
    db: AsyncSession,
    user_id: str,
    linked_account_id: str,
    emails: list[NormalizedEmail],
) -> list[IngestedEmail]:
    """Ingest normalized emails — sanitise, deduplicate, persist."""
    ingested = []
    for email in emails:
        # Deduplicate by provider_message_id
        existing = await db.execute(
            select(IngestedEmail).where(
                IngestedEmail.user_id == user_id,
                IngestedEmail.provider_message_id == email.provider_message_id,
            )
        )
        if existing.scalar_one_or_none():
            continue

        record = IngestedEmail(
            user_id=user_id,
            linked_account_id=linked_account_id,
            provider=email.provider,
            provider_message_id=email.provider_message_id,
            thread_id=email.thread_id,
            subject=email.subject,
            sender=email.sender,
            recipients_json=json.dumps(email.recipients),
            body_sanitized=sanitize_email_body(email.body_text or email.body_html),
            received_at=email.received_at,
        )
        db.add(record)
        ingested.append(record)

    await db.flush()
    logger.info("inbox.ingested", user_id=user_id, count=len(ingested))
    return ingested


async def list_emails(
    db: AsyncSession, user_id: str, skip: int = 0, limit: int = 50
) -> list[IngestedEmail]:
    """List ingested emails for a user."""
    result = await db.execute(
        select(IngestedEmail)
        .where(IngestedEmail.user_id == user_id)
        .order_by(IngestedEmail.received_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_email(db: AsyncSession, user_id: str, email_id: str) -> IngestedEmail:
    """Get a single email by ID."""
    result = await db.execute(
        select(IngestedEmail).where(
            IngestedEmail.id == email_id,
            IngestedEmail.user_id == user_id,
        )
    )
    email = result.scalar_one_or_none()
    if not email:
        raise NotFoundError("Email", email_id)
    return email


async def save_actions(
    db: AsyncSession, actions: list[ExtractedEmailAction]
) -> list[ExtractedEmailAction]:
    """Persist extracted actions."""
    for action in actions:
        db.add(action)
    await db.flush()
    return actions


async def get_actions_for_email(
    db: AsyncSession, user_id: str, email_id: str
) -> list[ExtractedEmailAction]:
    """Get all extracted actions for an email."""
    result = await db.execute(
        select(ExtractedEmailAction).where(
            ExtractedEmailAction.email_id == email_id,
            ExtractedEmailAction.user_id == user_id,
        )
    )
    return list(result.scalars().all())

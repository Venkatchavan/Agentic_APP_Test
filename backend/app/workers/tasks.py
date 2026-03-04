"""
Background tasks — executed by Celery workers.
Each task creates its own async DB session.
"""

from __future__ import annotations

import asyncio
import structlog
from app.workers.celery_app import celery_app

logger = structlog.get_logger()


def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def ingest_emails_task(self, user_id: str, account_id: str):
    """
    Periodic task: fetch new emails from a linked account
    and run AI extraction on them.
    """
    logger.info(
        "task.ingest_emails.start",
        user_id=user_id,
        account_id=account_id,
    )

    async def _run():
        from app.database import async_session_factory
        async with async_session_factory() as db:
            # 1. Get linked account & provider
            from app.accounts.service import get_linked_account
            account = await get_linked_account(db, user_id, account_id)
            if not account or not account.is_active:
                logger.warning("task.ingest_emails.inactive", account_id=account_id)
                return

            # 2. Fetch emails via provider adapter
            from app.providers import get_email_provider
            provider = get_email_provider(account.provider)
            emails = await provider.fetch_emails(
                account.access_token_enc, limit=20,
            )

            # 3. Ingest each email
            from app.inbox.service import ingest_email
            count = 0
            for email in emails:
                result = await ingest_email(db, user_id, account_id, email)
                if result:
                    count += 1

            await db.commit()
            logger.info("task.ingest_emails.done", count=count)

    try:
        _run_async(_run())
    except Exception as exc:
        logger.error("task.ingest_emails.failed", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=15)
def process_meeting_transcript_task(
    self, user_id: str, transcript_id: str,
):
    """Process a meeting transcript with AI extraction."""
    logger.info(
        "task.process_meeting.start",
        user_id=user_id,
        transcript_id=transcript_id,
    )

    async def _run():
        from app.database import async_session_factory
        async with async_session_factory() as db:
            from app.meetings.service import get_transcript, save_summary
            from app.meetings.extraction import extract_meeting_data

            transcript = await get_transcript(db, transcript_id)
            if not transcript:
                logger.warning("task.process_meeting.not_found")
                return

            data = await extract_meeting_data(transcript.content)
            await save_summary(db, transcript_id, user_id, data)
            await db.commit()
            logger.info("task.process_meeting.done")

    try:
        _run_async(_run())
    except Exception as exc:
        logger.error("task.process_meeting.failed", error=str(exc))
        raise self.retry(exc=exc)


@celery_app.task
def cleanup_expired_tokens_task():
    """Periodic: deactivate accounts with expired tokens."""
    logger.info("task.cleanup_tokens.start")

    async def _run():
        from datetime import datetime, timezone
        from sqlalchemy import update
        from app.database import async_session_factory
        from app.accounts.models import LinkedAccount

        async with async_session_factory() as db:
            stmt = (
                update(LinkedAccount)
                .where(
                    LinkedAccount.token_expires_at < datetime.now(timezone.utc),
                    LinkedAccount.is_active == True,  # noqa
                )
                .values(is_active=False)
            )
            result = await db.execute(stmt)
            await db.commit()
            logger.info("task.cleanup_tokens.done", deactivated=result.rowcount)

    _run_async(_run())

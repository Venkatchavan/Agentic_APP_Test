"""
Account-linking service — CRUD for linked provider accounts.
"""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.accounts.models import LinkedAccount
from app.common.exceptions import NotFoundError

logger = structlog.get_logger()


async def list_linked_accounts(db: AsyncSession, user_id: str) -> list[LinkedAccount]:
    """Return all linked accounts for a user."""
    result = await db.execute(
        select(LinkedAccount)
        .where(LinkedAccount.user_id == user_id)
        .order_by(LinkedAccount.created_at.desc())
    )
    return list(result.scalars().all())


async def get_linked_account(
    db: AsyncSession, user_id: str, account_id: str
) -> LinkedAccount:
    """Get a single linked account, scoped to user."""
    result = await db.execute(
        select(LinkedAccount).where(
            LinkedAccount.id == account_id,
            LinkedAccount.user_id == user_id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise NotFoundError("LinkedAccount", account_id)
    return account


async def create_linked_account(
    db: AsyncSession,
    user_id: str,
    provider: str,
    provider_account_id: str,
    provider_email: str,
    access_token_enc: str,
    refresh_token_enc: str | None,
    scopes: str,
) -> LinkedAccount:
    """Persist a new linked account after OAuth exchange."""
    account = LinkedAccount(
        user_id=user_id,
        provider=provider,
        provider_account_id=provider_account_id,
        provider_email=provider_email,
        access_token_enc=access_token_enc,
        refresh_token_enc=refresh_token_enc,
        scopes=scopes,
    )
    db.add(account)
    await db.flush()
    logger.info("accounts.linked", user_id=user_id, provider=provider)
    return account


async def unlink_account(db: AsyncSession, user_id: str, account_id: str) -> None:
    """Soft-delete (deactivate) a linked account."""
    account = await get_linked_account(db, user_id, account_id)
    account.is_active = False
    await db.flush()
    logger.info("accounts.unlinked", user_id=user_id, account_id=account_id)

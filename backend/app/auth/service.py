"""
Auth service — registration, login, token refresh.
"""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.schemas import RegisterRequest, TokenResponse
from app.common.exceptions import ConflictError, UnauthorizedError
from app.common.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


async def register_user(db: AsyncSession, req: RegisterRequest) -> User:
    """Create a new user account."""
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise ConflictError(f"Email '{req.email}' is already registered")

    user = User(
        email=req.email,
        display_name=req.display_name,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    await db.flush()
    logger.info("auth.user_registered", user_id=user.id, email=user.email)
    return user


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> User:
    """Verify credentials and return user."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not user.hashed_password:
        raise UnauthorizedError("Invalid email or password")
    if not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    if not user.is_active:
        raise UnauthorizedError("Account is deactivated")
    return user


def issue_tokens(user_id: str) -> TokenResponse:
    """Generate access + refresh token pair."""
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Fetch user by primary key."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

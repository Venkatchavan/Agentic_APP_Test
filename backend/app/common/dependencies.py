"""
Shared FastAPI dependencies — auth, DB session, pagination.
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db

settings = get_settings()


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    """Extract and verify user_id from JWT Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Missing Bearer token"},
        )
    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "UNAUTHORIZED", "message": "Invalid token payload"},
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Token verification failed"},
        )


# Typed dependency aliases for cleaner route signatures
CurrentUser = Annotated[str, Depends(get_current_user_id)]
DbSession = Annotated[AsyncSession, Depends(get_db)]


class PaginationParams:
    """Common pagination query params."""

    def __init__(self, skip: int = 0, limit: int = 50):
        self.skip = max(0, skip)
        self.limit = min(max(1, limit), 200)


Pagination = Annotated[PaginationParams, Depends()]

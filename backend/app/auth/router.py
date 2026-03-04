"""
Auth REST endpoints — register, login, refresh, me, OAuth starts.
"""

import structlog
from fastapi import APIRouter, HTTPException

from app.auth import schemas, service
from app.common.dependencies import CurrentUser, DbSession
from app.common.exceptions import AppError

logger = structlog.get_logger()
router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
async def register(req: schemas.RegisterRequest, db: DbSession):
    """Register a new user account."""
    try:
        user = await service.register_user(db, req)
        return user
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post("/login", response_model=schemas.TokenResponse)
async def login(req: schemas.LoginRequest, db: DbSession):
    """Authenticate and receive tokens."""
    try:
        user = await service.authenticate_user(db, req.email, req.password)
        return service.issue_tokens(user.id)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh_token(req: schemas.RefreshRequest, db: DbSession):
    """Exchange refresh token for new access token."""
    from jose import JWTError, jwt as jose_jwt
    from app.config import get_settings

    settings = get_settings()
    try:
        payload = jose_jwt.decode(
            req.refresh_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "Invalid refresh token"})
        user = await service.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "User not found"})
        return service.issue_tokens(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "Token expired or invalid"})


@router.get("/me", response_model=schemas.UserResponse)
async def get_me(user_id: CurrentUser, db: DbSession):
    """Get current authenticated user profile."""
    user = await service.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "User not found"})
    return user

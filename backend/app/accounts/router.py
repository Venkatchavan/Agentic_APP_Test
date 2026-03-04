"""
Account-linking REST endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.accounts import schemas, service
from app.common.dependencies import CurrentUser, DbSession
from app.common.exceptions import AppError

router = APIRouter()


@router.get("/", response_model=list[schemas.LinkedAccountResponse])
async def list_accounts(user_id: CurrentUser, db: DbSession):
    """List all linked provider accounts."""
    return await service.list_linked_accounts(db, user_id)


@router.post("/link", response_model=schemas.LinkedAccountResponse, status_code=201)
async def link_account(req: schemas.LinkAccountRequest, user_id: CurrentUser, db: DbSession):
    """Link a new provider account via OAuth authorization code."""
    try:
        # In production, exchange auth code with provider adapter here
        account = await service.create_linked_account(
            db=db,
            user_id=user_id,
            provider=req.provider,
            provider_account_id="pending_exchange",
            provider_email="pending@exchange.com",
            access_token_enc="encrypted_placeholder",
            refresh_token_enc="encrypted_placeholder",
            scopes="",
        )
        return account
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.delete("/{account_id}", status_code=204)
async def unlink_account(account_id: str, user_id: CurrentUser, db: DbSession):
    """Unlink (deactivate) a provider account."""
    try:
        await service.unlink_account(db, user_id, account_id)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})

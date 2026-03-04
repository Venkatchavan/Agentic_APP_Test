"""
Drafts REST endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.drafts import schemas, service
from app.common.dependencies import CurrentUser, DbSession, Pagination
from app.common.exceptions import AppError

router = APIRouter()


@router.get("/", response_model=list[schemas.DraftReplyResponse])
async def list_drafts(user_id: CurrentUser, db: DbSession, page: Pagination):
    """List all drafts."""
    return await service.list_drafts(db, user_id, page.skip, page.limit)


@router.get("/{draft_id}", response_model=schemas.DraftReplyResponse)
async def get_draft(draft_id: str, user_id: CurrentUser, db: DbSession):
    """Get a single draft."""
    try:
        return await service.get_draft(db, user_id, draft_id)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.put("/{draft_id}", response_model=schemas.DraftReplyResponse)
async def edit_draft(
    draft_id: str, req: schemas.EditDraftRequest, user_id: CurrentUser, db: DbSession
):
    """Edit a draft before approval — allows user to modify AI output."""
    try:
        draft = await service.get_draft(db, user_id, draft_id)
        updates = req.model_dump(exclude_none=True)
        if "to_addresses" in updates:
            import json
            updates["to_addresses_json"] = json.dumps(updates.pop("to_addresses"))
        return await service.update_draft(db, draft, updates)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})

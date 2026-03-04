"""
Inbox REST endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.inbox import schemas, service
from app.inbox.extraction import extract_actions_from_email
from app.common.dependencies import CurrentUser, DbSession, Pagination
from app.common.exceptions import AppError

router = APIRouter()


@router.get("/emails", response_model=list[schemas.IngestedEmailResponse])
async def list_emails(user_id: CurrentUser, db: DbSession, page: Pagination):
    """List ingested emails."""
    return await service.list_emails(db, user_id, page.skip, page.limit)


@router.get("/emails/{email_id}", response_model=schemas.EmailDetailResponse)
async def get_email_detail(email_id: str, user_id: CurrentUser, db: DbSession):
    """Get email with extracted actions."""
    try:
        email = await service.get_email(db, user_id, email_id)
        actions = await service.get_actions_for_email(db, user_id, email_id)
        return schemas.EmailDetailResponse(email=email, actions=actions)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post("/emails/{email_id}/extract", response_model=list[schemas.ExtractedActionResponse])
async def extract_actions(email_id: str, user_id: CurrentUser, db: DbSession):
    """Run AI extraction on an email — results are proposals, not executed."""
    try:
        email = await service.get_email(db, user_id, email_id)
        actions = await extract_actions_from_email(
            email_id=email.id,
            user_id=user_id,
            subject=email.subject,
            sender=email.sender,
            body=email.body_sanitized,
        )
        saved = await service.save_actions(db, actions)
        email.processed = True
        return saved
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post("/ingest", response_model=list[schemas.IngestedEmailResponse])
async def ingest_emails(req: schemas.IngestEmailsRequest, user_id: CurrentUser, db: DbSession):
    """Trigger email ingestion from a linked account."""
    # In production, this would call the provider adapter
    # For now, returns empty — the worker handles actual ingestion
    return []

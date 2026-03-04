"""
Scheduling REST endpoints.
"""

from fastapi import APIRouter, HTTPException

from app.scheduling import schemas, service
from app.common.dependencies import CurrentUser, DbSession, Pagination
from app.common.exceptions import AppError

router = APIRouter()


@router.get("/proposals", response_model=list[schemas.ScheduleProposalResponse])
async def list_proposals(user_id: CurrentUser, db: DbSession, page: Pagination):
    """List schedule proposals."""
    return await service.list_proposals(db, user_id, page.skip, page.limit)


@router.post("/proposals", response_model=schemas.ScheduleProposalResponse, status_code=201)
async def create_proposal(
    req: schemas.CreateProposalRequest, user_id: CurrentUser, db: DbSession
):
    """Create a new schedule proposal."""
    return await service.create_proposal(
        db=db,
        user_id=user_id,
        **req.model_dump(),
    )


@router.get("/proposals/{proposal_id}", response_model=schemas.ScheduleProposalResponse)
async def get_proposal(proposal_id: str, user_id: CurrentUser, db: DbSession):
    """Get a single proposal."""
    try:
        return await service.get_proposal(db, user_id, proposal_id)
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})

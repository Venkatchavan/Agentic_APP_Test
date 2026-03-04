"""
Meetings REST endpoints.
"""

import json
from fastapi import APIRouter, HTTPException

from app.meetings import schemas, service
from app.meetings.extraction import extract_meeting_content
from app.common.dependencies import CurrentUser, DbSession, Pagination
from app.common.exceptions import AppError

router = APIRouter()


@router.get("/", response_model=list[schemas.TranscriptResponse])
async def list_meetings(user_id: CurrentUser, db: DbSession, page: Pagination):
    """List all meeting transcripts."""
    return await service.list_transcripts(db, user_id, page.skip, page.limit)


@router.post("/import", response_model=schemas.TranscriptResponse, status_code=201)
async def import_meeting(req: schemas.TranscriptImportRequest, user_id: CurrentUser, db: DbSession):
    """Import a meeting transcript."""
    return await service.import_transcript(
        db=db,
        user_id=user_id,
        title=req.title,
        source_type=req.source_type,
        transcript_text=req.transcript_text or "",
        meeting_date=req.meeting_date,
        participants=req.participants,
    )


@router.get("/{transcript_id}", response_model=schemas.MeetingDetailResponse)
async def get_meeting_detail(transcript_id: str, user_id: CurrentUser, db: DbSession):
    """Get meeting transcript with summary, decisions, and actions."""
    try:
        transcript = await service.get_transcript(db, user_id, transcript_id)
        summary = await service.get_summary(db, transcript_id)
        decisions = []
        actions = []
        if summary:
            decisions = await service.get_decisions(db, summary.id)
            actions = await service.get_action_items(db, summary.id)
        return schemas.MeetingDetailResponse(
            transcript=transcript,
            summary=summary,
            decisions=decisions,
            action_items=actions,
        )
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})


@router.post("/{transcript_id}/process", response_model=schemas.MeetingSummaryResponse)
async def process_meeting(transcript_id: str, user_id: CurrentUser, db: DbSession):
    """Run AI extraction on a transcript — outputs are proposals."""
    try:
        transcript = await service.get_transcript(db, user_id, transcript_id)
        summary, decisions, actions = await extract_meeting_content(
            transcript_id=transcript.id,
            user_id=user_id,
            title=transcript.title,
            participants=transcript.participants_json,
            transcript=transcript.transcript_text,
        )
        await service.save_summary(db, summary, decisions, actions)
        transcript.processed = True
        return summary
    except AppError as e:
        raise HTTPException(status_code=e.status_code, detail={"code": e.code, "message": e.message})

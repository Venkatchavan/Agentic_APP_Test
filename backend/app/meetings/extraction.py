"""
Meeting extraction — AI-powered summary, decision, and action extraction.
"""

import json
import structlog

from app.ai.client import ai_extract
from app.meetings.models import MeetingActionItem, MeetingDecision, MeetingSummary

logger = structlog.get_logger()

SUMMARY_PROMPT = """Analyze the following meeting transcript and produce:
1. A concise summary (2-4 paragraphs)
2. Key points (bulleted list)
3. Decisions made (with who decided, if clear)
4. Action items (with owner and due date, if mentioned)

Return JSON with this structure:
{{
  "summary": "...",
  "key_points": ["..."],
  "decisions": [
    {{"text": "...", "decided_by": "..." or null, "confidence": 0.0-1.0, "source_span": "..."}}
  ],
  "action_items": [
    {{"title": "...", "description": "...", "owner": "..." or null, "due_date": "ISO8601" or null, "confidence": 0.0-1.0, "source_span": "..."}}
  ],
  "confidence": 0.0-1.0
}}

Do NOT invent content not present in the transcript.

MEETING TITLE: {title}
PARTICIPANTS: {participants}
TRANSCRIPT:
{transcript}
"""

VALID_STATUSES = {"proposed", "approved", "rejected", "executed"}


async def extract_meeting_content(
    transcript_id: str,
    user_id: str,
    title: str,
    participants: str,
    transcript: str,
) -> tuple[MeetingSummary, list[MeetingDecision], list[MeetingActionItem]]:
    """Run AI extraction on transcript, validate, return structured outputs."""
    prompt = SUMMARY_PROMPT.format(
        title=title, participants=participants, transcript=transcript[:20000]
    )

    raw = await ai_extract(
        system_prompt="You are a precise meeting analyst. Output valid JSON only.",
        user_content=prompt,
    )

    # ai_extract already returns a parsed dict
    data = raw if isinstance(raw, dict) else {}
    return _parse_meeting_output(data, transcript_id, user_id)


def _parse_meeting_output(
    data: dict, transcript_id: str, user_id: str
) -> tuple[MeetingSummary, list[MeetingDecision], list[MeetingActionItem]]:
    """Deterministic validation of AI output."""

    summary = MeetingSummary(
        transcript_id=transcript_id,
        user_id=user_id,
        summary_text=str(data.get("summary", "Failed to generate summary"))[:5000],
        key_points_json=json.dumps(data.get("key_points", [])),
        confidence=_clamp(data.get("confidence", 0.0)),
    )

    decisions = []
    for d in data.get("decisions", []):
        if not isinstance(d, dict):
            continue
        decisions.append(MeetingDecision(
            summary_id=summary.id,
            user_id=user_id,
            decision_text=str(d.get("text", ""))[:2000],
            decided_by=str(d.get("decided_by", ""))[:255] or None,
            confidence=_clamp(d.get("confidence", 0.0)),
            source_span=str(d.get("source_span", ""))[:1000],
        ))

    actions = []
    for a in data.get("action_items", []):
        if not isinstance(a, dict):
            continue
        actions.append(MeetingActionItem(
            summary_id=summary.id,
            user_id=user_id,
            title=str(a.get("title", "Untitled"))[:500],
            description=str(a.get("description", ""))[:2000],
            owner=str(a.get("owner", ""))[:255] or None,
            due_date=_safe_date(a.get("due_date")),
            confidence=_clamp(a.get("confidence", 0.0)),
            source_span=str(a.get("source_span", ""))[:1000],
            status="proposed",
        ))

    return summary, decisions, actions


def _clamp(val, lo=0.0, hi=1.0) -> float:
    try:
        return max(lo, min(hi, float(val)))
    except (TypeError, ValueError):
        return 0.0


def _safe_date(val):
    if not val:
        return None
    from datetime import datetime
    try:
        return datetime.fromisoformat(str(val))
    except (ValueError, TypeError):
        return None

"""
Inbox extraction — uses AI layer to extract actions from emails.
Deterministic validation wraps all model outputs.
"""

import json
import structlog

from app.ai.client import ai_extract
from app.inbox.models import ExtractedEmailAction

logger = structlog.get_logger()

EXTRACTION_PROMPT = """Analyze the following email and extract all actionable items.
For each action, provide:
- action_type: one of [task, approval, commitment, schedule_intent, followup]
- title: short descriptive title
- description: brief detail
- due_date: ISO 8601 date if mentioned, else null
- owner: person responsible if mentioned, else null
- confidence: 0.0 to 1.0
- source_span: the exact phrase from the email that indicates this action

Return a JSON array of objects. If no actions found, return [].
Do NOT invent actions that are not clearly indicated in the email.

EMAIL SUBJECT: {subject}
FROM: {sender}
BODY:
{body}
"""

# Allowed action types — deterministic enforcement
VALID_ACTION_TYPES = {"task", "approval", "commitment", "schedule_intent", "followup"}


async def extract_actions_from_email(
    email_id: str,
    user_id: str,
    subject: str,
    sender: str,
    body: str,
) -> list[ExtractedEmailAction]:
    """
    Run AI extraction → validate → return typed actions.
    Model output is a proposal, never directly executed.
    """
    prompt = EXTRACTION_PROMPT.format(subject=subject, sender=sender, body=body)

    raw_output = await ai_extract(
        system_prompt="You are a precise email action extractor. Output valid JSON only.",
        user_content=prompt,
    )

    # ai_extract returns already-parsed JSON (dict or list)
    actions = _parse_and_validate(raw_output, email_id, user_id)
    logger.info(
        "inbox.extraction_complete",
        email_id=email_id,
        action_count=len(actions),
    )
    return actions


def _parse_and_validate(
    raw, email_id: str, user_id: str
) -> list[ExtractedEmailAction]:
    """Deterministic validation layer — never trust raw model output."""
    # raw may be already-parsed (list/dict) or a string
    if isinstance(raw, str):
        try:
            items = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("inbox.extraction_parse_failed", raw_preview=raw[:200])
            return []
    elif isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        items = [raw]
    else:
        return []

    if not isinstance(items, list):
        items = [items]

    results = []
    for item in items:
        if not isinstance(item, dict):
            continue
        action_type = str(item.get("action_type", "")).lower()
        if action_type not in VALID_ACTION_TYPES:
            continue

        confidence = float(item.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))

        results.append(ExtractedEmailAction(
            email_id=email_id,
            user_id=user_id,
            action_type=action_type,
            title=str(item.get("title", "Untitled action"))[:500],
            description=str(item.get("description", ""))[:2000],
            due_date=_safe_parse_date(item.get("due_date")),
            owner=str(item.get("owner", ""))[:255] or None,
            confidence=confidence,
            source_span=str(item.get("source_span", ""))[:1000],
            ambiguity_flags=json.dumps(item.get("ambiguity_flags", [])),
            status="proposed",  # Always starts as proposal
        ))
    return results


def _safe_parse_date(val):
    """Parse ISO date string safely, return None on failure."""
    if not val:
        return None
    from datetime import datetime
    try:
        return datetime.fromisoformat(str(val))
    except (ValueError, TypeError):
        return None

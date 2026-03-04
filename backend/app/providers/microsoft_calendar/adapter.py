"""
Microsoft Calendar (Graph API) adapter — implements CalendarProvider.
"""

from datetime import datetime, timezone

import httpx
import structlog

from app.providers.base import CalendarProvider, CalendarSlot, NormalizedCalendarEvent

logger = structlog.get_logger()

GRAPH_API = "https://graph.microsoft.com/v1.0"


class MicrosoftCalendarAdapter(CalendarProvider):
    """Microsoft Graph Calendar adapter."""

    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    async def list_events(
        self, access_token: str, start: datetime, end: datetime
    ) -> list[NormalizedCalendarEvent]:
        params = {
            "$filter": (
                f"start/dateTime ge '{start.isoformat()}' "
                f"and end/dateTime le '{end.isoformat()}'"
            ),
            "$orderby": "start/dateTime",
            "$top": 100,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_API}/me/events",
                headers=self._headers(access_token),
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("value", []):
            results.append(NormalizedCalendarEvent(
                provider="microsoft_calendar",
                provider_event_id=item["id"],
                title=item.get("subject", "(no title)"),
                description=item.get("body", {}).get("content", ""),
                start_time=datetime.fromisoformat(
                    item["start"]["dateTime"]
                ).replace(tzinfo=timezone.utc),
                end_time=datetime.fromisoformat(
                    item["end"]["dateTime"]
                ).replace(tzinfo=timezone.utc),
                attendees=[
                    a.get("emailAddress", {}).get("address", "")
                    for a in item.get("attendees", [])
                ],
                location=item.get("location", {}).get("displayName", ""),
                is_all_day=item.get("isAllDay", False),
            ))
        return results

    async def get_free_slots(
        self, access_token: str, start: datetime, end: datetime,
        duration_minutes: int = 30,
    ) -> list[CalendarSlot]:
        events = await self.list_events(access_token, start, end)
        busy = sorted([(e.start_time, e.end_time) for e in events], key=lambda x: x[0])

        slots: list[CalendarSlot] = []
        cursor = start
        for busy_start, busy_end in busy:
            gap = (busy_start - cursor).total_seconds()
            if gap >= duration_minutes * 60:
                slots.append(CalendarSlot(
                    start_time=cursor,
                    end_time=busy_start,
                    duration_minutes=int(gap / 60),
                ))
            cursor = max(cursor, busy_end)
        remaining = (end - cursor).total_seconds()
        if remaining >= duration_minutes * 60:
            slots.append(CalendarSlot(
                start_time=cursor, end_time=end, duration_minutes=int(remaining / 60)
            ))
        return slots

    async def create_event(
        self, access_token: str, event: NormalizedCalendarEvent
    ) -> str:
        """Create event — MUST be gated by approval before calling."""
        payload = {
            "subject": event.title,
            "body": {"contentType": "HTML", "content": event.description},
            "start": {"dateTime": event.start_time.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": event.end_time.isoformat(), "timeZone": "UTC"},
            "attendees": [
                {"emailAddress": {"address": a}, "type": "required"}
                for a in event.attendees
            ],
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GRAPH_API}/me/events",
                headers={**self._headers(access_token), "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
        event_id = resp.json()["id"]
        logger.info("mscal.event_created", event_id=event_id)
        return event_id

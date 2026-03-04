"""
Google Calendar adapter — implements CalendarProvider.
"""

from datetime import datetime, timedelta, timezone

import httpx
import structlog

from app.providers.base import CalendarProvider, CalendarSlot, NormalizedCalendarEvent

logger = structlog.get_logger()

GCAL_API = "https://www.googleapis.com/calendar/v3"


class GoogleCalendarAdapter(CalendarProvider):
    """Google Calendar API adapter."""

    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    async def list_events(
        self, access_token: str, start: datetime, end: datetime
    ) -> list[NormalizedCalendarEvent]:
        params = {
            "timeMin": start.isoformat(),
            "timeMax": end.isoformat(),
            "singleEvents": "true",
            "orderBy": "startTime",
            "maxResults": 100,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GCAL_API}/calendars/primary/events",
                headers=self._headers(access_token),
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("items", []):
            start_dt = self._parse_dt(item.get("start", {}))
            end_dt = self._parse_dt(item.get("end", {}))
            results.append(NormalizedCalendarEvent(
                provider="google_calendar",
                provider_event_id=item["id"],
                title=item.get("summary", "(no title)"),
                description=item.get("description", ""),
                start_time=start_dt,
                end_time=end_dt,
                attendees=[
                    a.get("email", "") for a in item.get("attendees", [])
                ],
                location=item.get("location", ""),
                status=item.get("status", "confirmed"),
            ))
        return results

    def _parse_dt(self, dt_obj: dict) -> datetime:
        if "dateTime" in dt_obj:
            return datetime.fromisoformat(dt_obj["dateTime"])
        if "date" in dt_obj:
            return datetime.fromisoformat(dt_obj["date"]).replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc)

    async def get_free_slots(
        self, access_token: str, start: datetime, end: datetime,
        duration_minutes: int = 30,
    ) -> list[CalendarSlot]:
        events = await self.list_events(access_token, start, end)
        busy = [(e.start_time, e.end_time) for e in events]
        busy.sort(key=lambda x: x[0])

        slots: list[CalendarSlot] = []
        cursor = start
        for busy_start, busy_end in busy:
            if (busy_start - cursor).total_seconds() >= duration_minutes * 60:
                slots.append(CalendarSlot(
                    start_time=cursor,
                    end_time=busy_start,
                    duration_minutes=int((busy_start - cursor).total_seconds() / 60),
                ))
            cursor = max(cursor, busy_end)
        if (end - cursor).total_seconds() >= duration_minutes * 60:
            slots.append(CalendarSlot(
                start_time=cursor,
                end_time=end,
                duration_minutes=int((end - cursor).total_seconds() / 60),
            ))
        return slots

    async def create_event(
        self, access_token: str, event: NormalizedCalendarEvent
    ) -> str:
        """Create event — MUST be gated by approval before calling."""
        payload = {
            "summary": event.title,
            "description": event.description,
            "start": {"dateTime": event.start_time.isoformat()},
            "end": {"dateTime": event.end_time.isoformat()},
            "attendees": [{"email": a} for a in event.attendees],
            "location": event.location,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GCAL_API}/calendars/primary/events",
                headers={**self._headers(access_token), "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
        event_id = resp.json()["id"]
        logger.info("gcal.event_created", event_id=event_id)
        return event_id

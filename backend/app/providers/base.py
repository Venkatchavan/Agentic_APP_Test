"""
Provider adapter base classes — abstract interfaces for email and calendar.
All provider-specific logic must implement these; domain code only depends on these.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pydantic import BaseModel


# ── Normalized models (provider-agnostic) ────────────────


class NormalizedEmail(BaseModel):
    """Provider-agnostic email representation."""
    provider: str
    provider_message_id: str
    thread_id: str | None = None
    subject: str
    sender: str
    recipients: list[str]
    cc: list[str] = []
    body_text: str
    body_html: str = ""
    received_at: datetime
    has_attachments: bool = False
    labels: list[str] = []


class NormalizedCalendarEvent(BaseModel):
    """Provider-agnostic calendar event."""
    provider: str
    provider_event_id: str
    title: str
    description: str = ""
    start_time: datetime
    end_time: datetime
    attendees: list[str] = []
    location: str = ""
    is_all_day: bool = False
    status: str = "confirmed"  # confirmed | tentative | cancelled


class CalendarSlot(BaseModel):
    """A proposed free slot."""
    start_time: datetime
    end_time: datetime
    duration_minutes: int


# ── Abstract adapters ────────────────────────────────────


class EmailProvider(ABC):
    """Abstract email provider adapter."""

    @abstractmethod
    async def fetch_emails(
        self, access_token: str, max_results: int = 20, page_token: str | None = None
    ) -> list[NormalizedEmail]:
        ...

    @abstractmethod
    async def fetch_thread(
        self, access_token: str, thread_id: str
    ) -> list[NormalizedEmail]:
        ...

    @abstractmethod
    async def create_draft(
        self, access_token: str, to: list[str], subject: str, body_html: str,
        in_reply_to: str | None = None,
    ) -> str:
        """Create a draft reply. Returns provider draft ID."""
        ...

    @abstractmethod
    async def send_draft(self, access_token: str, draft_id: str) -> str:
        """Send a previously created draft. Returns message ID. APPROVAL-GATED."""
        ...


class CalendarProvider(ABC):
    """Abstract calendar provider adapter."""

    @abstractmethod
    async def list_events(
        self, access_token: str, start: datetime, end: datetime
    ) -> list[NormalizedCalendarEvent]:
        ...

    @abstractmethod
    async def get_free_slots(
        self, access_token: str, start: datetime, end: datetime,
        duration_minutes: int = 30,
    ) -> list[CalendarSlot]:
        ...

    @abstractmethod
    async def create_event(
        self, access_token: str, event: NormalizedCalendarEvent
    ) -> str:
        """Create calendar event. Returns provider event ID. APPROVAL-GATED."""
        ...

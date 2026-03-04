"""Providers package — adapter interfaces, registry, and factory."""

from app.providers.base import (
    EmailProvider,
    CalendarProvider,
    NormalizedEmail,
    NormalizedCalendarEvent,
)


def get_email_provider(provider_name: str) -> EmailProvider:
    """Factory: return the correct email adapter by provider name."""
    if provider_name == "gmail":
        from app.providers.gmail.adapter import GmailAdapter
        return GmailAdapter()
    elif provider_name == "outlook":
        from app.providers.outlook.adapter import OutlookAdapter
        return OutlookAdapter()
    else:
        raise ValueError(f"Unknown email provider: {provider_name}")


def get_calendar_provider(provider_name: str) -> CalendarProvider:
    """Factory: return the correct calendar adapter by provider name."""
    if provider_name == "google_calendar":
        from app.providers.google_calendar.adapter import GoogleCalendarAdapter
        return GoogleCalendarAdapter()
    elif provider_name == "microsoft_calendar":
        from app.providers.microsoft_calendar.adapter import MicrosoftCalendarAdapter
        return MicrosoftCalendarAdapter()
    else:
        raise ValueError(f"Unknown calendar provider: {provider_name}")


__all__ = [
    "EmailProvider",
    "CalendarProvider",
    "NormalizedEmail",
    "NormalizedCalendarEvent",
    "get_email_provider",
    "get_calendar_provider",
]

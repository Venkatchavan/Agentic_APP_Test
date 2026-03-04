"""
Gmail adapter — implements EmailProvider for Google Gmail API.
"""

import base64
from datetime import datetime, timezone
from email.mime.text import MIMEText

import httpx
import structlog

from app.providers.base import EmailProvider, NormalizedEmail

logger = structlog.get_logger()

GMAIL_API = "https://gmail.googleapis.com/gmail/v1"


class GmailAdapter(EmailProvider):
    """Gmail API adapter. All calls use user access token."""

    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    async def fetch_emails(
        self, access_token: str, max_results: int = 20, page_token: str | None = None
    ) -> list[NormalizedEmail]:
        params = {"maxResults": max_results, "q": "is:inbox"}
        if page_token:
            params["pageToken"] = page_token

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GMAIL_API}/users/me/messages",
                headers=self._headers(access_token),
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        messages = data.get("messages", [])
        results = []
        for msg_stub in messages[:max_results]:
            email = await self._fetch_message(access_token, msg_stub["id"])
            if email:
                results.append(email)
        return results

    async def _fetch_message(self, token: str, message_id: str) -> NormalizedEmail | None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GMAIL_API}/users/me/messages/{message_id}",
                headers=self._headers(token),
                params={"format": "full"},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()

        headers = {h["name"].lower(): h["value"] for h in data.get("payload", {}).get("headers", [])}
        body_text = self._extract_body(data.get("payload", {}))

        return NormalizedEmail(
            provider="gmail",
            provider_message_id=data["id"],
            thread_id=data.get("threadId"),
            subject=headers.get("subject", "(no subject)"),
            sender=headers.get("from", ""),
            recipients=self._parse_addresses(headers.get("to", "")),
            cc=self._parse_addresses(headers.get("cc", "")),
            body_text=body_text,
            received_at=datetime.fromtimestamp(
                int(data.get("internalDate", "0")) / 1000, tz=timezone.utc
            ),
            labels=data.get("labelIds", []),
        )

    def _extract_body(self, payload: dict) -> str:
        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
        return ""

    def _parse_addresses(self, raw: str) -> list[str]:
        return [a.strip() for a in raw.split(",") if a.strip()] if raw else []

    async def fetch_thread(self, access_token: str, thread_id: str) -> list[NormalizedEmail]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GMAIL_API}/users/me/threads/{thread_id}",
                headers=self._headers(access_token),
                params={"format": "full"},
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for msg in data.get("messages", []):
            headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
            body_text = self._extract_body(msg.get("payload", {}))
            results.append(NormalizedEmail(
                provider="gmail",
                provider_message_id=msg["id"],
                thread_id=thread_id,
                subject=headers.get("subject", ""),
                sender=headers.get("from", ""),
                recipients=self._parse_addresses(headers.get("to", "")),
                body_text=body_text,
                received_at=datetime.fromtimestamp(
                    int(msg.get("internalDate", "0")) / 1000, tz=timezone.utc
                ),
            ))
        return results

    async def create_draft(
        self, access_token: str, to: list[str], subject: str, body_html: str,
        in_reply_to: str | None = None,
    ) -> str:
        mime = MIMEText(body_html, "html")
        mime["to"] = ", ".join(to)
        mime["subject"] = subject
        if in_reply_to:
            mime["In-Reply-To"] = in_reply_to
        raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GMAIL_API}/users/me/drafts",
                headers=self._headers(access_token),
                json={"message": {"raw": raw}},
            )
            resp.raise_for_status()
        draft_id = resp.json()["id"]
        logger.info("gmail.draft_created", draft_id=draft_id)
        return draft_id

    async def send_draft(self, access_token: str, draft_id: str) -> str:
        """Send draft — MUST be gated by approval before calling."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GMAIL_API}/users/me/drafts/send",
                headers=self._headers(access_token),
                json={"id": draft_id},
            )
            resp.raise_for_status()
        msg_id = resp.json().get("id", draft_id)
        logger.info("gmail.draft_sent", message_id=msg_id)
        return msg_id

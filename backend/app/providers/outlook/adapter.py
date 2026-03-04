"""
Outlook / Microsoft Graph adapter — implements EmailProvider.
"""

from datetime import datetime, timezone

import httpx
import structlog

from app.providers.base import EmailProvider, NormalizedEmail

logger = structlog.get_logger()

GRAPH_API = "https://graph.microsoft.com/v1.0"


class OutlookAdapter(EmailProvider):
    """Microsoft Graph Mail adapter."""

    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    async def fetch_emails(
        self, access_token: str, max_results: int = 20, page_token: str | None = None
    ) -> list[NormalizedEmail]:
        params = {"$top": max_results, "$orderby": "receivedDateTime desc"}
        if page_token:
            params["$skip"] = page_token

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_API}/me/messages",
                headers=self._headers(access_token),
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for msg in data.get("value", []):
            results.append(self._normalize(msg))
        return results

    def _normalize(self, msg: dict) -> NormalizedEmail:
        return NormalizedEmail(
            provider="outlook",
            provider_message_id=msg["id"],
            thread_id=msg.get("conversationId"),
            subject=msg.get("subject", "(no subject)"),
            sender=msg.get("from", {}).get("emailAddress", {}).get("address", ""),
            recipients=[
                r["emailAddress"]["address"]
                for r in msg.get("toRecipients", [])
                if "emailAddress" in r
            ],
            cc=[
                r["emailAddress"]["address"]
                for r in msg.get("ccRecipients", [])
                if "emailAddress" in r
            ],
            body_text=msg.get("body", {}).get("content", ""),
            received_at=datetime.fromisoformat(
                msg.get("receivedDateTime", "2000-01-01T00:00:00Z")
            ),
            has_attachments=msg.get("hasAttachments", False),
        )

    async def fetch_thread(
        self, access_token: str, thread_id: str
    ) -> list[NormalizedEmail]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{GRAPH_API}/me/messages",
                headers=self._headers(access_token),
                params={
                    "$filter": f"conversationId eq '{thread_id}'",
                    "$orderby": "receivedDateTime asc",
                    "$top": 50,
                },
            )
            resp.raise_for_status()
            data = resp.json()
        return [self._normalize(msg) for msg in data.get("value", [])]

    async def create_draft(
        self, access_token: str, to: list[str], subject: str, body_html: str,
        in_reply_to: str | None = None,
    ) -> str:
        payload: dict = {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body_html},
            "toRecipients": [
                {"emailAddress": {"address": addr}} for addr in to
            ],
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GRAPH_API}/me/messages",
                headers={**self._headers(access_token), "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
        draft_id = resp.json()["id"]
        logger.info("outlook.draft_created", draft_id=draft_id)
        return draft_id

    async def send_draft(self, access_token: str, draft_id: str) -> str:
        """Send draft — MUST be gated by approval before calling."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{GRAPH_API}/me/messages/{draft_id}/send",
                headers=self._headers(access_token),
            )
            resp.raise_for_status()
        logger.info("outlook.draft_sent", draft_id=draft_id)
        return draft_id

"""
Shared security utilities — hashing, token creation, sanitisation.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
import bleach

from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Password hashing ────────────────────────────────────


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT tokens ───────────────────────────────────────────


def create_access_token(user_id: str, extra: dict | None = None) -> str:
    """Create a short-lived access token."""
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )
    payload = {"sub": user_id, "exp": expires, "type": "access"}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    """Create a longer-lived refresh token."""
    expires = datetime.now(timezone.utc) + timedelta(
        days=settings.jwt_refresh_token_expire_days
    )
    payload = {"sub": user_id, "exp": expires, "type": "refresh"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# ── HTML sanitisation (emails) ───────────────────────────

ALLOWED_TAGS = [
    "p", "br", "b", "i", "u", "strong", "em", "a", "ul", "ol", "li",
    "h1", "h2", "h3", "h4", "blockquote", "pre", "code", "span", "div",
]
ALLOWED_ATTRS = {"a": ["href", "title"], "span": ["class"], "div": ["class"]}


def sanitize_html(raw_html: str) -> str:
    """Strip dangerous HTML — safe for model processing."""
    return bleach.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True,
    )


def redact_secrets(text: str) -> str:
    """Best-effort redaction of common secret patterns."""
    import re
    patterns = [
        (r'(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*\S+', r'\1=***REDACTED***'),
        (r'(?i)bearer\s+\S+', 'Bearer ***REDACTED***'),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)
    return text

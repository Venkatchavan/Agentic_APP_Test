"""
Backend configuration — environment-driven settings.
All secrets loaded from env vars, never hardcoded.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central app configuration. Every secret comes from env."""

    # ── App ──────────────────────────────────────────────
    app_name: str = "Agentic Productivity API"
    app_version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # ── Database ─────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agentic_app"
    database_echo: bool = False

    # ── Redis ────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Auth / JWT ───────────────────────────────────────
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── OAuth — Gmail ────────────────────────────────────
    gmail_client_id: str = ""
    gmail_client_secret: str = ""
    gmail_redirect_uri: str = "http://localhost:8000/api/v1/auth/gmail/callback"
    gmail_scopes: str = "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.compose"

    # ── OAuth — Outlook ──────────────────────────────────
    outlook_client_id: str = ""
    outlook_client_secret: str = ""
    outlook_redirect_uri: str = "http://localhost:8000/api/v1/auth/outlook/callback"
    outlook_tenant_id: str = "common"

    # ── OAuth — Google Calendar ──────────────────────────
    google_calendar_scopes: str = "https://www.googleapis.com/auth/calendar"

    # ── OAuth — Microsoft Calendar ───────────────────────
    ms_calendar_scopes: str = "Calendars.ReadWrite"

    # ── AI Layer ─────────────────────────────────────────
    ai_provider: str = "gemini"  # "openai" | "anthropic" | "gemini"
    ai_openai_api_key: str = ""
    ai_openai_model: str = "gpt-4o"
    ai_anthropic_api_key: str = ""
    ai_anthropic_model: str = "claude-sonnet-4-20250514"
    ai_gemini_api_key: str = ""
    ai_gemini_model: str = "gemini-2.0-flash"
    ai_fallback_model: str = "gemini-2.0-flash"
    ai_max_retries: int = 3
    ai_request_timeout: int = 60
    ai_budget_limit_usd: float = 500.0

    # ── Object Storage ───────────────────────────────────
    s3_bucket_name: str = "agentic-app-artifacts"
    s3_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    # ── Observability ────────────────────────────────────
    log_level: str = "INFO"
    enable_tracing: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    """Return cached settings singleton."""
    return Settings()

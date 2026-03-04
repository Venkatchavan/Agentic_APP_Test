"""AI module router — exposes model info and usage stats."""

from fastapi import APIRouter, Depends

from app.common.dependencies import CurrentUser
from app.ai.client import _budget_spent_usd
from app.config import get_settings

settings = get_settings()

router = APIRouter()


@router.get("/status")
async def ai_status(user: CurrentUser):
    """Return current AI provider config and budget usage."""
    model_map = {
        "openai": settings.ai_openai_model,
        "anthropic": settings.ai_anthropic_model,
        "gemini": settings.ai_gemini_model,
    }
    return {
        "provider": settings.ai_provider,
        "model": model_map.get(settings.ai_provider, "unknown"),
        "budget_limit_usd": settings.ai_budget_limit_usd,
        "budget_spent_usd": round(_budget_spent_usd, 4),
    }

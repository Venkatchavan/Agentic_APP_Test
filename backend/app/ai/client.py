"""
Model-agnostic AI client.
Supports OpenAI, Anthropic, and Google Gemini — chosen via settings.ai_provider.
All callers use `ai_extract()` or `ai_generate()` only.
"""

from __future__ import annotations

import asyncio
import json
import structlog
import httpx

from app.config import get_settings
from app.common.exceptions import AIBudgetExceededError

settings = get_settings()

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Lightweight budget gate (in-memory; swap to Redis for multi-worker)
# ---------------------------------------------------------------------------
_budget_spent_usd: float = 0.0


def _check_budget(estimated_cost: float) -> None:
    global _budget_spent_usd
    limit = settings.ai_budget_limit_usd
    if limit and (_budget_spent_usd + estimated_cost) > limit:
        raise AIBudgetExceededError(
            f"AI budget exhausted: ${_budget_spent_usd:.4f} spent, "
            f"limit ${limit:.2f}"
        )


def _record_cost(cost: float) -> None:
    global _budget_spent_usd
    _budget_spent_usd += cost
    logger.info("ai.cost_recorded", cost_usd=cost, total_usd=_budget_spent_usd)


# ---------------------------------------------------------------------------
# Provider dispatch
# ---------------------------------------------------------------------------

async def ai_extract(
    system_prompt: str,
    user_content: str,
    *,
    model: str | None = None,
    max_tokens: int = 2048,
    temperature: float = 0.0,
) -> dict:
    """
    Send a structured-extraction prompt and return parsed JSON dict.
    Used by inbox/meetings/drafts extraction modules.
    """
    raw = await _call_llm(
        system_prompt=system_prompt,
        user_content=user_content,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return _parse_json(raw)


async def ai_generate(
    system_prompt: str,
    user_content: str,
    *,
    model: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """
    General text generation — returns raw string.
    Used for draft reply / follow-up composition.
    """
    return await _call_llm(
        system_prompt=system_prompt,
        user_content=user_content,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )


# ---------------------------------------------------------------------------
# LLM call router
# ---------------------------------------------------------------------------

async def _call_llm(
    system_prompt: str,
    user_content: str,
    *,
    model: str | None,
    max_tokens: int,
    temperature: float,
) -> str:
    provider = settings.ai_provider  # "openai" | "anthropic"
    _check_budget(estimated_cost=0.005)  # conservative per-call estimate

    if provider == "openai":
        text = await _call_openai(
            system_prompt, user_content,
            model=model or settings.ai_openai_model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    elif provider == "anthropic":
        text = await _call_anthropic(
            system_prompt, user_content,
            model=model or settings.ai_anthropic_model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    elif provider == "gemini":
        text = await _call_gemini(
            system_prompt, user_content,
            model=model or settings.ai_gemini_model,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unknown AI provider: {provider}")

    _record_cost(0.003)  # placeholder; replace with token-based calc
    return text


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------

async def _call_openai(
    system_prompt: str,
    user_content: str,
    *,
    model: str,
    max_tokens: int,
    temperature: float,
) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.ai_openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Anthropic
# ---------------------------------------------------------------------------

async def _call_anthropic(
    system_prompt: str,
    user_content: str,
    *,
    model: str,
    max_tokens: int,
    temperature: float,
) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": settings.ai_anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_content}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    return data["content"][0]["text"]


# ---------------------------------------------------------------------------
# Google Gemini
# ---------------------------------------------------------------------------

async def _call_gemini(
    system_prompt: str,
    user_content: str,
    *,
    model: str,
    max_tokens: int,
    temperature: float,
) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={settings.ai_gemini_api_key}"
    )
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\n{user_content}"}],
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    _retries = 3
    _delay = 5.0  # seconds, doubles on each retry
    async with httpx.AsyncClient(timeout=60) as client:
        for attempt in range(_retries):
            resp = await client.post(url, json=payload)
            if resp.status_code == 429 and attempt < _retries - 1:
                wait = _delay * (2 ** attempt)
                logger.warning(
                    "ai.gemini_rate_limited",
                    attempt=attempt + 1,
                    retry_after_s=wait,
                )
                await asyncio.sleep(wait)
                continue
            resp.raise_for_status()
            break
        data = resp.json()

    return data["candidates"][0]["content"]["parts"][0]["text"]


# ---------------------------------------------------------------------------
# JSON parsing helper
# ---------------------------------------------------------------------------

def _parse_json(raw: str) -> dict:
    """
    Parse JSON from LLM output, tolerating markdown fences.
    """
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("ai.json_parse_failed", raw_length=len(raw))
        return {"raw": raw, "_parse_error": True}

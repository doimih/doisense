"""
AI Router: chooses between GPT-5 Mini and Claude.
Uses OpenAI and Anthropic clients; model names can be overridden via env.
"""
import hashlib
import os
from django.conf import settings

from .models import AILog
from core.system_config import get_system_config


def _hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:64]


def _log_call(user_id, model: str, prompt: str):
    AILog.objects.create(
        user_id=user_id,
        model=model,
        prompt_hash=_hash_prompt(prompt),
    )


def complete(prompt: str, system: str | None = None, user_id=None, max_tokens: int | None = None) -> str:
    """
    Send prompt to AI and return reply text.
    Prefer OpenAI (GPT) if key is set, else Anthropic (Claude).
    """
    config = get_system_config()
    provider = (config.ai_provider or "auto").strip().lower()

    openai_key = (
        config.ai_openai_api_key
        or getattr(settings, "OPENAI_API_KEY", "")
        or os.environ.get("OPENAI_API_KEY")
    )
    anthropic_key = (
        config.ai_anthropic_api_key
        or getattr(settings, "ANTHROPIC_API_KEY", "")
        or os.environ.get("ANTHROPIC_API_KEY")
    )

    if provider == "openai":
        if not openai_key:
            return "[AI not configured. Set OpenAI API key in Admin or OPENAI_API_KEY.]"
        return _complete_openai(prompt, system=system, user_id=user_id, api_key=openai_key, max_tokens=max_tokens)
    if provider == "anthropic":
        if not anthropic_key:
            return "[AI not configured. Set Anthropic API key in Admin or ANTHROPIC_API_KEY.]"
        return _complete_anthropic(
            prompt,
            system=system,
            user_id=user_id,
            api_key=anthropic_key,
            max_tokens=max_tokens,
        )

    if openai_key:
        return _complete_openai(prompt, system=system, user_id=user_id, api_key=openai_key, max_tokens=max_tokens)
    if anthropic_key:
        return _complete_anthropic(
            prompt,
            system=system,
            user_id=user_id,
            api_key=anthropic_key,
            max_tokens=max_tokens,
        )
    return "[AI not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.]"


def _complete_openai(prompt: str, system: str | None = None, user_id=None, api_key: str = "", max_tokens: int | None = None) -> str:
    try:
        from openai import OpenAI

        config = get_system_config()
        model = config.ai_openai_model or os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        client = OpenAI(api_key=api_key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens or 1024,
        )
        text = (resp.choices[0].message.content or "").strip()
        _log_call(user_id, "openai", prompt)
        return text
    except Exception as e:
        return f"[OpenAI error: {e}]"


def _complete_anthropic(prompt: str, system: str | None = None, user_id=None, api_key: str = "", max_tokens: int | None = None) -> str:
    try:
        from anthropic import Anthropic

        config = get_system_config()
        model = config.ai_anthropic_model or "claude-3-5-haiku-20241022"
        client = Anthropic(api_key=api_key)
        kwargs = {
            "model": model,
            "max_tokens": max_tokens or 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        resp = client.messages.create(**kwargs)
        text = (resp.content[0].text if resp.content else "").strip()
        _log_call(user_id, "anthropic", prompt)
        return text
    except Exception as e:
        return f"[Anthropic error: {e}]"

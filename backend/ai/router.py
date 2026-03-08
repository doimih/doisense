"""
AI Router: chooses between GPT-5 Mini and Claude.
Uses OpenAI and Anthropic clients; model names can be overridden via env.
"""
import hashlib
import os
from django.conf import settings

from .models import AILog


def _hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:64]


def _log_call(user_id, model: str, prompt: str):
    AILog.objects.create(
        user_id=user_id,
        model=model,
        prompt_hash=_hash_prompt(prompt),
    )


def complete(prompt: str, system: str | None = None, user_id=None) -> str:
    """
    Send prompt to AI and return reply text.
    Prefer OpenAI (GPT) if key is set, else Anthropic (Claude).
    """
    openai_key = getattr(settings, "OPENAI_API_KEY", "") or os.environ.get("OPENAI_API_KEY")
    anthropic_key = getattr(settings, "ANTHROPIC_API_KEY", "") or os.environ.get("ANTHROPIC_API_KEY")

    if openai_key:
        return _complete_openai(prompt, system=system, user_id=user_id)
    if anthropic_key:
        return _complete_anthropic(prompt, system=system, user_id=user_id)
    return "[AI not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.]"


def _complete_openai(prompt: str, system: str | None = None, user_id=None) -> str:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY"))
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model=os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            messages=messages,
            max_tokens=1024,
        )
        text = (resp.choices[0].message.content or "").strip()
        _log_call(user_id, "openai", prompt)
        return text
    except Exception as e:
        return f"[OpenAI error: {e}]"


def _complete_anthropic(prompt: str, system: str | None = None, user_id=None) -> str:
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY or os.environ.get("ANTHROPIC_API_KEY"))
        kwargs = {"model": "claude-3-5-haiku-20241022", "max_tokens": 1024, "messages": [{"role": "user", "content": prompt}]}
        if system:
            kwargs["system"] = system
        resp = client.messages.create(**kwargs)
        text = (resp.content[0].text if resp.content else "").strip()
        _log_call(user_id, "anthropic", prompt)
        return text
    except Exception as e:
        return f"[Anthropic error: {e}]"

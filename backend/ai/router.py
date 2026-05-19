"""
AI Router: chooses between GPT-5 Mini and Claude.
Uses OpenAI and Anthropic clients; model names can be overridden via env.
"""

import hashlib
import os
import re
import time
from collections.abc import Iterator
from decimal import Decimal, InvalidOperation
from django.conf import settings

from .models import AILog
from core.system_config import get_system_config


_COMPLEXITY_HINTS = (
    "analyze",
    "analysis",
    "compare",
    "strategy",
    "roadmap",
    "plan",
    "weekly",
    "monthly",
    "report",
    "long-term",
    "deep",
    "diagnos",
    "therapy",
)


def _get_generation_params(provider: str, max_tokens: int | None) -> dict:
    """
    Speed-focused defaults that can be overridden from Django settings.
    """
    optimized_max_tokens = _optimize_max_tokens(max_tokens)
    if provider == "openai":
        return {
            "max_tokens": optimized_max_tokens,
            "temperature": float(getattr(settings, "AI_OPENAI_TEMPERATURE", 0.2)),
            "top_p": float(getattr(settings, "AI_OPENAI_TOP_P", 0.9)),
            "presence_penalty": float(getattr(settings, "AI_OPENAI_PRESENCE_PENALTY", 0.0)),
            "frequency_penalty": float(getattr(settings, "AI_OPENAI_FREQUENCY_PENALTY", 0.0)),
        }
    if provider == "anthropic":
        return {
            "max_tokens": optimized_max_tokens,
            "temperature": float(getattr(settings, "AI_ANTHROPIC_TEMPERATURE", 0.2)),
            "top_p": float(getattr(settings, "AI_ANTHROPIC_TOP_P", 0.9)),
        }
    return {"max_tokens": optimized_max_tokens}


def _optimize_max_tokens(max_tokens: int | None) -> int:
    configured_default = int(getattr(settings, "AI_DEFAULT_MAX_TOKENS", 768))
    speed_cap = int(getattr(settings, "AI_SPEED_MAX_TOKENS_CAP", 700))
    raw = max_tokens or configured_default
    return max(128, min(raw, speed_cap))


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def _extract_current_message(prompt: str) -> str:
    marker = "Current user message:\n"
    if marker in prompt:
        return prompt.rsplit(marker, 1)[-1].strip()
    return prompt.strip()


def _is_complex_request(prompt: str, max_tokens: int | None = None) -> bool:
    current = _extract_current_message(prompt)
    lowered = current.lower()
    words = re.findall(r"\w+", current)

    complex_max_tokens_threshold = int(os.environ.get("OPENAI_COMPLEX_MAX_TOKENS_THRESHOLD", "700"))
    complex_chars_threshold = int(os.environ.get("OPENAI_COMPLEX_CHARS_THRESHOLD", "480"))
    complex_words_threshold = int(os.environ.get("OPENAI_COMPLEX_WORDS_THRESHOLD", "90"))

    if max_tokens and max_tokens >= complex_max_tokens_threshold:
        return True
    if len(current) >= complex_chars_threshold or len(words) >= complex_words_threshold:
        return True
    if current.count("\n") >= 4:
        return True
    return any(hint in lowered for hint in _COMPLEXITY_HINTS)


def _select_openai_model(configured_model: str, prompt: str, max_tokens: int | None = None) -> str:
    default_model = (configured_model or os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")).strip()
    cheap_model = (os.environ.get("OPENAI_CHAT_MODEL_CHEAP", "gpt-4.1-nano")).strip()
    cost_aware_enabled = _env_bool("OPENAI_COST_AWARE_ROUTING", default=True)

    if not cost_aware_enabled or not cheap_model or cheap_model == default_model:
        return default_model
    if _is_complex_request(prompt, max_tokens=max_tokens):
        return default_model
    return cheap_model


def _hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:64]


def _is_timeout_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "timeout" in message or "timed out" in message


def _safe_provider_error(provider_name: str, exc: Exception) -> str:
    if _is_timeout_error(exc):
        return f"[{provider_name} error: upstream timeout]"
    return f"[{provider_name} error: upstream request failed]"


def _log_monitoring_event(
    *,
    provider: str,
    model: str,
    prompt: str,
    latency_ms: int,
    status: str,
    response_text: str = "",
    error: Exception | None = None,
) -> None:
    try:
        from ai_core.monitoring import log_ai_request_event

        log_ai_request_event(
            provider=provider,
            model=model,
            prompt_hash=_hash_prompt(prompt),
            latency_ms=latency_ms,
            status=status,
            response_text=response_text,
            error_type=type(error).__name__ if error else "",
            error_message=str(error) if error else "",
            timeout=_is_timeout_error(error) if error else False,
        )
    except Exception:
        # Monitoring should never interrupt primary AI flow.
        return


def _log_call(user_id, model: str, prompt: str):
    AILog.objects.create(
        user_id=user_id,
        provider="unknown",
        model=model,
        prompt_hash=_hash_prompt(prompt),
    )


def _parse_model_price_overrides(raw: str) -> dict[str, tuple[Decimal, Decimal]]:
    """Parse overrides format: model:input,output;model2:input,output"""
    result: dict[str, tuple[Decimal, Decimal]] = {}
    for item in (raw or "").split(";"):
        item = item.strip()
        if not item or ":" not in item:
            continue
        model_name, values = item.split(":", 1)
        parts = [p.strip() for p in values.split(",")]
        if len(parts) != 2:
            continue
        try:
            result[model_name.strip()] = (Decimal(parts[0]), Decimal(parts[1]))
        except (InvalidOperation, ValueError):
            continue
    return result


def _get_provider_default_pricing(provider: str) -> tuple[Decimal, Decimal]:
    if provider == "openai":
        in_rate = Decimal(os.environ.get("OPENAI_DEFAULT_INPUT_COST_PER_MTOK", "0.25"))
        out_rate = Decimal(os.environ.get("OPENAI_DEFAULT_OUTPUT_COST_PER_MTOK", "2.00"))
        return in_rate, out_rate
    if provider == "anthropic":
        in_rate = Decimal(os.environ.get("ANTHROPIC_DEFAULT_INPUT_COST_PER_MTOK", "0.80"))
        out_rate = Decimal(os.environ.get("ANTHROPIC_DEFAULT_OUTPUT_COST_PER_MTOK", "4.00"))
        return in_rate, out_rate
    return Decimal("0"), Decimal("0")


def _estimate_cost_usd(
    provider: str, model: str, input_tokens: int | None, output_tokens: int | None
) -> Decimal | None:
    if input_tokens is None and output_tokens is None:
        return None

    overrides = _parse_model_price_overrides(os.environ.get("AI_MODEL_PRICE_OVERRIDES", ""))
    in_rate, out_rate = overrides.get(model, _get_provider_default_pricing(provider))

    in_tokens = Decimal(input_tokens or 0)
    out_tokens = Decimal(output_tokens or 0)
    cost = (in_tokens / Decimal(1_000_000)) * in_rate + (out_tokens / Decimal(1_000_000)) * out_rate
    return cost.quantize(Decimal("0.000001"))


def _log_call_with_usage(
    user_id,
    provider: str,
    model: str,
    prompt: str,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
):
    AILog.objects.create(
        user_id=user_id,
        provider=provider,
        model=model,
        prompt_hash=_hash_prompt(prompt),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=_estimate_cost_usd(provider, model, input_tokens, output_tokens),
    )


def complete(
    prompt: str, system: str | None = None, user_id=None, max_tokens: int | None = None
) -> str:
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
        return _complete_openai(
            prompt, system=system, user_id=user_id, api_key=openai_key, max_tokens=max_tokens
        )
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
        openai_result = _complete_openai(
            prompt, system=system, user_id=user_id, api_key=openai_key, max_tokens=max_tokens
        )
        # In auto mode, fall back to Anthropic if OpenAI is configured but currently failing (e.g., quota/outage).
        if not openai_result.startswith("[OpenAI error:"):
            return openai_result
    if anthropic_key:
        anthropic_result = _complete_anthropic(
            prompt,
            system=system,
            user_id=user_id,
            api_key=anthropic_key,
            max_tokens=max_tokens,
        )
        if not anthropic_result.startswith("[Anthropic error:"):
            return anthropic_result
        if openai_key:
            return openai_result
        return anthropic_result
    if openai_key:
        return openai_result
    return "[AI not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.]"


def complete_stream(
    prompt: str, system: str | None = None, user_id=None, max_tokens: int | None = None
) -> Iterator[str]:
    """
    Stream AI reply tokens. Falls back safely to complete() if stream APIs fail.
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
            yield "[AI not configured. Set OpenAI API key in Admin or OPENAI_API_KEY.]"
            return
        openai_streamed = False
        for token in _complete_openai_stream(
            prompt, system=system, user_id=user_id, api_key=openai_key, max_tokens=max_tokens
        ):
            openai_streamed = True
            yield token
        if openai_streamed:
            return
        if anthropic_key:
            anthropic_streamed = False
            for token in _complete_anthropic_stream(
                prompt,
                system=system,
                user_id=user_id,
                api_key=anthropic_key,
                max_tokens=max_tokens,
            ):
                anthropic_streamed = True
                yield token
            if anthropic_streamed:
                return
        yield complete(prompt=prompt, system=system, user_id=user_id, max_tokens=max_tokens)
        return

    if provider == "anthropic":
        if not anthropic_key:
            yield "[AI not configured. Set Anthropic API key in Admin or ANTHROPIC_API_KEY.]"
            return
        anthropic_streamed = False
        for token in _complete_anthropic_stream(
            prompt,
            system=system,
            user_id=user_id,
            api_key=anthropic_key,
            max_tokens=max_tokens,
        ):
            anthropic_streamed = True
            yield token
        if anthropic_streamed:
            return
        if openai_key:
            openai_streamed = False
            for token in _complete_openai_stream(
                prompt, system=system, user_id=user_id, api_key=openai_key, max_tokens=max_tokens
            ):
                openai_streamed = True
                yield token
            if openai_streamed:
                return
        yield complete(prompt=prompt, system=system, user_id=user_id, max_tokens=max_tokens)
        return

    if openai_key:
        openai_streamed = False
        for token in _complete_openai_stream(
            prompt, system=system, user_id=user_id, api_key=openai_key, max_tokens=max_tokens
        ):
            openai_streamed = True
            yield token
        if openai_streamed:
            return

    if anthropic_key:
        anthropic_streamed = False
        for token in _complete_anthropic_stream(
            prompt,
            system=system,
            user_id=user_id,
            api_key=anthropic_key,
            max_tokens=max_tokens,
        ):
            anthropic_streamed = True
            yield token
        if anthropic_streamed:
            return

    # Safe fallback to sync path as a single chunk.
    yield complete(prompt=prompt, system=system, user_id=user_id, max_tokens=max_tokens)


def _complete_openai(
    prompt: str,
    system: str | None = None,
    user_id=None,
    api_key: str = "",
    max_tokens: int | None = None,
) -> str:
    started_at = time.perf_counter()
    model = "unknown"
    try:
        from openai import OpenAI

        config = get_system_config()
        model = _select_openai_model(config.ai_openai_model, prompt, max_tokens=max_tokens)
        gen_params = _get_generation_params("openai", max_tokens=max_tokens)
        client = OpenAI(api_key=api_key)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=gen_params["max_tokens"],
            temperature=gen_params["temperature"],
            top_p=gen_params["top_p"],
            presence_penalty=gen_params["presence_penalty"],
            frequency_penalty=gen_params["frequency_penalty"],
        )
        usage = getattr(resp, "usage", None)
        input_tokens = getattr(usage, "prompt_tokens", None) if usage else None
        output_tokens = getattr(usage, "completion_tokens", None) if usage else None
        text = (resp.choices[0].message.content or "").strip()
        _log_call_with_usage(
            user_id=user_id,
            provider="openai",
            model=model,
            prompt=prompt,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        _log_monitoring_event(
            provider="openai",
            model=model,
            prompt=prompt,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
            status="ok",
            response_text=text,
        )
        return text
    except Exception as e:
        _log_monitoring_event(
            provider="openai",
            model=model,
            prompt=prompt,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
            status="timeout" if _is_timeout_error(e) else "error",
            error=e,
        )
        return _safe_provider_error("OpenAI", e)


def _complete_anthropic(
    prompt: str,
    system: str | None = None,
    user_id=None,
    api_key: str = "",
    max_tokens: int | None = None,
) -> str:
    started_at = time.perf_counter()
    model = "unknown"
    try:
        from anthropic import Anthropic

        config = get_system_config()
        model = config.ai_anthropic_model or "claude-3-5-haiku-20241022"
        gen_params = _get_generation_params("anthropic", max_tokens=max_tokens)
        client = Anthropic(api_key=api_key)
        kwargs = {
            "model": model,
            "max_tokens": gen_params["max_tokens"],
            "temperature": gen_params["temperature"],
            "top_p": gen_params["top_p"],
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        resp = client.messages.create(**kwargs)
        usage = getattr(resp, "usage", None)
        input_tokens = getattr(usage, "input_tokens", None) if usage else None
        output_tokens = getattr(usage, "output_tokens", None) if usage else None
        text = (resp.content[0].text if resp.content else "").strip()
        _log_call_with_usage(
            user_id=user_id,
            provider="anthropic",
            model=model,
            prompt=prompt,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
        _log_monitoring_event(
            provider="anthropic",
            model=model,
            prompt=prompt,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
            status="ok",
            response_text=text,
        )
        return text
    except Exception as e:
        _log_monitoring_event(
            provider="anthropic",
            model=model,
            prompt=prompt,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
            status="timeout" if _is_timeout_error(e) else "error",
            error=e,
        )
        return _safe_provider_error("Anthropic", e)


def _complete_openai_stream(
    prompt: str,
    system: str | None = None,
    user_id=None,
    api_key: str = "",
    max_tokens: int | None = None,
) -> Iterator[str]:
    started_at = time.perf_counter()
    from openai import OpenAI

    config = get_system_config()
    model = _select_openai_model(config.ai_openai_model, prompt, max_tokens=max_tokens)
    gen_params = _get_generation_params("openai", max_tokens=max_tokens)
    client = OpenAI(api_key=api_key)

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    chunks: list[str] = []
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=gen_params["max_tokens"],
        temperature=gen_params["temperature"],
        top_p=gen_params["top_p"],
        presence_penalty=gen_params["presence_penalty"],
        frequency_penalty=gen_params["frequency_penalty"],
        stream=True,
    )
    try:
        for chunk in stream:
            token = (chunk.choices[0].delta.content or "") if chunk.choices else ""
            if token:
                chunks.append(token)
                yield token

        text = "".join(chunks)
        _log_call_with_usage(
            user_id=user_id,
            provider="openai",
            model=model,
            prompt=prompt,
            input_tokens=None,
            output_tokens=None,
        )
        _log_monitoring_event(
            provider="openai",
            model=model,
            prompt=prompt,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
            status="ok",
            response_text=text,
        )
    except Exception as e:
        _log_monitoring_event(
            provider="openai",
            model=model,
            prompt=prompt,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
            status="timeout" if _is_timeout_error(e) else "error",
            error=e,
        )
        return


def _complete_anthropic_stream(
    prompt: str,
    system: str | None = None,
    user_id=None,
    api_key: str = "",
    max_tokens: int | None = None,
) -> Iterator[str]:
    started_at = time.perf_counter()
    from anthropic import Anthropic

    config = get_system_config()
    model = config.ai_anthropic_model or "claude-3-5-haiku-20241022"
    gen_params = _get_generation_params("anthropic", max_tokens=max_tokens)
    client = Anthropic(api_key=api_key)

    kwargs = {
        "model": model,
        "max_tokens": gen_params["max_tokens"],
        "temperature": gen_params["temperature"],
        "top_p": gen_params["top_p"],
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    chunks: list[str] = []
    try:
        with client.messages.stream(**kwargs) as stream:
            for token in stream.text_stream:
                if token:
                    chunks.append(token)
                    yield token

        text = "".join(chunks)
        _log_call_with_usage(
            user_id=user_id,
            provider="anthropic",
            model=model,
            prompt=prompt,
            input_tokens=None,
            output_tokens=None,
        )
        _log_monitoring_event(
            provider="anthropic",
            model=model,
            prompt=prompt,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
            status="ok",
            response_text=text,
        )
    except Exception as e:
        _log_monitoring_event(
            provider="anthropic",
            model=model,
            prompt=prompt,
            latency_ms=int((time.perf_counter() - started_at) * 1000),
            status="timeout" if _is_timeout_error(e) else "error",
            error=e,
        )
        return

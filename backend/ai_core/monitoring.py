from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from time import time

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q

from core.models import AdminAuditLog, SystemErrorEvent

from .models import PromptVersion


_EVENTS_CACHE_KEY = "ai_core:monitoring:events"


def _events_limit() -> int:
    return int(getattr(settings, "AI_MONITORING_EVENTS_LIMIT", 600))


def _events_cache_ttl_seconds() -> int:
    return int(getattr(settings, "AI_MONITORING_EVENTS_TTL_SECONDS", 60 * 60 * 24))


def _latency_spike_ms_threshold() -> int:
    return int(getattr(settings, "AI_MONITORING_LATENCY_SPIKE_MS", 3500))


def _long_response_chars_threshold() -> int:
    return int(getattr(settings, "AI_MONITORING_LONG_RESPONSE_CHARS", 3500))


def log_ai_request_event(
    *,
    provider: str,
    model: str,
    prompt_hash: str,
    latency_ms: int | None,
    status: str,
    response_text: str = "",
    error_type: str = "",
    error_message: str = "",
    timeout: bool = False,
) -> None:
    """
    Store lightweight request telemetry in cache.
    This is additive and never blocks normal AI request flow.
    """
    event = {
        "timestamp": time(),
        "provider": (provider or "unknown")[:64],
        "model": (model or "unknown")[:128],
        "prompt_hash": (prompt_hash or "")[:64],
        "latency_ms": int(latency_ms or 0),
        "status": (status or "ok")[:32],
        "response_length": len((response_text or "").strip()),
        "error_type": (error_type or "")[:128],
        "error_message": (error_message or "")[:500],
        "timeout": bool(timeout),
    }

    try:
        events = cache.get(_EVENTS_CACHE_KEY) or []
        events.append(event)
        if len(events) > _events_limit():
            events = events[-_events_limit():]
        cache.set(_EVENTS_CACHE_KEY, events, timeout=_events_cache_ttl_seconds())
    except Exception:
        # Monitoring must never break production request flow.
        return


def _recent_events(hours: int = 24) -> list[dict]:
    events = cache.get(_EVENTS_CACHE_KEY) or []
    if not events:
        return []
    min_ts = time() - (hours * 3600)
    return [event for event in events if float(event.get("timestamp", 0)) >= min_ts]


def compute_aggregated_metrics(hours: int = 24) -> dict:
    """
    Compute top-level AI health metrics used by admin dashboard.
    """
    events = _recent_events(hours=hours)
    total_requests = len(events)
    if total_requests == 0:
        return {
            "window_hours": hours,
            "total_requests": 0,
            "avg_latency_ms": 0,
            "max_latency_ms": 0,
            "p95_latency_ms": 0,
            "error_count": 0,
            "timeout_count": 0,
            "error_rate": 0.0,
        }

    latencies = [
        int(event.get("latency_ms", 0))
        for event in events
        if event.get("status") == "ok" and int(event.get("latency_ms", 0)) > 0
    ]
    latencies_sorted = sorted(latencies)
    p95_index = int(0.95 * (len(latencies_sorted) - 1)) if latencies_sorted else 0

    error_count = sum(1 for event in events if event.get("status") in {"error", "timeout"})
    timeout_count = sum(1 for event in events if bool(event.get("timeout")))
    error_rate = round((error_count / total_requests) * 100, 2)

    return {
        "window_hours": hours,
        "total_requests": total_requests,
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0,
        "max_latency_ms": max(latencies) if latencies else 0,
        "p95_latency_ms": latencies_sorted[p95_index] if latencies_sorted else 0,
        "error_count": error_count,
        "timeout_count": timeout_count,
        "error_rate": error_rate,
    }


def detect_anomalies(hours: int = 24) -> list[dict]:
    """
    Detect notable anomalies:
    - latency spikes
    - empty AI responses
    - unusually long AI responses
    """
    events = _recent_events(hours=hours)
    metrics = compute_aggregated_metrics(hours=hours)

    anomalies: list[dict] = []
    dynamic_spike_threshold = int(float(metrics.get("avg_latency_ms") or 0) * 2.5)
    spike_threshold = max(_latency_spike_ms_threshold(), dynamic_spike_threshold)
    long_threshold = _long_response_chars_threshold()

    for event in events:
        latency_ms = int(event.get("latency_ms", 0))
        response_length = int(event.get("response_length", 0))
        status = event.get("status", "ok")
        occurred_at = datetime.fromtimestamp(
            float(event.get("timestamp", 0)), tz=dt_timezone.utc
        )

        if status == "ok" and latency_ms > spike_threshold:
            anomalies.append(
                {
                    "kind": "latency_spike",
                    "severity": "warning",
                    "message": f"Latency spike detected ({latency_ms} ms).",
                    "occurred_at": occurred_at,
                }
            )

        if status == "ok" and response_length == 0:
            anomalies.append(
                {
                    "kind": "empty_response",
                    "severity": "critical",
                    "message": "AI returned an empty response.",
                    "occurred_at": occurred_at,
                }
            )

        if status == "ok" and response_length > long_threshold:
            anomalies.append(
                {
                    "kind": "long_response",
                    "severity": "warning",
                    "message": f"Unusually long response ({response_length} chars).",
                    "occurred_at": occurred_at,
                }
            )

    return sorted(anomalies, key=lambda item: item["occurred_at"], reverse=True)[:30]


def fetch_recent_prompt_audits_and_modifications(limit: int = 10) -> dict:
    recent_audits = list(
        AdminAuditLog.objects.select_related("actor")
        .filter(
            target_model="ai_core.prompt",
            action__in=[
                "ai_brain_prompt_audited",
                "ai_brain_prompt_updated",
                "ai_brain_prompt_improved",
            ],
        )
        .order_by("-created_at")[:limit]
    )

    recent_prompt_edits = list(
        PromptVersion.objects.select_related("prompt").order_by("-updated_at", "-version_number")[:limit]
    )

    return {
        "recent_audits": recent_audits,
        "recent_prompt_edits": recent_prompt_edits,
    }


def _fetch_recent_error_logs(limit: int = 15) -> list[dict]:
    events = _recent_events(hours=24)
    event_errors = [
        {
            "source": "ai_request",
            "created_at": datetime.fromtimestamp(float(event.get("timestamp", 0)), tz=dt_timezone.utc),
            "provider": event.get("provider", "unknown"),
            "model": event.get("model", "unknown"),
            "error_type": event.get("error_type") or ("Timeout" if event.get("timeout") else "RequestError"),
            "message": event.get("error_message") or "AI request failed.",
        }
        for event in events
        if event.get("status") in {"error", "timeout"}
    ]

    system_errors = [
        {
            "source": "system_error",
            "created_at": error.created_at,
            "provider": "n/a",
            "model": "n/a",
            "error_type": error.error_type or "SystemError",
            "message": error.message or "No message provided.",
        }
        for error in SystemErrorEvent.objects.filter(
            Q(component__istartswith="ai") | Q(component__istartswith="ai_core")
        )
        .order_by("-created_at")[:limit]
    ]

    combined = sorted(event_errors + system_errors, key=lambda item: item["created_at"], reverse=True)
    return combined[:limit]


def _orchestrator_health() -> dict:
    cache_version = cache.get("ai_core:orchestrator:version")
    return {
        "cache_version": cache_version,
        "cache_ttl_seconds": int(getattr(settings, "AI_ORCHESTRATOR_CACHE_TTL_SECONDS", 300)),
        "max_history_turns": int(getattr(settings, "AI_PROMPT_MAX_HISTORY_TURNS", 4)),
        "max_context_chars": int(getattr(settings, "AI_PROMPT_MAX_CONTEXT_CHARS", 1600)),
        "max_message_chars": int(getattr(settings, "AI_PROMPT_MAX_MESSAGE_CHARS", 2000)),
        "status": "warm" if cache_version else "cold",
    }


def _cache_status() -> dict:
    backend_name = (
        settings.CACHES.get("default", {})
        .get("BACKEND", "unknown")
        .rsplit(".", 1)[-1]
    )
    return {
        "backend": backend_name,
        "events_cached": len(cache.get(_EVENTS_CACHE_KEY) or []),
    }


def _summary_status(metrics: dict, anomalies: list[dict]) -> str:
    if metrics.get("error_rate", 0) >= 15 or metrics.get("timeout_count", 0) >= 5:
        return "critical"
    if metrics.get("error_rate", 0) >= 5 or anomalies:
        return "warning"
    return "healthy"


def build_ai_health_dashboard_context(hours: int = 24) -> dict:
    metrics = compute_aggregated_metrics(hours=hours)
    anomalies = detect_anomalies(hours=hours)
    prompt_activity = fetch_recent_prompt_audits_and_modifications(limit=10)
    orchestrator = _orchestrator_health()

    return {
        "dashboard_window_hours": hours,
        "metrics": metrics,
        "anomalies": anomalies,
        "error_logs": _fetch_recent_error_logs(limit=15),
        "recent_audits": prompt_activity["recent_audits"],
        "recent_prompt_edits": prompt_activity["recent_prompt_edits"],
        "orchestrator": orchestrator,
        "cache_status": _cache_status(),
        "system_status": _summary_status(metrics, anomalies),
    }
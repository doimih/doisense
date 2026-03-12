import json
from urllib import request as urlrequest

from django.conf import settings

from .models import AnalyticsEvent


EVENT_SCHEMA = {
    "user_registered": ["auth_method"],
    "user_activated": ["auth_method"],
    "onboarding_started": ["tier_variant"],
    "onboarding_step_completed": ["step_key", "step_index", "tier_variant"],
    "onboarding_profile_saved": ["has_journal", "tier_variant"],
    "onboarding_completed": ["tier_variant"],
    "onboarding_restarted": ["entrypoint"],
    "chat_message_sent": ["module"],
    "journal_entry_created": ["question_id"],
    "program_day_completed": ["program_id", "day_number"],
    "program_completed": ["program_id", "day_number"],
    "program_paused": ["program_id", "day_number"],
    "program_resumed": ["program_id", "day_number"],
    "program_reflection_submitted": ["program_id", "day_number"],
    "program_dropout_detected": ["program_id", "day_number"],
    "checkout_initiated": ["plan_tier"],
    "subscription_change_requested": ["plan_tier"],
    "subscription_cancel_requested": ["plan_tier"],
    "subscription_refunded": ["plan_tier"],
    "support_ticket_created": [],
    "feature_access_checked": ["feature_key", "granted"],
    "quota_exceeded": ["metric_key"],
}


def _safe_properties(event_name: str, properties: dict | None) -> dict:
    data = properties or {}
    allowed_keys = set(EVENT_SCHEMA.get(event_name, []))
    if not allowed_keys:
        return data
    return {key: value for key, value in data.items() if key in allowed_keys}


def _send_to_posthog(event_name: str, distinct_id: str, properties: dict):
    api_key = getattr(settings, "POSTHOG_API_KEY", "")
    host = getattr(settings, "POSTHOG_HOST", "https://app.posthog.com").rstrip("/")
    if not api_key:
        return

    payload = {
        "api_key": api_key,
        "event": event_name,
        "distinct_id": distinct_id,
        "properties": properties,
    }

    req = urlrequest.Request(
        f"{host}/capture/",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=2):
            return
    except Exception:
        return


def track_event(
    event_name: str,
    *,
    source: str = "backend",
    user=None,
    session_id: str = "",
    properties: dict | None = None,
):
    filtered_properties = _safe_properties(event_name, properties)

    event = AnalyticsEvent.objects.create(
        event_name=event_name,
        source=source,
        user=user if getattr(user, "is_authenticated", False) else None,
        session_id=session_id,
        properties=filtered_properties,
    )

    distinct_id = str(getattr(user, "id", "anonymous") or "anonymous")
    _send_to_posthog(event_name, distinct_id, filtered_properties)

    return event

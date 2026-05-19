import json
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone

from ai.models import Conversation, DailyReport, MonthlyReport, WeeklyReport
from ai.router import complete
from journal.models import JournalEntry

User = get_user_model()

DAILY_ALLOWED_TIERS = {"trial", "premium", "vip"}
WEEKLY_ALLOWED_TIERS = {"trial", "premium", "vip"}
MONTHLY_ALLOWED_TIERS = {"vip"}


@dataclass
class ReportStats:
    processed: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0


def _user_tier(user) -> str:
    return (getattr(user, "effective_plan_tier", lambda: "free")() or "free").strip().lower()


def _get_period_daily(target_day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(target_day, datetime.min.time())
    end = start + timedelta(days=1)
    return timezone.make_aware(start), timezone.make_aware(end)


def _get_period_weekly(target_day: date) -> tuple[datetime, datetime, date]:
    week_start = target_day - timedelta(days=target_day.weekday())
    start = datetime.combine(week_start, datetime.min.time())
    end = start + timedelta(days=7)
    return timezone.make_aware(start), timezone.make_aware(end), week_start


def _get_period_monthly(target_day: date) -> tuple[datetime, datetime, int, int]:
    month_start = target_day.replace(day=1)
    if month_start.month == 12:
        next_month = month_start.replace(year=month_start.year + 1, month=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1)
    start = datetime.combine(month_start, datetime.min.time())
    end = datetime.combine(next_month, datetime.min.time())
    return timezone.make_aware(start), timezone.make_aware(end), month_start.year, month_start.month


def _collect_user_signals(user_id: int, start: datetime, end: datetime) -> dict[str, Any]:
    entries = list(
        JournalEntry.objects.filter(user_id=user_id, created_at__gte=start, created_at__lt=end)
        .order_by("-created_at")
        .values("content", "emotions")[:30]
    )
    conversations_count = Conversation.objects.filter(
        user_id=user_id,
        created_at__gte=start,
        created_at__lt=end,
    ).count()

    emotion_counter: Counter[str] = Counter()
    for row in entries:
        for emo in row.get("emotions") or []:
            val = str(emo).strip().lower()
            if val:
                emotion_counter[val] += 1

    highlights = []
    for row in entries[:3]:
        content = (row.get("content") or "").strip().replace("\n", " ")
        if content:
            highlights.append(content[:180])

    return {
        "journal_count": len(entries),
        "conversation_count": conversations_count,
        "top_emotions": [emo for emo, _ in emotion_counter.most_common(5)],
        "sample_lines": highlights,
    }


def _safe_json_parse(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    raw = text.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _fallback_daily(signals: dict[str, Any]) -> dict[str, Any]:
    summary = (
        f"Daily summary based on {signals['journal_count']} journal entries "
        f"and {signals['conversation_count']} AI conversations."
    )
    recommendations = [
        "Keep a short reflection habit for emotional clarity.",
        "Pick one small wellbeing action for tomorrow.",
    ]
    return {
        "summary": summary,
        "highlights": signals["sample_lines"][:3],
        "challenges": [],
        "recommendations": recommendations,
    }


def _fallback_weekly(signals: dict[str, Any]) -> dict[str, Any]:
    trends = [
        (
            f"Top emotions: {', '.join(signals['top_emotions'])}"
            if signals["top_emotions"]
            else "No strong emotion trend detected."
        ),
        f"Journaling frequency: {signals['journal_count']} entries this week.",
    ]
    return {
        "summary": (
            f"Weekly summary from {signals['journal_count']} journal entries and "
            f"{signals['conversation_count']} AI conversations."
        ),
        "trends": trends,
        "progress": "Steady reflection activity maintained.",
        "recommendations": [
            "Keep consistent journaling on high-stress days.",
            "Review one positive habit to continue next week.",
        ],
    }


def _fallback_monthly(signals: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": (
            f"Monthly summary from {signals['journal_count']} journal entries and "
            f"{signals['conversation_count']} AI conversations."
        ),
        "trends": [
            (
                f"Top emotions this month: {', '.join(signals['top_emotions'])}"
                if signals["top_emotions"]
                else "No dominant emotion pattern."
            ),
        ],
        "insights": "Consistency and emotional awareness can improve with regular reflection.",
        "recommendations": [
            "Set one monthly wellbeing objective and track it weekly.",
            "Discuss recurring challenges with a trusted person if needed.",
        ],
    }


def _build_ai_report(
    user, report_type: str, signals: dict[str, Any], max_tokens: int = 700
) -> dict[str, Any] | None:
    if signals["journal_count"] == 0 and signals["conversation_count"] == 0:
        return None

    if report_type == "daily":
        schema = (
            '{"summary":"...","highlights":["..."],"challenges":["..."],"recommendations":["..."]}'
        )
        goal = "Generate a concise daily wellbeing report"
    elif report_type == "weekly":
        schema = '{"summary":"...","trends":["..."],"progress":"...","recommendations":["..."]}'
        goal = "Generate a concise weekly wellbeing report"
    else:
        schema = '{"summary":"...","trends":["..."],"insights":"...","recommendations":["..."]}'
        goal = "Generate a concise monthly wellbeing report"

    prompt = (
        f"{goal} for this user based on platform signals. "
        "Return ONLY JSON without markdown. Keep text empathetic, practical, and short.\n"
        f"Required JSON schema: {schema}\n"
        f"User language: {(getattr(user, 'language', '') or 'en').strip() or 'en'}\n"
        f"Signals: {json.dumps(signals, ensure_ascii=True)}"
    )

    system = (
        "You are a wellness reporting assistant. "
        "Produce accurate summaries from provided signals only, with no fabricated facts."
    )
    result = complete(prompt, system=system, user_id=user.id, max_tokens=max_tokens)
    parsed = _safe_json_parse(result)
    return parsed


def generate_daily_report_for_user(user, target_day: date | None = None) -> bool:
    day = target_day or timezone.localdate()
    start, end = _get_period_daily(day)
    signals = _collect_user_signals(user.id, start, end)
    parsed = _build_ai_report(user, "daily", signals) or _fallback_daily(signals)

    DailyReport.objects.update_or_create(
        user=user,
        date=day,
        defaults={
            "summary": str(parsed.get("summary") or "").strip(),
            "highlights": (
                parsed.get("highlights") if isinstance(parsed.get("highlights"), list) else []
            ),
            "challenges": (
                parsed.get("challenges") if isinstance(parsed.get("challenges"), list) else []
            ),
            "recommendations": (
                parsed.get("recommendations")
                if isinstance(parsed.get("recommendations"), list)
                else []
            ),
        },
    )
    return True


def generate_weekly_report_for_user(user, target_day: date | None = None) -> bool:
    day = target_day or timezone.localdate()
    start, end, week_start = _get_period_weekly(day)
    signals = _collect_user_signals(user.id, start, end)
    parsed = _build_ai_report(user, "weekly", signals) or _fallback_weekly(signals)

    WeeklyReport.objects.update_or_create(
        user=user,
        week_start=week_start,
        defaults={
            "summary": str(parsed.get("summary") or "").strip(),
            "trends": parsed.get("trends") if isinstance(parsed.get("trends"), list) else [],
            "progress": str(parsed.get("progress") or "").strip(),
            "recommendations": (
                parsed.get("recommendations")
                if isinstance(parsed.get("recommendations"), list)
                else []
            ),
        },
    )
    return True


def generate_monthly_report_for_user(user, target_day: date | None = None) -> bool:
    day = target_day or timezone.localdate()
    start, end, year, month = _get_period_monthly(day)
    signals = _collect_user_signals(user.id, start, end)
    parsed = _build_ai_report(user, "monthly", signals) or _fallback_monthly(signals)

    MonthlyReport.objects.update_or_create(
        user=user,
        year=year,
        month=month,
        defaults={
            "summary": str(parsed.get("summary") or "").strip(),
            "trends": parsed.get("trends") if isinstance(parsed.get("trends"), list) else [],
            "insights": str(parsed.get("insights") or "").strip(),
            "recommendations": (
                parsed.get("recommendations")
                if isinstance(parsed.get("recommendations"), list)
                else []
            ),
        },
    )
    return True


def _iter_eligible_users(allowed_tiers: set[str], user_id: int | None = None):
    qs = User.objects.filter(is_active=True).order_by("id")
    if user_id is not None:
        qs = qs.filter(id=user_id)
    for user in qs.iterator():
        if _user_tier(user) in allowed_tiers:
            yield user


def run_daily_reports_for_all_users(
    target_day: date | None = None, user_id: int | None = None
) -> ReportStats:
    stats = ReportStats()
    for user in _iter_eligible_users(DAILY_ALLOWED_TIERS, user_id=user_id):
        stats.processed += 1
        try:
            generate_daily_report_for_user(user, target_day=target_day)
            stats.updated += 1
        except Exception:
            stats.errors += 1
    return stats


def run_weekly_reports_for_all_users(
    target_day: date | None = None, user_id: int | None = None
) -> ReportStats:
    stats = ReportStats()
    for user in _iter_eligible_users(WEEKLY_ALLOWED_TIERS, user_id=user_id):
        stats.processed += 1
        try:
            generate_weekly_report_for_user(user, target_day=target_day)
            stats.updated += 1
        except Exception:
            stats.errors += 1
    return stats


def run_monthly_reports_for_all_users(
    target_day: date | None = None, user_id: int | None = None
) -> ReportStats:
    stats = ReportStats()
    for user in _iter_eligible_users(MONTHLY_ALLOWED_TIERS, user_id=user_id):
        stats.processed += 1
        try:
            generate_monthly_report_for_user(user, target_day=target_day)
            stats.updated += 1
        except Exception:
            stats.errors += 1
    return stats

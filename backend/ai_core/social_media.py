from __future__ import annotations

import json
import logging
from urllib.parse import quote_plus

from .models import Prompt, SocialMediaPost

logger = logging.getLogger(__name__)


PLATFORM_TONES = {
    SocialMediaPost.PLATFORM_INSTAGRAM: "inspirational, concise, visual-first",
    SocialMediaPost.PLATFORM_TIKTOK: "energetic, short, trend-aware",
    SocialMediaPost.PLATFORM_LINKEDIN: "professional, practical, reflective",
}

WELLNESS_KEYWORDS = {
    "wellness",
    "wellbeing",
    "well-being",
    "mindfulness",
    "sleep",
    "stress",
    "nutrition",
    "movement",
    "fitness",
    "hydration",
    "mental",
    "health",
    "self-care",
    "selfcare",
}


def _global_rules_prompt() -> str:
    prompt = (
        Prompt.objects.filter(type=Prompt.TYPE_RULES, name__icontains="social_media")
        .order_by("-id")
        .first()
    )
    if prompt and prompt.content:
        return prompt.content.strip()
    return (
        "All generated social media content must be wellness-related only. "
        "Adapt tone to the platform. Every post must end with a platform-specific closing line."
    )


def _platform_closing_line(platform: str) -> str:
    endings = {
        SocialMediaPost.PLATFORM_INSTAGRAM: "See you on Instagram for your next wellness step.",
        SocialMediaPost.PLATFORM_TIKTOK: "Follow on TikTok for the next quick wellness reset.",
        SocialMediaPost.PLATFORM_LINKEDIN: "Connect on LinkedIn for more evidence-based wellness insights.",
    }
    return endings.get(platform, "Stay consistent with your wellness journey on this platform.")


def _hashtags_for_topic(topic: str, platform: str) -> str:
    base = ["#Wellness", "#Mindset", "#HealthyHabits"]
    platform_tags = {
        SocialMediaPost.PLATFORM_INSTAGRAM: ["#SelfCare", "#DailyWellness"],
        SocialMediaPost.PLATFORM_TIKTOK: ["#WellnessTips", "#HabitReset"],
        SocialMediaPost.PLATFORM_LINKEDIN: ["#WorkplaceWellness", "#LeadershipWellbeing"],
    }
    topic_tag = f"#{''.join(ch for ch in topic.title() if ch.isalnum())}" if topic else "#Wellbeing"
    tags = base + platform_tags.get(platform, []) + [topic_tag]
    return " ".join(dict.fromkeys(tags))


def _normalize_wellness_topic(topic: str) -> str:
    cleaned = (topic or "daily wellness").strip()
    lowered = cleaned.lower()
    if any(keyword in lowered for keyword in WELLNESS_KEYWORDS):
        return cleaned
    return f"wellness practice: {cleaned}"


def _llm_generate_post(
    topic: str, platform: str, tone: str, rules: str, closing_line: str, hashtags: str
) -> dict | None:
    """
    Ask the LLM to generate a structured wellness post.
    Returns a parsed dict on success, or None on any failure.
    """
    try:
        from ai.router import complete  # Lazy import to avoid circular dependency
    except Exception:
        return None

    body_length_hint = (
        "100-300 characters"
        if platform in (SocialMediaPost.PLATFORM_INSTAGRAM, SocialMediaPost.PLATFORM_TIKTOK)
        else "200-500 characters"
    )

    prompt = (
        f"You are an expert wellness content creator for the Doisense platform.\n"
        f"Platform: {platform}\n"
        f"Tone: {tone}\n"
        f"Wellness topic: {topic}\n"
        f"Content rules: {rules}\n\n"
        f"Generate a social media post for this topic.\n"
        f"Body length: {body_length_hint}.\n"
        f"End the body with exactly this closing line: {closing_line}\n\n"
        f"Return ONLY a raw JSON object with these exact keys (no markdown, no explanation):\n"
        f"  title          - short, engaging (max 80 chars)\n"
        f"  body           - main post text with closing line appended\n"
        f"  hashtags       - space-separated hashtag string\n"
        f"  wellness_topic - normalized wellness topic label\n"
    )
    system = (
        "You are an expert wellness content creator. "
        "Always return a valid raw JSON object and nothing else. "
        "No markdown code fences. No extra explanation."
    )

    try:
        raw = complete(prompt, system=system, max_tokens=600)
    except Exception as exc:
        logger.warning("LLM call failed in social post generation: %s", exc)
        return None

    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

    if cleaned.startswith("["):
        logger.warning("LLM returned provider error for social post: %s", cleaned[:120])
        return None

    try:
        data = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning(
            "LLM response is not valid JSON for social post: %s | raw=%s", exc, cleaned[:200]
        )
        return None

    if not isinstance(data, dict) or not all(k in data for k in ("title", "body", "wellness_topic")):
        logger.warning(
            "LLM response missing required keys for social post: %s",
            list(data.keys()) if isinstance(data, dict) else type(data),
        )
        return None

    return {
        "title": str(data.get("title", ""))[:255].strip(),
        "body": str(data.get("body", "")).strip(),
        "hashtags": str(data.get("hashtags", hashtags)).strip(),
        "wellness_topic": str(data.get("wellness_topic", topic))[:255].strip(),
        "closing_line": closing_line,
    }


def _passes_guardrails(post_data: dict) -> bool:
    """Ensure generated post is wellness-related (keyword check)."""
    combined = " ".join([
        post_data.get("title", ""),
        post_data.get("body", ""),
        post_data.get("hashtags", ""),
        post_data.get("wellness_topic", ""),
    ]).lower()
    return any(keyword in combined for keyword in WELLNESS_KEYWORDS)


def _template_generate_post(topic: str, platform: str, tone: str, closing_line: str) -> dict:
    """Deterministic template fallback — always succeeds, always wellness-safe."""
    title = f"{topic.title()}: A Practical Wellness Moment"
    body = (
        f"Today, focus on {topic.lower()} with one intentional action: "
        f"pause for 2 minutes, breathe deeply, and choose one healthy next step. "
        f"This {tone} message is designed to keep your wellness habits realistic and consistent.\n\n"
        f"{closing_line}"
    )
    return {
        "title": title,
        "body": body,
        "hashtags": _hashtags_for_topic(topic, platform),
        "wellness_topic": topic,
        "closing_line": closing_line,
    }


def generate_social_post(topic: str, platform: str) -> dict:
    """
    Generate a wellness social media post.
    Tries the LLM pipeline with guardrails first;
    falls back to a deterministic template on any failure or guardrail violation.
    """
    normalized_topic = _normalize_wellness_topic(topic)
    normalized_platform = (platform or SocialMediaPost.PLATFORM_INSTAGRAM).strip().lower()
    tone = PLATFORM_TONES.get(normalized_platform, "clear, supportive")
    rules = _global_rules_prompt()
    closing_line = _platform_closing_line(normalized_platform)
    hashtags = _hashtags_for_topic(normalized_topic, normalized_platform)

    llm_result = _llm_generate_post(
        normalized_topic, normalized_platform, tone, rules, closing_line, hashtags
    )
    if llm_result and _passes_guardrails(llm_result):
        post_data = llm_result
        logger.info(
            "Social post generated via LLM for topic=%s platform=%s",
            normalized_topic, normalized_platform,
        )
    else:
        if llm_result is not None:
            logger.warning(
                "LLM result failed guardrails for topic=%s platform=%s; using template fallback",
                normalized_topic, normalized_platform,
            )
        post_data = _template_generate_post(normalized_topic, normalized_platform, tone, closing_line)

    return {
        "platform": normalized_platform,
        "image_url": "",
        "rules_applied": rules,
        **post_data,
    }


def generate_social_image(prompt: str) -> str:
    sanitized = (prompt or "wellness inspiration").strip()
    # Placeholder generator URL; can be replaced with a real image generation provider.
    return f"https://dummyimage.com/1200x1200/0f766e/ffffff.png&text={quote_plus(sanitized[:120])}"


def save_generated_post(data: dict) -> SocialMediaPost:
    return SocialMediaPost.objects.create(
        platform=data.get("platform", SocialMediaPost.PLATFORM_INSTAGRAM),
        title=data.get("title", "Wellness Post"),
        body=data.get("body", ""),
        hashtags=data.get("hashtags", ""),
        image_url=data.get("image_url", ""),
        video_url=data.get("video_url", ""),
        owner=SocialMediaPost.OWNER_DOISENSE,
        owner_user=data.get("owner_user"),
        wellness_topic=data.get("wellness_topic", "wellness"),
        status=data.get("status", SocialMediaPost.STATUS_DRAFT),
        publish_log=data.get("publish_log", "Created from social media generator."),
    )

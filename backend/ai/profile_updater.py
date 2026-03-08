"""
AI Profile Updater: scanează textele scrise de clienți (jurnal, etc.),
structurează informația cu AI și actualizează automat profilele utilizatorilor.
Funcționează indiferent de limba/țara utilizatorului – AI analizează orice limbă.
"""
import json
import logging
from typing import Any

from django.contrib.auth import get_user_model
from journal.models import JournalEntry
from profiles.models import UserProfile

from .router import complete

User = get_user_model()
logger = logging.getLogger(__name__)

# Prompt pentru AI: analizează texte în orice limbă, returnează JSON structurat
PROFILE_ANALYSIS_SYSTEM = """You are an expert at analyzing personal wellbeing and reflection texts.
Your task: read all the user's texts (they may be in ANY language: Romanian, English, German, Italian, Spanish, Polish, etc.).
Extract and structure the information to build a user profile for personalized AI support.

Always respond with ONLY a valid JSON object, no other text. Use this exact structure:
{
  "preferred_tone": "short description of how they prefer to be spoken to (e.g. warm and direct, gentle, encouraging)",
  "sensitivities": "topics or themes to be careful about, or 'none' if not evident",
  "communication_style": "how they express themselves (e.g. concise, detailed, metaphorical)",
  "emotional_baseline": "recurring emotional themes or baseline (e.g. anxiety, hope, fatigue, calm)",
  "keywords": {"themes": ["theme1", "theme2"], "concerns": ["c1", "c2"], "goals": ["g1"]}
}
Keep each string field under 200 characters. keywords must be an object with string keys and arrays of strings.
If you cannot infer something, use empty string "" or empty array [].
Do not add any text before or after the JSON."""


def get_user_texts(user_id: int, limit: int = 50) -> str:
    """
    Colectează textele utilizatorului din DB (jurnal, eventual chat în viitor).
    Returnează un singur bloc de text pentru analiză, păstrând ordinea cronologică.
    """
    entries = (
        JournalEntry.objects.filter(user_id=user_id)
        .select_related("question")
        .order_by("created_at")[:limit]
    )
    parts = []
    for e in entries:
        parts.append(e.content.strip())
        if e.emotions:
            parts.append(f"[emotions: {', '.join(str(x) for x in e.emotions)}]")
    return "\n---\n".join(parts) if parts else ""


def parse_ai_profile_response(raw: str) -> dict[str, Any] | None:
    """Parsează răspunsul AI (JSON) și validează câmpurile pentru profile."""
    raw = raw.strip()
    # Elimină eventuale blocuri markdown
    if raw.startswith("```"):
        lines = raw.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("AI profile response is not valid JSON: %s", e)
        return None
    # Normalizează la câmpurile din UserProfile
    result = {
        "preferred_tone": _truncate(str(data.get("preferred_tone", "")), 100),
        "sensitivities": _truncate(str(data.get("sensitivities", "")), 500),
        "communication_style": _truncate(str(data.get("communication_style", "")), 100),
        "emotional_baseline": _truncate(str(data.get("emotional_baseline", "")), 100),
        "keywords": data.get("keywords") if isinstance(data.get("keywords"), dict) else {},
    }
    return result


def _truncate(s: str, max_len: int) -> str:
    return s[:max_len] if len(s) > max_len else s


def update_profile_from_ai(user_id: int, dry_run: bool = False) -> bool:
    """
    Pentru un user: colectează texte, trimite la AI, parsează răspunsul, actualizează profile.
    Returnează True dacă actualizarea a reușit.
    """
    texts = get_user_texts(user_id)
    if not texts or len(texts) < 20:
        logger.info("User %s has insufficient text for profile update (skip).", user_id)
        return False

    prompt = (
        "Analyze the following user texts (they can be in any language) and return the profile JSON.\n\n"
        "User texts:\n" + texts[:12000]
    )
    reply = complete(prompt, system=PROFILE_ANALYSIS_SYSTEM, user_id=user_id)
    if not reply or reply.startswith("["):
        logger.warning("AI returned empty or error for user %s: %s", user_id, reply[:200])
        return False

    profile_data = parse_ai_profile_response(reply)
    if not profile_data:
        return False

    if dry_run:
        logger.info("Dry run – would update profile for user %s: %s", user_id, profile_data)
        return True

    profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
    profile.preferred_tone = profile_data["preferred_tone"]
    profile.sensitivities = profile_data["sensitivities"]
    profile.communication_style = profile_data["communication_style"]
    profile.emotional_baseline = profile_data["emotional_baseline"]
    profile.keywords = profile_data["keywords"]
    profile.save(update_fields=[
        "preferred_tone", "sensitivities", "communication_style",
        "emotional_baseline", "keywords",
    ])
    logger.info("Updated profile for user %s.", user_id)
    return True


def run_profile_updates_for_all_users(dry_run: bool = False, limit: int | None = None) -> dict:
    """
    Rulează actualizarea de profile pentru toți userii care au suficiente texte.
    Returnează dict cu: processed, updated, skipped, errors.
    """
    user_ids = (
        JournalEntry.objects.values_list("user_id", flat=True)
        .distinct()
    )
    if limit:
        user_ids = list(user_ids)[:limit]
    else:
        user_ids = list(user_ids)

    stats = {"processed": 0, "updated": 0, "skipped": 0, "errors": 0}
    for uid in user_ids:
        stats["processed"] += 1
        try:
            ok = update_profile_from_ai(uid, dry_run=dry_run)
            if ok:
                stats["updated"] += 1
            else:
                stats["skipped"] += 1
        except Exception as e:
            logger.exception("Profile update failed for user %s: %s", uid, e)
            stats["errors"] += 1
    return stats

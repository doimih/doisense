from pathlib import Path
import json
from typing import Dict, Any

from .models import ConversationTemplate
from profiles.models import UserProfile
from core.system_config import get_system_config


SUPPORT_DISCLAIMER = (
    "Iti sunt alaturi cu suport emotional si recomandari generale. "
    "Nu pot oferi sfaturi medicale sau psihologice, dar te pot ajuta sa intelegi mai bine ce simti."
)


def _normalize_plan_tier(user) -> str:
    return getattr(user, "effective_plan_tier", lambda: "free")()


def _should_force_support_disclaimer(current_message: str, conversation_count: int | None) -> bool:
    if conversation_count is not None and conversation_count >= 0 and (conversation_count + 1) % 10 == 0:
        return True

    message = (current_message or "").lower()
    if not message:
        return False

    keywords = (
        "diagnose",
        "diagnosis",
        "diagnostic",
        "medical",
        "doctor",
        "psychi",
        "psycholog",
        "psychiat",
        "therapy",
        "terapie",
        "medicatie",
        "medication",
        "panic attack",
        "self-harm",
        "suicide",
        "kill myself",
    )
    return any(keyword in message for keyword in keywords)


def _get_disclaimer_instruction(current_message: str, conversation_count: int | None) -> str:
    if _should_force_support_disclaimer(current_message, conversation_count):
        return (
            "Include this short disclaimer once in this reply, in a calm and empathetic tone: "
            f'"{SUPPORT_DISCLAIMER}"'
        )
    return (
        "Do not add the medical-support disclaimer by default. Add it only when the user requests diagnosis, "
        "therapy, treatment, urgent mental-health certainty, or when the system explicitly asks for it."
    )


def _get_chat_capability_instruction(plan_tier: str) -> str:
    if plan_tier == "trial":
        return (
            "User tier: TRIAL. Treat this as a guided preview tier, richer than BASIC but lighter than PREMIUM. "
            "You may use recent context, reflect the user's emotional state, and suggest one short action plan with at most 2 concrete steps. "
            "Do not present weekly or monthly reports, long-term trend claims, or typology updates as available in trial. "
            "If the user asks for deeper longitudinal tracking, explain briefly that ongoing reports and richer follow-up are part of paid plans after the trial."
        )
    if plan_tier == "premium":
        return (
            "User tier: PREMIUM. You may use recent conversation context, provide structured reflection, identify recent-day patterns, "
            "and suggest a short daily action plan with up to 3 steps. You may provide daily or weekly-style summaries when the user asks for them. "
            "Do not produce monthly reports or formal typology updates for PREMIUM."
        )
    if plan_tier == "vip":
        return (
            "User tier: VIP. You may synthesize longer-term patterns, connect current issues with recent history, offer layered strategic guidance, "
            "generate daily, weekly, or monthly-style reflections when asked, and discuss emotional or behavioral typology as a working hypothesis grounded in known history. "
            "Do not upsell; focus on depth, continuity, and precision."
        )
    return (
        "User tier: BASIC. Keep responses concise, focus on one clear next step, and avoid formal plans, reports, or typology updates. "
        "If the user asks for deeper tracking, broader personalization, or recurring reports, answer helpfully and mention in one sentence that paid tiers unlock richer ongoing guidance."
    )


def _get_chat_guardrails(plan_tier: str) -> str:
    if plan_tier == "vip":
        upsell_instruction = "Do not upsell or compare plans unless the user explicitly asks about subscriptions."
    elif plan_tier == "premium":
        upsell_instruction = (
            "Use upsell sparingly. Mention VIP only if the user explicitly asks for deeper longitudinal pattern mapping, typology, "
            "or more strategic long-range guidance."
        )
    elif plan_tier == "trial":
        upsell_instruction = (
            "Use intelligent upsell only when it naturally follows the user's request. Frame paid value as continuity after the trial, "
            "not pressure. Never interrupt emotional support with sales language."
        )
    else:
        upsell_instruction = (
            "Use intelligent upsell only when the user asks for features unavailable in BASIC, such as richer tracking, deeper personalization, or recurring reports. "
            "Keep it to one calm sentence."
        )

    return (
        "Never claim that a plan, report, typology update, or database save was generated unless you are actually presenting that content in the reply and the tier supports it. "
        "If capability is unavailable for this tier, provide the closest lighter alternative instead of promising unavailable functionality. "
        + upsell_instruction
    )


def _load_default_chat_prompt_template() -> str:
    """Load default chat prompt from filesystem."""
    repo_root = Path(__file__).resolve().parents[2]
    prompt_path = repo_root / "templates" / "ai_prompts" / "chat.txt"
    try:
        return prompt_path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _load_orchestrator_prompt_template() -> str:
    """Load orchestrator prompt with DB verification from filesystem."""
    repo_root = Path(__file__).resolve().parents[2]
    prompt_path = repo_root / "templates" / "ai_prompts" / "orchestrator.txt"
    try:
        return prompt_path.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def get_chat_system_prompt(
    user,
    language: str,
    current_message: str = "",
    conversation_count: int | None = None,
) -> str:
    """Build system prompt for chat using user profile and optional template."""
    parts = []
    effective_tier = _normalize_plan_tier(user)
    try:
        profile = user.profile
        if profile.preferred_tone:
            parts.append(f"Preferred tone: {profile.preferred_tone}.")
        if profile.communication_style:
            parts.append(f"Communication style: {profile.communication_style}.")
        if profile.emotional_baseline:
            parts.append(f"Emotional baseline: {profile.emotional_baseline}.")
        if profile.sensitivities:
            parts.append(f"Be aware of sensitivities: {profile.sensitivities}.")
        if profile.keywords:
            parts.append(f"Relevant keywords/context: {profile.keywords}.")
    except UserProfile.DoesNotExist:
        pass

    template = ConversationTemplate.objects.filter(
        language=language, name="default"
    ).first()
    if template:
        parts.insert(0, template.prompt)
    else:
        default_template = _load_default_chat_prompt_template()
        if default_template:
            parts.insert(0, default_template)

    base = get_system_config().ai_system_prompt_base or (
        "You are a supportive wellbeing assistant. Respond in the user's language. "
        "Be empathetic and concise."
    )
    parts.append(f"User language: {language}.")
    parts.append(_get_chat_capability_instruction(effective_tier))
    parts.append(_get_chat_guardrails(effective_tier))
    parts.append(_get_disclaimer_instruction(current_message, conversation_count))
    if parts:
        return base + " " + " ".join(parts)
    return base


def _get_chat_tier_instruction(plan_tier: str) -> str:
    return _get_chat_capability_instruction(plan_tier)


def get_orchestrator_system_prompt(user, language: str = "en") -> str:
    """Build orchestrator system prompt with DB verification instructions.
    
    This is the master orchestrator that coordinates all AI operations and
    explicitly manages what data gets saved to the database.
    """
    orchestrator_template = _load_orchestrator_prompt_template()
    
    if not orchestrator_template:
        # Fallback if orchestrator not found
        return "You are an AI Orchestrator for a wellness platform managing data with DB verification."
    
    # Add user-specific package tier instruction
    package_tier = get_user_package_tier(user)
    package_instruction = f"\nCURENT PACHET UTILIZATOR: {package_tier}\n"
    
    if package_tier == "TRIAL":
        package_instruction += (
            "Capacități trial: conversație ghidată, reflecție structurată și un mini-plan scurt. "
            "Fără rapoarte recurente și fără actualizări de tipologie."
        )
    elif package_tier == "BASIC":
        package_instruction += "Restricții: Fără planuri, rapoarte și actualizări tipologie. Doar conversație și analiză simplă."
    elif package_tier == "PREMIUM":
        package_instruction += "Capacități: Planuri zilnice, rapoarte zilnice/săptămânale, analize detaliate."
    elif package_tier == "VIP":
        package_instruction += "Capacități maxime: Planuri complete, rapoarte lunare, actualizări tipologie, analiza profundă."
    
    return orchestrator_template + package_instruction


def get_user_package_tier(user) -> str:
    """Get user's package tier (TRIAL, BASIC, PREMIUM, VIP)."""
    effective_tier = _normalize_plan_tier(user)
    if effective_tier == "vip":
        return "VIP"
    if effective_tier == "premium":
        return "PREMIUM"
    if effective_tier == "trial":
        return "TRIAL"
    return "BASIC"


def validate_save_to_db(user, response_json: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and enforce save_to_db rules based on user package tier.
    
    This function ensures that AI responses respect package limitations.
    For example: BASIC users cannot save daily_reports, weekly_reports, etc.
    """
    if "save_to_db" not in response_json:
        response_json["save_to_db"] = {}
    
    save_to_db = response_json["save_to_db"]
    package_tier = get_user_package_tier(user)
    
    if package_tier in {"TRIAL", "BASIC"}:
        save_to_db["daily_reports"] = False
        save_to_db["weekly_reports"] = False
        save_to_db["monthly_reports"] = False
        save_to_db["typology_update"] = False
    
    elif package_tier == "PREMIUM":
        save_to_db["monthly_reports"] = False
        save_to_db["typology_update"] = False
    
    return response_json


def extract_save_to_db_fields(response_json: Dict[str, Any]) -> Dict[str, bool]:
    """Extract what needs to be saved to DB from AI response.
    
    Returns a dict with boolean flags indicating what the AI recommends saving.
    Backend then handles actual database operations with error handling.
    """
    return response_json.get("save_to_db", {})


def build_db_save_request(user_id: int, response_json: Dict[str, Any], 
                         original_message: str = None) -> Dict[str, Any]:
    """Build a database save request based on AI response and save_to_db flags.
    
    This creates a structured request that the database layer can process
    with proper error handling and transaction management.
    """
    save_to_db = response_json.get("save_to_db", {})
    
    save_request = {
        "user_id": user_id,
        "timestamp": None,  # Will be set by DB layer
        "operations": []
    }
    
    # Conditional saves based on flags
    if save_to_db.get("conversations"):
        save_request["operations"].append({
            "type": "conversation",
            "data": {
                "message": original_message,
                "response": response_json.get("response", ""),
                "response_type": response_json.get("response_type", "response")
            }
        })
    
    if save_to_db.get("emotional_tags"):
        analysis = response_json.get("analysis", {})
        save_request["operations"].append({
            "type": "emotional_tags",
            "data": {
                "dominant_emotion": analysis.get("emotie_dominanta"),
                "secondary_emotions": analysis.get("emotii_secundare", [])
            }
        })
    
    if save_to_db.get("wellness_metrics"):
        analysis = response_json.get("analysis", {})
        scores = analysis.get("scoruri", {})
        save_request["operations"].append({
            "type": "wellness_metrics",
            "data": {
                "stress_score": scores.get("stres"),
                "energy_score": scores.get("energie"),
                "motivation_score": scores.get("motivatie")
            }
        })
    
    if save_to_db.get("questions_generated"):
        questions = response_json.get("questions", [])
        if questions:
            save_request["operations"].append({
                "type": "questions_generated",
                "data": {
                    "questions": questions
                }
            })
    
    if save_to_db.get("analysis_summary"):
        analysis = response_json.get("analysis", {})
        save_request["operations"].append({
            "type": "analysis_summary",
            "data": {
                "analysis": analysis
            }
        })
    
    if save_to_db.get("daily_reports"):
        reports = response_json.get("reports", {})
        if reports.get("daily"):
            save_request["operations"].append({
                "type": "daily_report",
                "data": reports["daily"]
            })
    
    if save_to_db.get("weekly_reports"):
        reports = response_json.get("reports", {})
        if reports.get("weekly"):
            save_request["operations"].append({
                "type": "weekly_report",
                "data": reports["weekly"]
            })
    
    if save_to_db.get("monthly_reports"):
        reports = response_json.get("reports", {})
        if reports.get("monthly"):
            save_request["operations"].append({
                "type": "monthly_report",
                "data": reports["monthly"]
            })
    
    if save_to_db.get("typology_update"):
        typology = response_json.get("typology", {})
        save_request["operations"].append({
            "type": "typology_update",
            "data": typology
        })
    
    return save_request


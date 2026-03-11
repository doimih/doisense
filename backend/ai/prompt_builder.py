from pathlib import Path
import json
from typing import Dict, Any

from .models import ConversationTemplate
from profiles.models import UserProfile
from core.system_config import get_system_config


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


def get_chat_system_prompt(user, language: str) -> str:
    """Build system prompt for chat using user profile and optional template."""
    parts = []
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
    if parts:
        return base + " " + " ".join(parts)
    return base


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
    
    if package_tier == "BASIC":
        package_instruction += "Restricții: Fără planuri, rapoarte și actualizări tipologie. Doar conversație și analiză simplă."
    elif package_tier == "PREMIUM":
        package_instruction += "Capacități: Planuri zilnice, rapoarte zilnice/săptămânale, analize detaliate."
    elif package_tier == "VIP":
        package_instruction += "Capacități maxime: Planuri complete, rapoarte lunare, actualizări tipologie, analiza profundă."
    
    return orchestrator_template + package_instruction


def get_user_package_tier(user) -> str:
    """Get user's package tier (BASIC, PREMIUM, VIP)."""
    try:
        profile = user.profile
        return profile.subscription_tier or "BASIC"
    except UserProfile.DoesNotExist:
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
    
    # BASIC restrictions
    if package_tier == "BASIC":
        save_to_db["daily_reports"] = False
        save_to_db["weekly_reports"] = False
        save_to_db["monthly_reports"] = False
        save_to_db["typology_update"] = False
    
    # PREMIUM restrictions
    elif package_tier == "PREMIUM":
        save_to_db["monthly_reports"] = False
        save_to_db["typology_update"] = False
    
    # VIP has all capabilities - no restrictions
    
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


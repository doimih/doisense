from .models import ConversationTemplate
from profiles.models import UserProfile
from core.system_config import get_system_config


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

    base = get_system_config().ai_system_prompt_base or (
        "You are a supportive wellbeing assistant. Respond in the user's language. "
        "Be empathetic and concise."
    )
    if parts:
        return base + " " + " ".join(parts)
    return base

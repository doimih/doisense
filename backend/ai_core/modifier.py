import json

from .models import Prompt
from .validators import validate_english_prompt_content


def call_ai_modifier(payload: dict) -> dict | None:
    """
    Call the platform LLM to generate an improved version of a prompt.
    Uses ai.router.complete() which picks OpenAI or Anthropic based on SystemConfig.
    Returns a parsed dict or None if the call fails.
    """
    try:
        from ai.router import complete
    except ImportError:
        return None

    name = payload.get("prompt_name", "")
    ptype = payload.get("prompt_type", "")
    content = payload.get("content", "") or ""

    system = (
        "You are a professional AI prompt editor specializing in mental-health and wellness platforms. "
        "You MUST reply with valid JSON only — no markdown fences, no explanations outside the JSON. "
        "The JSON must have exactly these keys: improved_prompt (string), explanation (array of strings), "
        "risks_if_not_updated (array of strings)."
    )
    user_msg = (
        f"Improve the following prompt named '{name}' (type: {ptype}).\n"
        f"---CURRENT PROMPT---\n{content}\n\n"
        "Rewrite it to be clearer, better structured, and more effective for a wellness AI assistant. "
        "Keep it in English. Return JSON with: improved_prompt, explanation, risks_if_not_updated."
    )

    try:
        raw = complete(user_msg, system=system, max_tokens=1500)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        result = json.loads(raw)
        for key in ("improved_prompt", "explanation", "risks_if_not_updated"):
            if key not in result:
                result[key] = [] if key != "improved_prompt" else ""
        return result
    except Exception:
        return None


def _normalize_lines(content: str) -> list[str]:
    return [line.strip() for line in (content or "").splitlines() if line.strip()]


def suggest_improved_prompt(prompt: Prompt) -> dict:
    payload = {
        "prompt_name": prompt.name,
        "prompt_type": prompt.type,
        "content": prompt.content,
    }
    llm_result = call_ai_modifier(payload)
    if llm_result:
        validate_english_prompt_content(llm_result.get("improved_prompt", ""))
        return llm_result

    lines = _normalize_lines(prompt.content)
    improved_sections = [
        "Role:",
        f"- You are handling the '{prompt.name}' prompt in the AI Brain backend.",
        "",
        "Objectives:",
        "- Keep the response helpful, safe, and aligned with the platform's wellness goals.",
        "- Preserve empathy, clarity, and boundaries.",
        "",
        "Instructions:",
    ]
    if lines:
        improved_sections.extend(f"- {line}" for line in lines)
    improved_sections.extend(
        [
            "",
            "Output expectations:",
            "- Write in clear English.",
            "- Avoid medical claims, unsupported assumptions, and contradictory instructions.",
        ]
    )

    improved_prompt = "\n".join(improved_sections).strip()
    validate_english_prompt_content(improved_prompt)
    return {
        "improved_prompt": improved_prompt,
        "explanation": [
            "Grouped the prompt into explicit sections for role, objectives, instructions, and output expectations.",
            "Reinforced safe wellness boundaries and clarity requirements.",
            "Preserved the existing intent while making the prompt easier for a model to follow.",
        ],
        "risks_if_not_updated": [
            "The prompt may remain harder for a model to follow consistently.",
            "Important safety and wellness framing can stay implicit instead of explicit.",
            "Long-term maintenance gets harder when structure varies across prompts.",
        ],
    }

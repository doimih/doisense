import json

from .models import Prompt


def call_ai_auditor(payload: dict) -> dict | None:
    """
    Call the platform LLM to audit a prompt.
    Uses ai.router.complete() which picks OpenAI or Anthropic based on SystemConfig.
    Returns a parsed dict from the LLM, or None if the call fails.
    """
    try:
        from ai.router import complete
    except ImportError:
        return None

    legacy = payload.get("legacy_prompt", "") or ""
    new = payload.get("new_prompt", "") or ""
    name = payload.get("prompt_name", "")
    ptype = payload.get("prompt_type", "")

    legacy_section = f"\n---LEGACY PROMPT---\n{legacy}\n" if legacy.strip() else "(no legacy prompt provided)"

    system = (
        "You are a professional AI prompt auditor specializing in mental-health and wellness platforms. "
        "You MUST reply with valid JSON only — no markdown fences, no explanations outside the JSON. "
        "The JSON must have exactly these keys: summary (string), issues (array of strings), "
        "recommendations (array of strings), suggested_improvement (string), notes (array of strings)."
    )
    user_msg = (
        f"Audit the following prompt named '{name}' (type: {ptype}).\n"
        f"{legacy_section}\n"
        f"---NEW PROMPT---\n{new}\n\n"
        "Return a JSON audit report with keys: summary, issues, recommendations, suggested_improvement, notes."
    )

    try:
        raw = complete(user_msg, system=system, max_tokens=1024)
        # Strip accidental markdown fences if LLM wraps them
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        result = json.loads(raw)
        # Validate expected keys are present
        for key in ("summary", "issues", "recommendations", "suggested_improvement", "notes"):
            if key not in result:
                result[key] = [] if key in ("issues", "recommendations", "notes") else ""
        return result
    except Exception:
        return None


def _sentence_chunks(value: str) -> list[str]:
    chunks = []
    for part in (value or "").splitlines():
        cleaned = part.strip(" -\t")
        if cleaned:
            chunks.append(cleaned)
    return chunks


def _find_redundancies(legacy_chunks: list[str], new_chunks: list[str]) -> list[str]:
    legacy_set = {chunk.lower() for chunk in legacy_chunks}
    return [chunk for chunk in new_chunks if chunk.lower() in legacy_set]


def _find_missing_rules(legacy_chunks: list[str], new_chunks: list[str]) -> list[str]:
    new_set = {chunk.lower() for chunk in new_chunks}
    return [chunk for chunk in legacy_chunks if chunk.lower() not in new_set]


def _find_contradictions(legacy_text: str, new_text: str) -> list[str]:
    contradictions = []
    pairs = [
        ("always", "never"),
        ("must", "must not"),
        ("be concise", "be detailed"),
        ("empathetic", "detached"),
    ]
    legacy_lower = legacy_text.lower()
    new_lower = new_text.lower()
    for left, right in pairs:
        if left in legacy_lower and right in new_lower:
            contradictions.append(f"Legacy contains '{left}' while new prompt contains '{right}'.")
        if right in legacy_lower and left in new_lower:
            contradictions.append(f"Legacy contains '{right}' while new prompt contains '{left}'.")
    return contradictions


def _tone_mismatch(legacy_text: str, new_text: str) -> list[str]:
    notes = []
    legacy_lower = legacy_text.lower()
    new_lower = new_text.lower()
    if "empathetic" in legacy_lower and "empathetic" not in new_lower:
        notes.append("Legacy prompt explicitly requires empathy but the new prompt does not mention it.")
    if "wellness" in legacy_lower and "wellness" not in new_lower:
        notes.append("Legacy prompt is wellness-oriented while the new prompt does not reinforce that focus.")
    return notes


def audit_prompt(prompt: Prompt, legacy_prompt_text: str | None = None) -> dict:
    payload = {
        "prompt_name": prompt.name,
        "prompt_type": prompt.type,
        "legacy_prompt": legacy_prompt_text or "",
        "new_prompt": prompt.content,
    }
    llm_result = call_ai_auditor(payload)
    if llm_result:
        return llm_result

    legacy_prompt = legacy_prompt_text or ""
    legacy_chunks = _sentence_chunks(legacy_prompt)
    new_chunks = _sentence_chunks(prompt.content)
    redundancies = _find_redundancies(legacy_chunks, new_chunks)
    missing_rules = _find_missing_rules(legacy_chunks, new_chunks)
    contradictions = _find_contradictions(legacy_prompt, prompt.content)
    tone_notes = _tone_mismatch(legacy_prompt, prompt.content)

    potential_risks = [
        *contradictions,
        *tone_notes,
        *(f"Missing legacy rule: {item}" for item in missing_rules[:5]),
    ]

    recommended_changes = []
    if missing_rules:
        recommended_changes.append("Reintroduce the missing operational rules that still matter for the AI behavior.")
    if contradictions:
        recommended_changes.append("Resolve contradictory instructions before promoting this prompt to production.")
    if not recommended_changes:
        recommended_changes.append("Prompt is broadly consistent; validate it with a controlled staging test.")

    issue_lines = []
    if contradictions:
        issue_lines.extend(contradictions)
    if missing_rules:
        issue_lines.extend(f"Missing legacy rule: {item}" for item in missing_rules[:10])
    if tone_notes:
        issue_lines.extend(tone_notes)

    if contradictions:
        suggested_improvement = "Resolve contradictory instructions and keep only one behavioral rule per requirement."
    elif missing_rules:
        suggested_improvement = "Restore the missing legacy constraints that are still required in production behavior."
    else:
        suggested_improvement = "The prompt is structurally sound; focus on minor clarity improvements and staging validation."

    summary_parts = [
        f"Prompt '{prompt.name}' has {len(contradictions)} contradictions",
        f"{len(missing_rules)} missing legacy rules",
        f"and {len(redundancies)} overlaps with the legacy prompt.",
    ]

    return {
        "summary": " ".join(summary_parts),
        "issues": issue_lines or ["No critical issues detected in the current prompt draft."],
        "recommendations": recommended_changes,
        "suggested_improvement": suggested_improvement,
        "notes": [
            f"Legacy lines analyzed: {len(legacy_chunks)}",
            f"New prompt lines analyzed: {len(new_chunks)}",
            *[f"Redundant with legacy prompt: {item}" for item in redundancies[:10]],
        ],
    }

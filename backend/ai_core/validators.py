import re
import unicodedata

from django.core.exceptions import ValidationError


ENGLISH_ONLY_ERROR = (
    "Prompt content must be written in English. Other languages are not allowed."
)

_ENGLISH_MARKERS = {
    "a",
    "an",
    "and",
    "assistant",
    "be",
    "context",
    "for",
    "guidance",
    "must",
    "or",
    "prompt",
    "response",
    "rules",
    "should",
    "system",
    "the",
    "to",
    "user",
    "with",
    "you",
}

_FOREIGN_MARKERS = {
    "acest",
    "aceasta",
    "ajuta",
    "bonjour",
    "ciao",
    "como",
    "con",
    "cu",
    "das",
    "del",
    "des",
    "donde",
    "este",
    "esti",
    "fara",
    "gracias",
    "hola",
    "intrebare",
    "pentru",
    "pero",
    "por",
    "respuesta",
    "sau",
    "si",
    "sunt",
    "utilizator",
    "vous",
}

_BLOCKED_SCRIPTS = (
    "CYRILLIC",
    "ARABIC",
    "HEBREW",
    "GREEK",
    "HIRAGANA",
    "KATAKANA",
    "HANGUL",
    "CJK",
)


def _contains_non_latin_script(value: str) -> bool:
    for char in value:
        if not char.isalpha():
            continue
        try:
            name = unicodedata.name(char)
        except ValueError:
            continue
        if any(script in name for script in _BLOCKED_SCRIPTS):
            return True
    return False


def validate_english_prompt_content(value: str) -> None:
    text = (value or "").strip()
    if not text:
        return

    if _contains_non_latin_script(text):
        raise ValidationError(ENGLISH_ONLY_ERROR)

    words = re.findall(r"[A-Za-z']+", text.lower())
    if len(words) < 4:
        return

    english_hits = sum(1 for word in words if word in _ENGLISH_MARKERS)
    foreign_hits = sum(1 for word in words if word in _FOREIGN_MARKERS)

    if foreign_hits >= 2 and english_hits == 0:
        raise ValidationError(ENGLISH_ONLY_ERROR)

    if foreign_hits >= max(2, english_hits + 1):
        raise ValidationError(ENGLISH_ONLY_ERROR)

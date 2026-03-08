import pytest
from ai.profile_updater import get_user_texts, parse_ai_profile_response, _truncate


@pytest.mark.django_db
def test_get_user_texts_empty(user):
    assert get_user_texts(user.id) == ""


@pytest.mark.django_db
def test_get_user_texts_from_entries(user, journal_question):
    from journal.models import JournalEntry
    JournalEntry.objects.create(user=user, question=journal_question, content="I feel calm today.")
    JournalEntry.objects.create(user=user, question=journal_question, content="Anxious about work.")
    text = get_user_texts(user.id)
    assert "I feel calm today" in text
    assert "Anxious about work" in text


def test_parse_ai_profile_response_valid():
    raw = '{"preferred_tone": "warm", "sensitivities": "none", "communication_style": "short", "emotional_baseline": "calm", "keywords": {"themes": ["work"]}}'
    out = parse_ai_profile_response(raw)
    assert out is not None
    assert out["preferred_tone"] == "warm"
    assert out["sensitivities"] == "none"
    assert out["keywords"] == {"themes": ["work"]}


def test_parse_ai_profile_response_with_markdown():
    raw = '```json\n{"preferred_tone": "gentle", "sensitivities": "", "communication_style": "", "emotional_baseline": "", "keywords": {}}\n```'
    out = parse_ai_profile_response(raw)
    assert out is not None
    assert out["preferred_tone"] == "gentle"


def test_parse_ai_profile_response_invalid_returns_none():
    assert parse_ai_profile_response("not json at all") is None
    assert parse_ai_profile_response("") is None


def test_truncate():
    assert _truncate("hello", 10) == "hello"
    assert _truncate("hello world", 5) == "hello"

import pytest
from django.urls import reverse
from rest_framework import status

from journal.models import JournalQuestion


@pytest.fixture
def journal_question(db):
    return JournalQuestion.objects.create(
        text="How do you feel today?",
        category="daily",
        language="en",
        active=True,
    )


@pytest.mark.django_db
def test_journal_questions_requires_auth(api_client):
    response = api_client.get(reverse("journal-questions"))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_journal_questions_list(paid_client, journal_question):
    response = paid_client.get(reverse("journal-questions") + "?language=en")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) >= 1
    assert response.data[0]["text"] == journal_question.text


@pytest.mark.django_db
def test_journal_entries_post_requires_auth(api_client, journal_question):
    response = api_client.post(
        reverse("journal-entries"),
        {"question": journal_question.id, "content": "I feel good.", "emotions": []},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_journal_entries_post_success(paid_client, paid_user, journal_question):
    response = paid_client.post(
        reverse("journal-entries"),
        {"question": journal_question.id, "content": "I feel good.", "emotions": []},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["content"] == "I feel good."
    assert response.data["question"] == journal_question.id

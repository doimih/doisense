import pytest
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from programs.models import GuidedProgram, GuidedProgramDay, ProgramReflection, UserProgramProgress


@pytest.fixture
def guided_program(db):
    program = GuidedProgram.objects.create(
        title="Focus Reset",
        description="Program test",
        language="en",
        active=True,
        is_premium=False,
    )
    GuidedProgramDay.objects.create(
        program=program,
        day_number=1,
        title="Day 1",
        content="Content 1",
        question="Q1",
    )
    GuidedProgramDay.objects.create(
        program=program,
        day_number=2,
        title="Day 2",
        content="Content 2",
        question="Q2",
    )
    return program


@pytest.mark.django_db
def test_program_progress_complete_day(paid_client, guided_program):
    url = reverse("program-progress", args=[guided_program.id])
    response = paid_client.post(url, {"day_number": 1}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert 1 in response.data["completed_days"]
    assert response.data["current_day"] == 2


@pytest.mark.django_db
def test_program_progress_requires_auth(api_client, guided_program):
    url = reverse("program-progress", args=[guided_program.id])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_program_pause_and_resume(paid_client, paid_user, guided_program):
    pause_url = reverse("program-pause", args=[guided_program.id])
    resume_url = reverse("program-resume", args=[guided_program.id])

    pause_response = paid_client.post(pause_url, {}, format="json")
    assert pause_response.status_code == status.HTTP_200_OK
    assert pause_response.data["is_paused"] is True
    assert pause_response.data["paused_at"] is not None

    resume_response = paid_client.post(resume_url, {}, format="json")
    assert resume_response.status_code == status.HTTP_200_OK
    assert resume_response.data["is_paused"] is False
    assert resume_response.data["paused_at"] is None

    progress = UserProgramProgress.objects.get(user=paid_user, program=guided_program)
    assert progress.is_paused is False
    assert progress.paused_at is None


@pytest.mark.django_db
def test_program_reflection_create(paid_client, paid_user, guided_program):
    reflection_url = reverse("program-reflection", args=[guided_program.id])
    response = paid_client.post(
        reflection_url,
        {"day_number": 1, "reflection_text": "I kept my routine today."},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "ai_feedback" in response.data
    assert "Great reflection for day 1" in response.data["ai_feedback"]

    reflection = ProgramReflection.objects.get(user=paid_user, program=guided_program, day_number=1)
    assert reflection.reflection_text == "I kept my routine today."


@pytest.mark.django_db
def test_program_reflection_get_by_day_number(paid_client, paid_user, guided_program):
    ProgramReflection.objects.create(
        user=paid_user,
        program=guided_program,
        day_number=1,
        reflection_text="I noticed I start better with 10 minutes of planning.",
        ai_feedback="Good focus.",
    )

    url = reverse("program-reflection", args=[guided_program.id]) + "?day_number=1"
    response = paid_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["day_number"] == 1
    assert response.data["reflection_text"].startswith("I noticed")


@pytest.mark.django_db
def test_program_reflection_invalid_day_rejected(paid_client, guided_program):
    url = reverse("program-reflection", args=[guided_program.id])
    response = paid_client.post(
        url,
        {"day_number": 99, "reflection_text": "Out of range."},
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Program has only" in response.data["detail"]


@pytest.mark.django_db
def test_program_progress_marks_dropout_for_inactive_user(paid_client, paid_user, guided_program):
    progress = UserProgramProgress.objects.create(
        user=paid_user,
        program=guided_program,
        current_day=1,
        completed_days=[],
        is_paused=False,
    )
    old_ts = timezone.now() - timedelta(days=8)
    UserProgramProgress.objects.filter(pk=progress.pk).update(last_active_at=old_ts)

    response = paid_client.get(reverse("program-progress", args=[guided_program.id]))

    assert response.status_code == status.HTTP_200_OK
    progress.refresh_from_db()
    assert progress.dropout_marked_at is not None

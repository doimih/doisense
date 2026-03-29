import datetime

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from calendar_tasks.models import Task, TaskProgress
from programs.models import GuidedProgram, GuidedProgramDay, ProgramReflection, UserProgramProgress

User = get_user_model()


def _auth_client_for(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def premium_user(db):
    return User.objects.create_user(
        email="premium@example.com",
        password="testpass123",
        language="en",
        plan_tier="premium",
        is_premium=True,
    )


@pytest.fixture
def premium_client(premium_user):
    return _auth_client_for(premium_user)


@pytest.fixture
def vip_user(db):
    return User.objects.create_user(
        email="vip@example.com",
        password="testpass123",
        language="en",
        plan_tier="vip",
        is_premium=True,
        vip_manual_override=True,
    )


@pytest.fixture
def vip_client(vip_user):
    return _auth_client_for(vip_user)


@pytest.fixture
def programs_catalog(db):
    basic = GuidedProgram.objects.create(
        title="Focus Reset",
        description="Basic test program",
        language="en",
        category=GuidedProgram.CATEGORY_COACHING,
        duration_days=2,
        plan_access=GuidedProgram.PLAN_ACCESS_BASIC,
        active=True,
    )
    premium = GuidedProgram.objects.create(
        title="Deep Work Sprint",
        description="Premium execution program",
        language="en",
        category=GuidedProgram.CATEGORY_COACHING,
        duration_days=3,
        plan_access=GuidedProgram.PLAN_ACCESS_PREMIUM,
        active=True,
    )
    vip = GuidedProgram.objects.create(
        title="Executive Recovery",
        description="VIP adaptive program",
        language="en",
        category=GuidedProgram.CATEGORY_WELLNESS,
        duration_days=2,
        plan_access=GuidedProgram.PLAN_ACCESS_VIP,
        active=True,
    )

    for program in (basic, premium, vip):
        for day_number in range(1, program.duration_days + 1):
            GuidedProgramDay.objects.create(
                program=program,
                day_number=day_number,
                title=f"Day {day_number}",
                content=f"Content for day {day_number}",
                task_type=GuidedProgramDay.TASK_TYPE_CHECKIN,
                estimated_time_minutes=10,
                question=f"Question {day_number}",
                ai_prompt=f"Prompt {day_number}",
            )

    return {"basic": basic, "premium": premium, "vip": vip}


@pytest.mark.django_db
def test_program_list_respects_basic_tier(paid_client, programs_catalog):
    response = paid_client.get(reverse("programs-list"), {"language": "en"})

    assert response.status_code == status.HTTP_200_OK
    titles = [item["title"] for item in response.data["items"]]
    assert programs_catalog["basic"].title in titles
    assert programs_catalog["premium"].title not in titles
    assert programs_catalog["vip"].title not in titles


@pytest.mark.django_db
def test_program_detail_exposes_days_for_accessible_program(paid_client, programs_catalog):
    response = paid_client.get(reverse("program-detail", args=[programs_catalog["basic"].id]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == programs_catalog["basic"].title
    assert len(response.data["daily_steps"]) == programs_catalog["basic"].duration_days
    assert response.data["can_activate"] is False


@pytest.mark.django_db
def test_program_activate_generates_calendar_tasks(premium_client, premium_user, programs_catalog):
    program = programs_catalog["premium"]

    response = premium_client.post(reverse("program-activate", args=[program.id]), {}, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["calendar_tasks_generated"] == program.duration_days
    assert response.data["activation"]["status"] == "active"
    assert Task.objects.filter(user=premium_user, guided_program=program, source=Task.SOURCE_PROGRAM).count() == program.duration_days


@pytest.mark.django_db
def test_basic_user_cannot_activate_premium_program(paid_client, programs_catalog):
    response = paid_client.post(reverse("program-activate", args=[programs_catalog["premium"].id]), {}, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["required_plan"] == GuidedProgram.PLAN_ACCESS_PREMIUM


@pytest.mark.django_db
def test_program_active_returns_current_step_after_activation(premium_client, programs_catalog):
    program = programs_catalog["premium"]
    premium_client.post(reverse("program-activate", args=[program.id]), {}, format="json")

    response = premium_client.get(reverse("program-active"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["item"]["program"]["id"] == program.id
    assert response.data["item"]["current_step"]["day_number"] == 1


@pytest.mark.django_db
def test_complete_day_marks_task_progress_and_vip_message(vip_client, vip_user, programs_catalog):
    program = programs_catalog["vip"]
    vip_client.post(reverse("program-activate", args=[program.id]), {}, format="json")

    response = vip_client.post(reverse("program-complete-day", args=[program.id]), {"day_number": 1}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["completed_day"] == 1
    assert response.data["daily_message"]
    assert response.data["dynamic_recommendation"] is not None

    activation = UserProgramProgress.objects.get(user=vip_user, program=program)
    task = Task.objects.get(user=vip_user, guided_program=program, program_day=1, source=Task.SOURCE_PROGRAM)
    scheduled_day = activation.start_date + datetime.timedelta(days=0)
    progress_entry = TaskProgress.objects.get(task=task, progress_date=scheduled_day)
    assert progress_entry.is_completed is True


@pytest.mark.django_db
def test_program_reflection_roundtrip(premium_client, premium_user, programs_catalog):
    program = programs_catalog["premium"]

    create_response = premium_client.post(
        reverse("program-reflection", args=[program.id]),
        {"day_number": 1, "reflection_text": "I worked with more clarity today."},
        format="json",
    )

    assert create_response.status_code == status.HTTP_201_CREATED
    assert "ziua 1" in create_response.data["ai_feedback"].lower()

    fetch_response = premium_client.get(reverse("program-reflection", args=[program.id]), {"day_number": 1})

    assert fetch_response.status_code == status.HTTP_200_OK
    assert fetch_response.data["reflection_text"] == "I worked with more clarity today."
    assert ProgramReflection.objects.filter(user=premium_user, program=program, day_number=1).exists()


@pytest.mark.django_db
def test_program_progress_endpoint_returns_activation_state(premium_client, premium_user, programs_catalog):
    program = programs_catalog["premium"]
    progress = UserProgramProgress.objects.create(
        user=premium_user,
        program=program,
        current_day=2,
        start_date=timezone.localdate() - datetime.timedelta(days=1),
        completed_days=[1],
    )

    response = premium_client.get(reverse("program-progress", args=[program.id]))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == progress.id
    assert response.data["progress_day"] == 2
    assert response.data["completed_days"] == [1]

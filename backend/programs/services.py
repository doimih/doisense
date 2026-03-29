from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from ai.router import complete
from calendar_tasks.models import Task
from calendar_tasks.plan_access import resolve_calendar_plan_for_user
from calendar_tasks.services import update_task_stats, upsert_progress
from core.analytics import track_event

from .models import GuidedProgram, GuidedProgramDay, UserProgramProgress
from .seed_catalog import iter_program_seeds


PLAN_ORDER = {
    GuidedProgram.PLAN_ACCESS_BASIC: 1,
    GuidedProgram.PLAN_ACCESS_PREMIUM: 2,
    GuidedProgram.PLAN_ACCESS_VIP: 3,
}


CATEGORY_PRESENTATION = {
    GuidedProgram.CATEGORY_WELLNESS: {"title": "Wellness", "icon": "Leaf"},
    GuidedProgram.CATEGORY_COACHING: {"title": "Coaching", "icon": "Compass"},
    GuidedProgram.CATEGORY_EDUCATIE: {"title": "Educatie", "icon": "BookOpen"},
    GuidedProgram.CATEGORY_SUPORT: {"title": "Suport", "icon": "HeartHandshake"},
}


STEP_TYPE_DETAILS = {
    GuidedProgramDay.TASK_TYPE_CHECKIN: {
        "label": "Check-in",
        "prefix": "Check-in",
    },
    GuidedProgramDay.TASK_TYPE_EXERCISE: {
        "label": "Exercise",
        "prefix": "Exercitiu",
    },
    GuidedProgramDay.TASK_TYPE_REFLECTION: {
        "label": "Reflection",
        "prefix": "Reflectie",
    },
    GuidedProgramDay.TASK_TYPE_REMINDER: {
        "label": "Reminder",
        "prefix": "Reminder",
    },
    GuidedProgramDay.TASK_TYPE_JOURNALING: {
        "label": "Journaling",
        "prefix": "Jurnal",
    },
}


def user_program_tier(user) -> str | None:
    plan_ctx = resolve_calendar_plan_for_user(user)
    if plan_ctx:
        return plan_ctx.code
    if not user or not getattr(user, "is_authenticated", False):
        return None
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return GuidedProgram.PLAN_ACCESS_VIP
    if hasattr(user, "effective_plan_tier"):
        tier = user.effective_plan_tier()
        if tier in {"trial", "basic"}:
            return GuidedProgram.PLAN_ACCESS_BASIC
        if tier == "premium":
            return GuidedProgram.PLAN_ACCESS_PREMIUM
        if tier == "vip":
            return GuidedProgram.PLAN_ACCESS_VIP
    return None


def can_view_program(user, program: GuidedProgram) -> bool:
    tier = user_program_tier(user)
    if not tier:
        return False
    return PLAN_ORDER[tier] >= PLAN_ORDER[program.plan_access]


def can_activate_program(user, program: GuidedProgram) -> bool:
    tier = user_program_tier(user)
    if not tier:
        return False
    if tier == GuidedProgram.PLAN_ACCESS_BASIC:
        return False
    return PLAN_ORDER[tier] >= PLAN_ORDER[program.plan_access]


def vip_enabled(user) -> bool:
    return user_program_tier(user) == GuidedProgram.PLAN_ACCESS_VIP


def available_programs_for_user(user, *, category: str | None = None, language: str | None = None):
    qs = GuidedProgram.objects.filter(active=True)
    if category:
        qs = qs.filter(category=category)
    if language:
        qs = qs.filter(language=language)
    tier = user_program_tier(user)
    if not tier:
        return qs.none()
    return qs.filter(plan_access__in=[code for code, weight in PLAN_ORDER.items() if weight <= PLAN_ORDER[tier]])


def serialize_program(program: GuidedProgram, user=None, *, include_days: bool = False, activation: UserProgramProgress | None = None) -> dict:
    payload = {
        "id": program.id,
        "category": program.category,
        "category_meta": CATEGORY_PRESENTATION[program.category],
        "title": program.title,
        "description": program.description,
        "duration_days": program.duration_days,
        "plan_access": program.plan_access,
        "language": program.language,
        "active": program.active,
        "is_premium": program.is_premium,
        "is_vip_exclusive": program.is_vip_exclusive,
        "can_view": can_view_program(user, program) if user else True,
        "can_activate": can_activate_program(user, program) if user else False,
    }
    if activation:
        payload["activation"] = serialize_activation(activation)
    if include_days:
        payload["daily_steps"] = [serialize_day(step) for step in program.days.order_by("day_number")]
    return payload


def serialize_day(day: GuidedProgramDay) -> dict:
    return {
        "id": day.id,
        "day_number": day.day_number,
        "title": day.title,
        "content": day.content,
        "task_type": day.task_type,
        "estimated_time_minutes": day.estimated_time_minutes,
        "question": day.question,
        "ai_prompt": day.ai_prompt,
    }


def serialize_activation(progress: UserProgramProgress) -> dict:
    return {
        "id": progress.id,
        "user_id": progress.user_id,
        "program_id": progress.program_id,
        "start_date": progress.start_date.isoformat(),
        "status": progress.status,
        "progress_day": progress.progress_day,
        "completed_days": progress.completed_days,
        "started_at": progress.started_at.isoformat() if progress.started_at else None,
        "completed_at": progress.completed_at.isoformat() if progress.completed_at else None,
        "is_paused": progress.is_paused,
    }


def ensure_single_active_program(user, *, except_program_id: int | None = None) -> None:
    qs = UserProgramProgress.objects.filter(user=user, completed_at__isnull=True, is_paused=False)
    if except_program_id:
        qs = qs.exclude(program_id=except_program_id)
    for progress in qs:
        progress.pause()


def _program_task_title(program: GuidedProgram, step: GuidedProgramDay) -> str:
    prefix = STEP_TYPE_DETAILS[step.task_type]["prefix"]
    return f"{prefix}: {program.title} · Ziua {step.day_number}"


def _program_task_description(step: GuidedProgramDay) -> str:
    base = step.content.strip()
    if step.question:
        base = f"{base}\n\nIntrebare ghidata: {step.question.strip()}"
    return base


def generate_calendar_tasks_for_activation(user, program: GuidedProgram, progress: UserProgramProgress) -> list[Task]:
    created: list[Task] = []
    Task.objects.filter(user=user, guided_program=program, source=Task.SOURCE_PROGRAM).delete()
    for step in program.days.order_by("day_number"):
        scheduled_day = progress.start_date + timedelta(days=step.day_number - 1)
        task = Task.objects.create(
            user=user,
            title=_program_task_title(program, step),
            description=_program_task_description(step),
            duration_minutes=step.estimated_time_minutes,
            frequency=Task.FREQ_DAILY,
            reminder_enabled=True,
            reminder_minutes_before=15,
            source=Task.SOURCE_PROGRAM,
            task_type=step.task_type,
            guided_program=program,
            program_day=step.day_number,
            advanced_options={
                "program_category": program.category,
                "program_day": step.day_number,
                "task_type": step.task_type,
                "webview_safe": True,
            },
            ai_generated=vip_enabled(user),
            ai_metadata={"generated_from": "guided_program_activation"},
            starts_on=scheduled_day,
            ends_on=scheduled_day,
        )
        created.append(task)
    return created


def build_vip_daily_message(user, program: GuidedProgram, step: GuidedProgramDay, progress: UserProgramProgress) -> str:
    context = (
        f"Program: {program.title}\n"
        f"Categorie: {program.category}\n"
        f"Zi curenta: {step.day_number} din {program.duration_days}\n"
        f"Task type: {step.task_type}\n"
        f"Progres completat: {len(progress.completed_days)} zile\n"
        f"Continut zi: {step.content[:500]}"
    )
    try:
        reply = complete(
            prompt=(
                "Creeaza un mesaj scurt, elegant si practic pentru un utilizator VIP Executive. "
                "Include o recomandare adaptiva si o incurajare pentru ziua curenta.\n\n"
                f"{context}"
            ),
            system=(
                "Esti coach AI pentru wellbeing si performanta. "
                "Raspunzi in romana, maximum 120 de cuvinte, fara markdown."
            ),
            user_id=user.id,
            max_tokens=220,
        )
        cleaned = (reply or "").strip()
        if cleaned and not cleaned.startswith("["):
            return cleaned
    except Exception:
        pass
    return (
        f"Astazi esti in ziua {step.day_number} din {program.duration_days} in programul {program.title}. "
        f"Pastreaza accentul pe {STEP_TYPE_DETAILS[step.task_type]['label'].lower()} si ajusteaza intensitatea in functie de energia ta de azi."
    )


@transaction.atomic
def activate_program_for_user(user, program: GuidedProgram) -> tuple[UserProgramProgress, list[Task]]:
    progress, _ = UserProgramProgress.objects.get_or_create(user=user, program=program)
    ensure_single_active_program(user, except_program_id=program.id)
    progress.reset_activation(start_date=timezone.localdate())
    tasks = generate_calendar_tasks_for_activation(user, program, progress)
    track_event(
        "guided_program_activated",
        source="backend",
        user=user,
        properties={"program_id": program.id, "category": program.category, "plan_access": program.plan_access},
    )
    return progress, tasks


@transaction.atomic
def complete_program_day_for_user(user, program: GuidedProgram, *, day_number: int | None = None) -> dict:
    progress = UserProgramProgress.objects.select_for_update().get(user=user, program=program)
    step_number = day_number or progress.current_day
    step = program.days.get(day_number=step_number)

    scheduled_day = progress.start_date + timedelta(days=step_number - 1)
    task = Task.objects.filter(
        user=user,
        guided_program=program,
        program_day=step_number,
        source=Task.SOURCE_PROGRAM,
    ).first()
    if task:
        upsert_progress(task, user, scheduled_day, True, note=f"Completed from program day {step_number}")
        update_task_stats(task)

    progress.mark_day_complete(step_number)
    if step_number >= program.duration_days:
        progress.complete_program()

    message = build_vip_daily_message(user, program, step, progress) if vip_enabled(user) else ""
    recommendation = None
    if vip_enabled(user):
        recommendation = {
            "adjustment": "Reduce intensitatea cu 20% daca energia este scazuta; mentine consistenta, nu perfectiunea.",
            "suggestion": f"Dupa {STEP_TYPE_DETAILS[step.task_type]['label'].lower()}, noteaza un singur insight util pentru maine.",
        }

    track_event(
        "guided_program_day_completed",
        source="backend",
        user=user,
        properties={"program_id": program.id, "day_number": step_number},
    )

    return {
        "activation": serialize_activation(progress),
        "completed_day": step_number,
        "daily_message": message,
        "dynamic_recommendation": recommendation,
    }


def get_active_program_for_user(user) -> UserProgramProgress | None:
    return (
        UserProgramProgress.objects.select_related("program")
        .filter(user=user, completed_at__isnull=True, is_paused=False)
        .order_by("-started_at")
        .first()
    )


def seed_guided_programs(*, language: str = "ro") -> int:
    created = 0
    for seed in iter_program_seeds():
        program, was_created = GuidedProgram.objects.get_or_create(
            title=seed.title,
            language=language,
            defaults={
                "description": seed.description,
                "category": seed.category,
                "duration_days": seed.duration_days,
                "plan_access": seed.plan_access,
                "active": True,
            },
        )
        if not was_created:
            program.description = seed.description
            program.category = seed.category
            program.duration_days = seed.duration_days
            program.plan_access = seed.plan_access
            program.active = True
            program.save()
        program.days.all().delete()
        for day_number in range(1, seed.duration_days + 1):
            task_type = [
                GuidedProgramDay.TASK_TYPE_CHECKIN,
                GuidedProgramDay.TASK_TYPE_EXERCISE,
                GuidedProgramDay.TASK_TYPE_REFLECTION,
                GuidedProgramDay.TASK_TYPE_REMINDER,
                GuidedProgramDay.TASK_TYPE_JOURNALING,
            ][(day_number - 1) % 5]
            focus = {
                "wellness": "reglaj corporal si energie sustenabila",
                "coaching": "claritate, prioritate si executie consecventa",
                "educatie": "intelegere practica si integrare zilnica",
                "suport": "stabilizare emotionala si siguranta interioara",
            }[seed.category]
            GuidedProgramDay.objects.create(
                program=program,
                day_number=day_number,
                title=f"Ziua {day_number}: {seed.title}",
                content=(
                    f"Astazi lucrezi pe {focus}. Alege 10-20 minute pentru a parcurge pasul zilei, "
                    f"noteaza ce observi si mentine ritmul fara presiune inutila. "
                    f"Acesta este pasul {day_number} din {seed.duration_days} in programul {seed.title}."
                ),
                task_type=task_type,
                estimated_time_minutes=10 + ((day_number - 1) % 3) * 5,
                question=f"Care este cel mai util lucru pe care il inveti sau il observi in ziua {day_number}?",
                ai_prompt=(
                    f"Ajuta utilizatorul sa obtina valoare maxima din ziua {day_number} a programului {seed.title}. "
                    f"Fii clar, cald si practic."
                ),
            )
        created += 1 if was_created else 0
    return created
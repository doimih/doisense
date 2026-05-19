from __future__ import annotations


from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.router import complete
from core.analytics import track_event

from .models import Task, TaskProgress
from .plan_access import resolve_calendar_plan_for_user
from .serializers import TaskCheckSerializer, TaskCreateUpdateSerializer, TaskProgressSerializer
from .services import (
    build_month_markers,
    build_stats_response,
    build_task_payload,
    month_range,
    parse_iso_date,
    upsert_progress,
)


def _plan_or_403(request):
    plan_ctx = resolve_calendar_plan_for_user(request.user)
    if not plan_ctx:
        return None, Response(
            {
                "detail": "Calendar & Task module requires BASIC Start or higher.",
                "required_plans": ["basic", "premium", "vip"],
            },
            status=status.HTTP_403_FORBIDDEN,
        )
    return plan_ctx, None


def _task_for_user_or_404(user, task_id: int) -> Task | None:
    return Task.objects.filter(user=user, id=task_id).first()


def _restrict_advanced_options_for_basic(plan_code: str, payload: dict):
    if plan_code != "basic":
        return
    payload["advanced_options"] = {}
    if payload.get("frequency") in (Task.FREQ_MONTHLY, Task.FREQ_CUSTOM):
        payload["frequency"] = Task.FREQ_WEEKLY


class CalendarPlanCapabilitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_ctx, err = _plan_or_403(request)
        if err:
            return err
        return Response(
            {
                "plan": {
                    "code": plan_ctx.code,
                    "name": plan_ctx.name,
                    "capabilities": plan_ctx.capabilities,
                }
            }
        )


class CalendarTaskCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_ctx, err = _plan_or_403(request)
        if err:
            return err

        serializer = TaskCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = dict(serializer.validated_data)
        _restrict_advanced_options_for_basic(plan_ctx.code, payload)

        task = Task.objects.create(
            user=request.user,
            title=payload["title"],
            description=payload.get("description", ""),
            duration_minutes=payload.get("duration_minutes", 15),
            frequency=payload.get("frequency", Task.FREQ_DAILY),
            weekdays=payload.get("weekdays", []),
            month_days=payload.get("month_days", []),
            start_time=payload.get("start_time"),
            reminder_enabled=payload.get("reminder_enabled", False),
            reminder_minutes_before=payload.get("reminder_minutes_before", 10),
            advanced_options=payload.get("advanced_options", {}),
            starts_on=payload.get("starts_on", timezone.localdate()),
            ends_on=payload.get("ends_on"),
        )

        track_event(
            "feature_access_checked",
            source="system",
            user=request.user,
            properties={"feature_key": "calendar_task_create", "granted": True},
        )
        return Response(build_task_payload(task), status=status.HTTP_201_CREATED)


class CalendarTasksListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_ctx, err = _plan_or_403(request)
        if err:
            return err

        month_raw = (request.query_params.get("month") or "").strip()
        if month_raw:
            year, month = [int(item) for item in month_raw.split("-")]
            range_start, range_end = month_range(year, month)
        else:
            today = timezone.localdate()
            range_start, range_end = month_range(today.year, today.month)

        include_inactive = request.query_params.get("include_inactive") == "1" and plan_ctx.has(
            "task_history"
        )
        qs = Task.objects.filter(user=request.user)
        if not include_inactive:
            qs = qs.filter(is_active=True)

        tasks = [
            build_task_payload(task, include_stats=plan_ctx.has("advanced_stats"))
            for task in qs.order_by("-created_at")[:300]
        ]
        markers = build_month_markers(request.user, range_start, range_end)

        return Response(
            {
                "range": {"start": range_start.isoformat(), "end": range_end.isoformat()},
                "items": tasks,
                "markers": markers,
                "plan": {"code": plan_ctx.code, "capabilities": plan_ctx.capabilities},
            }
        )


class CalendarTaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id: int):
        plan_ctx, err = _plan_or_403(request)
        if err:
            return err
        task = _task_for_user_or_404(request.user, task_id)
        if not task:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(build_task_payload(task, include_stats=plan_ctx.has("advanced_stats")))

    def put(self, request, task_id: int):
        plan_ctx, err = _plan_or_403(request)
        if err:
            return err
        task = _task_for_user_or_404(request.user, task_id)
        if not task:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = dict(serializer.validated_data)
        _restrict_advanced_options_for_basic(plan_ctx.code, payload)

        for field in [
            "title",
            "description",
            "duration_minutes",
            "frequency",
            "weekdays",
            "month_days",
            "start_time",
            "reminder_enabled",
            "reminder_minutes_before",
            "advanced_options",
            "starts_on",
            "ends_on",
        ]:
            if field in payload:
                setattr(task, field, payload[field])
        task.save()
        return Response(build_task_payload(task, include_stats=plan_ctx.has("advanced_stats")))

    def delete(self, request, task_id: int):
        _, err = _plan_or_403(request)
        if err:
            return err
        task = _task_for_user_or_404(request.user, task_id)
        if not task:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        task.is_active = False
        task.save(update_fields=["is_active", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class CalendarTaskCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id: int):
        _, err = _plan_or_403(request)
        if err:
            return err

        task = _task_for_user_or_404(request.user, task_id)
        if not task:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        progress_day = serializer.validated_data.get("progress_date", timezone.localdate())
        completed = serializer.validated_data.get("completed", True)
        note = serializer.validated_data.get("note", "")

        row = upsert_progress(task, request.user, progress_day, completed, note)
        track_event(
            "feature_access_checked",
            source="system",
            user=request.user,
            properties={"feature_key": "calendar_task_check", "granted": True},
        )
        return Response(TaskProgressSerializer(row).data, status=status.HTTP_200_OK)


class CalendarTaskProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id: int):
        plan_ctx, err = _plan_or_403(request)
        if err:
            return err

        task = _task_for_user_or_404(request.user, task_id)
        if not task:
            return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        if not plan_ctx.has("task_history"):
            from_day = timezone.localdate() - timezone.timedelta(days=14)
        else:
            from_day = parse_iso_date(
                request.query_params.get("from"),
                fallback=timezone.localdate() - timezone.timedelta(days=180),
            )

        to_day = parse_iso_date(request.query_params.get("to"), fallback=timezone.localdate())
        qs = TaskProgress.objects.filter(
            task=task, progress_date__gte=from_day, progress_date__lte=to_day
        ).order_by("-progress_date")
        data = TaskProgressSerializer(qs, many=True).data
        return Response(
            {"items": data, "range": {"from": from_day.isoformat(), "to": to_day.isoformat()}}
        )


class CalendarStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plan_ctx, err = _plan_or_403(request)
        if err:
            return err

        payload = build_stats_response(request.user, advanced=plan_ctx.has("advanced_stats"))
        payload["plan"] = {"code": plan_ctx.code, "capabilities": plan_ctx.capabilities}
        return Response(payload)


class _VipAiBaseView(APIView):
    permission_classes = [IsAuthenticated]

    capability: str = ""
    prompt_header: str = ""

    def post(self, request):
        plan_ctx, err = _plan_or_403(request)
        if err:
            return err
        if not plan_ctx.has(self.capability):
            return Response(
                {
                    "detail": "Aceasta functie este disponibila doar pentru VIP Executive.",
                    "required_plan": "vip",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        context = (request.data.get("context") or "").strip()
        if not context:
            return Response(
                {"detail": "Campul context este obligatoriu."}, status=status.HTTP_400_BAD_REQUEST
            )

        system = (
            "Esti un coach de productivitate pentru platforma Doisense. "
            "Raspunzi in limba romana, clar, practic si actionabil. "
            "Nu oferi sfaturi medicale."
        )
        prompt = f"{self.prompt_header}\n\nContext utilizator:\n{context}\n\nGenereaza raspuns concret, in puncte."
        reply = complete(prompt=prompt, system=system, user_id=request.user.id, max_tokens=700)
        if reply.startswith("["):
            return Response(
                {"detail": "Serviciul AI este temporar indisponibil."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"result": reply.strip()})


class VipAiHabitSuggestionsView(_VipAiBaseView):
    capability = "ai_habit_suggestions"
    prompt_header = "Genereaza 5 sugestii de obiceiuri personalizate pentru urmatoarele 14 zile."


class VipAiRoutineBuilderView(_VipAiBaseView):
    capability = "ai_routine_builder"
    prompt_header = "Construieste o rutina zilnica completa (dimineata, pranz, seara) cu pasi clari si durata estimata."


class VipAiDailyCheckinView(_VipAiBaseView):
    capability = "ai_daily_checkin"
    prompt_header = (
        "Realizeaza un check-in zilnic ghidat cu 6 intrebari si un mini-plan pentru restul zilei."
    )


class VipAiProgressInsightsView(_VipAiBaseView):
    capability = "ai_progress_insights"
    prompt_header = "Analizeaza progresul obiceiurilor si extrage insight-uri actionabile, riscuri si oportunitati."


class VipAiHabitOptimizationView(_VipAiBaseView):
    capability = "ai_habit_optimization"
    prompt_header = (
        "Optimizeaza obiceiurile existente: ce pastrezi, ce elimini, ce ajustezi si de ce."
    )

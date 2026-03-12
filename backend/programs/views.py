from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.analytics import track_event
from core.feature_access import require_feature
from core.quota import check_and_consume

from .models import GuidedProgram, GuidedProgramDay, ProgramReflection, UserProgramProgress
from .serializers import (
    GuidedProgramSerializer,
    GuidedProgramDaySerializer,
    ProgramReflectionSerializer,
    UserProgramProgressSerializer,
)


def _build_reflection_feedback(reflection_text: str, day_number: int) -> str:
    snippet = reflection_text.strip().replace("\n", " ")[:220]
    return (
        f"Great reflection for day {day_number}. I noticed this key focus: '{snippet}'. "
        "Keep this momentum by choosing one concrete action for the next 24h and "
        "write down when you will do it."
    )


class ProgramListView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def get(self, request):
        language = request.query_params.get("language") or request.user.language or "en"
        qs = GuidedProgram.objects.filter(active=True, language=language)
        serializer = GuidedProgramSerializer(qs, many=True)
        return Response(serializer.data)


class ProgramDayView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def get(self, request, program_id, day_number):
        program = get_object_or_404(GuidedProgram, id=program_id, active=True)
        if program.is_premium and request.user.effective_plan_tier() not in ("premium", "vip"):
            return Response(
                {"detail": "This program requires a premium subscription."},
                status=403,
            )
        day = get_object_or_404(
            GuidedProgramDay, program=program, day_number=day_number
        )
        serializer = GuidedProgramDaySerializer(day)
        return Response(serializer.data)


class ProgramProgressView(APIView):
    """GET: fetch progress for a program. POST: mark current day complete."""

    permission_classes = [IsAuthenticated]

    def _get_program(self, program_id):
        return get_object_or_404(GuidedProgram, id=program_id, active=True)

    @require_feature("programs_access")
    def get(self, request, program_id):
        program = self._get_program(program_id)
        progress, _ = UserProgramProgress.objects.get_or_create(
            user=request.user, program=program
        )

        total_days = program.days.count()
        is_completed = len(progress.completed_days) >= total_days and total_days > 0
        if (
            not is_completed
            and not progress.is_paused
            and progress.last_active_at <= timezone.now() - timedelta(days=7)
            and progress.dropout_marked_at is None
        ):
            progress.dropout_marked_at = timezone.now()
            progress.save(update_fields=["dropout_marked_at"])
            track_event(
                "program_dropout_detected",
                source="backend",
                user=request.user,
                properties={"program_id": program.id, "day_number": progress.current_day},
            )

        serializer = UserProgramProgressSerializer(progress)
        return Response(serializer.data)

    @require_feature("programs_access")
    def post(self, request, program_id):
        program = self._get_program(program_id)
        day_number = request.data.get("day_number")
        if not isinstance(day_number, int) or day_number < 1:
            return Response({"detail": "day_number must be a positive integer."}, status=400)

        total_days = program.days.count()
        if day_number > total_days:
            return Response({"detail": f"Program has only {total_days} days."}, status=400)

        progress, _ = UserProgramProgress.objects.get_or_create(
            user=request.user, program=program
        )
        if day_number not in progress.completed_days:
            allowed, remaining, limit = check_and_consume(
                request.user, "program_days_completed", amount=1
            )
            if not allowed:
                base_url = getattr(
                    settings,
                    "FRONTEND_BASE_URL",
                    "https://projects.doimih.net/doisense",
                )
                language = request.user.language or "en"
                return Response(
                    {
                        "detail": "Monthly program progress quota exceeded for your tier.",
                        "code": "quota_exceeded",
                        "metric": "program_days_completed",
                        "limit": limit,
                        "remaining": remaining,
                        "cta_url": f"{base_url}/{language}/pricing",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        progress.mark_day_complete(day_number)
        if day_number >= total_days:
            track_event(
                "program_completed",
                source="backend",
                user=request.user,
                properties={"program_id": program.id, "day_number": day_number},
            )
        serializer = UserProgramProgressSerializer(progress)
        track_event(
            "program_day_completed",
            source="backend",
            user=request.user,
            properties={"program_id": program.id, "day_number": day_number},
        )
        return Response(serializer.data)


class ProgramPauseView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def post(self, request, program_id):
        program = get_object_or_404(GuidedProgram, id=program_id, active=True)
        progress, _ = UserProgramProgress.objects.get_or_create(user=request.user, program=program)
        progress.pause()
        track_event(
            "program_paused",
            source="backend",
            user=request.user,
            properties={"program_id": program.id, "day_number": progress.current_day},
        )
        return Response(UserProgramProgressSerializer(progress).data)


class ProgramResumeView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def post(self, request, program_id):
        program = get_object_or_404(GuidedProgram, id=program_id, active=True)
        progress, _ = UserProgramProgress.objects.get_or_create(user=request.user, program=program)
        progress.resume()
        track_event(
            "program_resumed",
            source="backend",
            user=request.user,
            properties={"program_id": program.id, "day_number": progress.current_day},
        )
        return Response(UserProgramProgressSerializer(progress).data)


class ProgramReflectionView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def get(self, request, program_id):
        program = get_object_or_404(GuidedProgram, id=program_id, active=True)
        day_number = request.query_params.get("day_number")
        try:
            day_number_int = int(day_number)
        except (TypeError, ValueError):
            return Response({"detail": "day_number query param is required."}, status=400)

        reflection = ProgramReflection.objects.filter(
            user=request.user,
            program=program,
            day_number=day_number_int,
        ).first()
        if not reflection:
            return Response({"detail": "Not found."}, status=404)
        return Response(ProgramReflectionSerializer(reflection).data)

    @require_feature("programs_access")
    def post(self, request, program_id):
        program = get_object_or_404(GuidedProgram, id=program_id, active=True)
        day_number = request.data.get("day_number")
        reflection_text = str(request.data.get("reflection_text") or "").strip()

        if not isinstance(day_number, int) or day_number < 1:
            return Response({"detail": "day_number must be a positive integer."}, status=400)
        if not reflection_text:
            return Response({"detail": "reflection_text is required."}, status=400)

        total_days = program.days.count()
        if day_number > total_days:
            return Response({"detail": f"Program has only {total_days} days."}, status=400)

        feedback = _build_reflection_feedback(reflection_text, day_number)
        reflection, _ = ProgramReflection.objects.update_or_create(
            user=request.user,
            program=program,
            day_number=day_number,
            defaults={
                "reflection_text": reflection_text,
                "ai_feedback": feedback,
            },
        )

        track_event(
            "program_reflection_submitted",
            source="backend",
            user=request.user,
            properties={"program_id": program.id, "day_number": day_number},
        )
        return Response(ProgramReflectionSerializer(reflection).data, status=status.HTTP_201_CREATED)

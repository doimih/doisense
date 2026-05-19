from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.feature_access import require_feature

from .models import GuidedProgram, ProgramReflection, UserProgramProgress
from .serializers import ProgramReflectionSerializer
from .services import (
    activate_program_for_user,
    available_programs_for_user,
    can_activate_program,
    can_view_program,
    complete_program_day_for_user,
    get_active_program_for_user,
    serialize_activation,
    serialize_day,
    serialize_program,
)


def _program_or_404(program_id: int) -> GuidedProgram:
    return get_object_or_404(
        GuidedProgram.objects.prefetch_related("days"), id=program_id, active=True
    )


def _activation_or_404(user, program: GuidedProgram) -> UserProgramProgress:
    return get_object_or_404(
        UserProgramProgress.objects.select_related("program"), user=user, program=program
    )


class ProgramListView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def get(self, request):
        category = (request.query_params.get("category") or "").strip() or None
        language = (request.query_params.get("language") or request.user.language or "ro").strip()
        programs = available_programs_for_user(request.user, category=category, language=language)
        return Response(
            {
                "items": [
                    serialize_program(program, request.user, include_days=False)
                    for program in programs
                ],
                "filters": {"category": category, "language": language},
            }
        )


class ProgramDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def get(self, request, program_id: int):
        program = _program_or_404(program_id)
        if not can_view_program(request.user, program):
            return Response(
                {
                    "detail": "Programul nu este disponibil pentru planul tau.",
                    "required_plan": program.plan_access,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        activation = UserProgramProgress.objects.filter(user=request.user, program=program).first()
        return Response(
            serialize_program(program, request.user, include_days=True, activation=activation)
        )


class ProgramActivateView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def post(self, request, program_id: int):
        program = _program_or_404(program_id)
        if not can_activate_program(request.user, program):
            return Response(
                {
                    "detail": "Activarea automata a programului este disponibila din PREMIUM Flow in sus.",
                    "required_plan": max(program.plan_access, GuidedProgram.PLAN_ACCESS_PREMIUM),
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        activation, tasks = activate_program_for_user(request.user, program)
        return Response(
            {
                "program": serialize_program(
                    program, request.user, include_days=True, activation=activation
                ),
                "activation": serialize_activation(activation),
                "calendar_tasks_generated": len(tasks),
            },
            status=status.HTTP_201_CREATED,
        )


class ProgramActiveView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def get(self, request):
        activation = get_active_program_for_user(request.user)
        if not activation:
            return Response({"item": None})

        program = activation.program
        current_step = program.days.filter(day_number=activation.progress_day).first()
        return Response(
            {
                "item": {
                    "program": serialize_program(
                        program, request.user, include_days=False, activation=activation
                    ),
                    "activation": serialize_activation(activation),
                    "current_step": serialize_day(current_step) if current_step else None,
                }
            }
        )


class ProgramCompleteDayView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def post(self, request, program_id: int):
        program = _program_or_404(program_id)
        activation = _activation_or_404(request.user, program)
        day_number_raw = request.data.get("day_number")
        try:
            day_number = (
                int(day_number_raw) if day_number_raw not in (None, "") else activation.progress_day
            )
        except (TypeError, ValueError):
            return Response(
                {"detail": "day_number trebuie sa fie un numar valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(complete_program_day_for_user(request.user, program, day_number=day_number))


class ProgramReflectionView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def get(self, request, program_id: int):
        program = _program_or_404(program_id)
        day_number_raw = request.query_params.get("day_number")
        if not day_number_raw:
            return Response(
                {"detail": "Parametrul day_number este obligatoriu."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            day_number = int(day_number_raw)
        except (TypeError, ValueError):
            return Response(
                {"detail": "day_number trebuie sa fie un numar valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reflection = ProgramReflection.objects.filter(
            user=request.user, program=program, day_number=day_number
        ).first()
        if not reflection:
            return Response(
                {"detail": "Nu exista reflectie pentru ziua ceruta."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(ProgramReflectionSerializer(reflection).data)

    @require_feature("programs_access")
    def post(self, request, program_id: int):
        program = _program_or_404(program_id)
        try:
            day_number = int(request.data.get("day_number") or 0)
        except (TypeError, ValueError):
            return Response(
                {"detail": "day_number trebuie sa fie un numar valid."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reflection_text = str(request.data.get("reflection_text") or "").strip()
        if day_number < 1 or not reflection_text:
            return Response(
                {"detail": "day_number si reflection_text sunt obligatorii."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reflection, _ = ProgramReflection.objects.update_or_create(
            user=request.user,
            program=program,
            day_number=day_number,
            defaults={
                "reflection_text": reflection_text,
                "ai_feedback": (
                    f"Ai surprins clar ziua {day_number}. Pastreaza ideea centrala si transforma-o intr-o actiune mica pentru maine."
                ),
            },
        )
        return Response(
            ProgramReflectionSerializer(reflection).data, status=status.HTTP_201_CREATED
        )


class ProgramProgressView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def get(self, request, program_id: int):
        activation = _activation_or_404(request.user, _program_or_404(program_id))
        return Response(serialize_activation(activation))


class ProgramPauseView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def post(self, request, program_id: int):
        activation = _activation_or_404(request.user, _program_or_404(program_id))
        activation.pause()
        return Response(serialize_activation(activation))


class ProgramResumeView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def post(self, request, program_id: int):
        activation = _activation_or_404(request.user, _program_or_404(program_id))
        activation.resume()
        return Response(serialize_activation(activation))


class ProgramStartView(ProgramActivateView):
    pass


class ProgramCompleteView(ProgramCompleteDayView):
    pass


class ProgramDayView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("programs_access")
    def get(self, request, program_id: int, day_number: int):
        program = _program_or_404(program_id)
        if not can_view_program(request.user, program):
            return Response(
                {"detail": "Program indisponibil pentru planul tau."},
                status=status.HTTP_403_FORBIDDEN,
            )
        day = get_object_or_404(program.days, day_number=day_number)
        return Response(serialize_day(day))

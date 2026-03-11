from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GuidedProgram, GuidedProgramDay, UserProgramProgress
from .serializers import (
    GuidedProgramSerializer,
    GuidedProgramDaySerializer,
    UserProgramProgressSerializer,
)


class ProgramListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.has_paid_access():
            return Response(
                {"detail": "Your trial or subscription has expired."},
                status=403,
            )
        language = request.query_params.get("language") or request.user.language or "en"
        qs = GuidedProgram.objects.filter(active=True, language=language)
        serializer = GuidedProgramSerializer(qs, many=True)
        return Response(serializer.data)


class ProgramDayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, program_id, day_number):
        if not request.user.has_paid_access():
            return Response(
                {"detail": "Your trial or subscription has expired."},
                status=403,
            )
        program = get_object_or_404(GuidedProgram, id=program_id, active=True)
        if program.is_premium and not request.user.has_paid_access():
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

    def get(self, request, program_id):
        if not request.user.has_paid_access():
            return Response({"detail": "Subscription expired."}, status=403)
        program = self._get_program(program_id)
        progress, _ = UserProgramProgress.objects.get_or_create(
            user=request.user, program=program
        )
        serializer = UserProgramProgressSerializer(progress)
        return Response(serializer.data)

    def post(self, request, program_id):
        if not request.user.has_paid_access():
            return Response({"detail": "Subscription expired."}, status=403)
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
        progress.mark_day_complete(day_number)
        serializer = UserProgramProgressSerializer(progress)
        return Response(serializer.data)

from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import GuidedProgram, GuidedProgramDay
from .serializers import GuidedProgramSerializer, GuidedProgramDaySerializer


class ProgramListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        language = request.query_params.get("language") or request.user.language or "en"
        qs = GuidedProgram.objects.filter(active=True, language=language)
        if not request.user.is_premium:
            qs = qs.filter(is_premium=False)
        serializer = GuidedProgramSerializer(qs, many=True)
        return Response(serializer.data)


class ProgramDayView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, program_id, day_number):
        program = get_object_or_404(GuidedProgram, id=program_id, active=True)
        if program.is_premium and not request.user.is_premium:
            return Response(
                {"detail": "This program requires a premium subscription."},
                status=403,
            )
        day = get_object_or_404(
            GuidedProgramDay, program=program, day_number=day_number
        )
        serializer = GuidedProgramDaySerializer(day)
        return Response(serializer.data)

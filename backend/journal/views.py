from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import JournalQuestion, JournalEntry
from .serializers import JournalQuestionSerializer, JournalEntrySerializer


class JournalQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        language = request.query_params.get("language") or request.user.language or "en"
        if language not in settings.SUPPORTED_LANGUAGES:
            language = "en"
        qs = JournalQuestion.objects.filter(active=True, language=language)
        serializer = JournalQuestionSerializer(qs, many=True)
        return Response(serializer.data)


class JournalEntriesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JournalEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

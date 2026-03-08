from rest_framework import serializers

from .models import GuidedProgram, GuidedProgramDay


class GuidedProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuidedProgram
        fields = ("id", "title", "description", "language", "active", "is_premium")


class GuidedProgramDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = GuidedProgramDay
        fields = ("id", "program", "day_number", "title", "content", "question", "ai_prompt")

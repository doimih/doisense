from rest_framework import serializers

from .models import GuidedProgram, GuidedProgramDay, ProgramReflection, UserProgramProgress


class GuidedProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuidedProgram
        fields = ("id", "title", "description", "language", "active", "is_premium")


class GuidedProgramDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = GuidedProgramDay
        fields = ("id", "program", "day_number", "title", "content", "question", "ai_prompt")


class UserProgramProgressSerializer(serializers.ModelSerializer):
    total_days = serializers.SerializerMethodField()

    class Meta:
        model = UserProgramProgress
        fields = (
            "id",
            "program",
            "current_day",
            "completed_days",
            "is_paused",
            "paused_at",
            "total_days",
            "started_at",
            "last_active_at",
        )
        read_only_fields = fields

    def get_total_days(self, obj):
        return obj.program.days.count()


class ProgramReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramReflection
        fields = (
            "id",
            "program",
            "day_number",
            "reflection_text",
            "ai_feedback",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "program", "ai_feedback", "created_at", "updated_at")

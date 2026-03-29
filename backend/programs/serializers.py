from rest_framework import serializers

from .models import GuidedProgram, GuidedProgramDay, ProgramReflection, UserProgramProgress


class GuidedProgramDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = GuidedProgramDay
        fields = (
            "id",
            "day_number",
            "title",
            "content",
            "task_type",
            "estimated_time_minutes",
            "question",
            "ai_prompt",
        )


class GuidedProgramSerializer(serializers.ModelSerializer):
    daily_steps = GuidedProgramDaySerializer(source="days", many=True, read_only=True)

    class Meta:
        model = GuidedProgram
        fields = (
            "id",
            "category",
            "title",
            "description",
            "duration_days",
            "plan_access",
            "language",
            "active",
            "is_premium",
            "daily_steps",
        )


class UserProgramProgressSerializer(serializers.ModelSerializer):
    total_days = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    progress_day = serializers.IntegerField(source="current_day", read_only=True)
    start_date = serializers.DateField(read_only=True)

    class Meta:
        model = UserProgramProgress
        fields = (
            "id",
            "program",
            "start_date",
            "current_day",
            "progress_day",
            "completed_days",
            "is_paused",
            "paused_at",
            "total_days",
            "status",
            "started_at",
            "completed_at",
            "last_active_at",
        )
        read_only_fields = fields

    def get_total_days(self, obj):
        return obj.program.days.count()

    def get_status(self, obj):
        return obj.status


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

from rest_framework import serializers

from .models import Task, TaskProgress


class TaskCreateUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=180)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    duration_minutes = serializers.IntegerField(
        min_value=5, max_value=600, required=False, default=15
    )
    frequency = serializers.ChoiceField(
        choices=[item[0] for item in Task.FREQUENCY_CHOICES],
        required=False,
        default=Task.FREQ_DAILY,
    )
    weekdays = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6), required=False, default=list
    )
    month_days = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=31), required=False, default=list
    )
    start_time = serializers.TimeField(required=False, allow_null=True)
    reminder_enabled = serializers.BooleanField(required=False, default=False)
    reminder_minutes_before = serializers.IntegerField(
        min_value=0, max_value=1440, required=False, default=10
    )
    advanced_options = serializers.JSONField(required=False, default=dict)
    starts_on = serializers.DateField(required=False)
    ends_on = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        starts_on = attrs.get("starts_on")
        ends_on = attrs.get("ends_on")
        if starts_on and ends_on and ends_on < starts_on:
            raise serializers.ValidationError({"ends_on": "ends_on must be after starts_on"})
        return attrs


class TaskCheckSerializer(serializers.Serializer):
    progress_date = serializers.DateField(required=False)
    completed = serializers.BooleanField(required=False, default=True)
    note = serializers.CharField(required=False, allow_blank=True, max_length=280, default="")


class TaskProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskProgress
        fields = [
            "id",
            "task_id",
            "progress_date",
            "is_completed",
            "completed_at",
            "note",
            "mood_score",
            "energy_score",
            "created_at",
            "updated_at",
        ]

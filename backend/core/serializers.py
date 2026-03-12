from rest_framework import serializers

from .models import CMSPage, UserWellbeingCheckin
from .analytics import EVENT_SCHEMA


class CMSPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSPage
        fields = (
            "id",
            "slug",
            "title",
            "language",
            "content",
            "is_published",
            "show_in_header",
            "show_in_footer",
            "menu_order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class WellbeingCheckinCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWellbeingCheckin
        fields = ("mood", "energy_level")

    def validate(self, attrs):
        mood = attrs.get("mood", "")
        energy_level = attrs.get("energy_level")

        if not mood and energy_level is None:
            raise serializers.ValidationError("Provide at least mood or energy_level.")

        if energy_level is not None and not (1 <= int(energy_level) <= 5):
            raise serializers.ValidationError({"energy_level": "Energy must be between 1 and 5."})

        return attrs


class AnalyticsTrackSerializer(serializers.Serializer):
    event_name = serializers.ChoiceField(choices=sorted(EVENT_SCHEMA.keys()))
    source = serializers.ChoiceField(choices=["frontend", "backend", "system"], default="frontend")
    session_id = serializers.CharField(required=False, allow_blank=True, max_length=128)
    properties = serializers.JSONField(required=False)

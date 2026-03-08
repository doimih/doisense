from rest_framework import serializers

from core.validators import validate_language
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "preferred_tone",
            "sensitivities",
            "communication_style",
            "emotional_baseline",
            "keywords",
        )

    def validate_keywords(self, value):
        if not isinstance(value, (dict, list)):
            raise serializers.ValidationError("keywords must be a JSON object or array")
        return value

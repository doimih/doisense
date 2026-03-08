from rest_framework import serializers

from .models import JournalQuestion, JournalEntry


class JournalQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalQuestion
        fields = ("id", "text", "category", "language", "tags", "active")


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = ("id", "question", "content", "emotions", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_content(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty")
        max_len = 10000
        if len(value) > max_len:
            raise serializers.ValidationError(f"Content must be at most {max_len} characters")
        return value.strip()

    def validate_emotions(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("emotions must be a list")
        return value

    def validate_question(self, value):
        if not value.active:
            raise serializers.ValidationError("This question is not active")
        return value

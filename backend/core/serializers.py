from rest_framework import serializers

from .models import CMSPage


class CMSPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CMSPage
        fields = (
            "id",
            "slug",
            "title",
            "content",
            "is_published",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

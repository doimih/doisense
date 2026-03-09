from rest_framework import serializers

from .models import CMSPage


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

from django import forms
from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "preferred_tone",
        "communication_style",
        "emotional_baseline",
    )
    search_fields = ("user__email",)
    list_filter = ("preferred_tone", "communication_style", "emotional_baseline")
    fieldsets = (
        (
            "User",
            {
                "fields": ("user",),
            },
        ),
        (
            "Profile Settings",
            {
                "fields": (
                    "preferred_tone",
                    "communication_style",
                    "emotional_baseline",
                    "sensitivities",
                ),
            },
        ),
        (
            "Keywords",
            {
                "fields": ("keywords",),
                "description": "Use JSON format, for example: {\"goal\": \"focus\"}.",
            },
        ),
    )
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "sensitivities":
            kwargs["widget"] = forms.Textarea(attrs={"rows": 4})
        if db_field.name == "keywords":
            kwargs["widget"] = forms.Textarea(attrs={"rows": 6, "style": "font-family: monospace;"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

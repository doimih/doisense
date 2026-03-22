import json

from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import JournalQuestion, JournalEntry


class JournalQuestionAdminForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Use tags separated by comma or new line (example: obiectiv, succes, motivatie).",
        label="Tags",
    )

    class Meta:
        model = JournalQuestion
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and isinstance(self.instance.tags, list):
            self.fields["tags"].initial = ", ".join(str(item) for item in self.instance.tags if item)

    def clean_tags(self):
        raw_value = (self.cleaned_data.get("tags") or "").strip()
        if not raw_value:
            return []

        # Allow advanced users to still paste a JSON array when needed.
        if raw_value.startswith("["):
            try:
                parsed = json.loads(raw_value)
            except json.JSONDecodeError as exc:
                raise forms.ValidationError("Invalid JSON array for tags.") from exc

            if not isinstance(parsed, list):
                raise forms.ValidationError("Tags JSON must be an array.")

            return [str(item).strip() for item in parsed if str(item).strip()]

        normalized = raw_value.replace("\n", ",")
        parts = [part.strip() for part in normalized.split(",")]
        return [part for part in parts if part]


@admin.register(JournalQuestion)
class JournalQuestionAdmin(admin.ModelAdmin):
    form = JournalQuestionAdminForm
    change_form_template = "admin/two_column_change_form.html"
    list_display = ("id", "text", "category", "language", "active", "delete_link")
    list_filter = ("language", "active")
    actions_on_top = True
    actions_on_bottom = False
    fieldsets = (
        (
            "Configurare",
            {
                "fields": (
                    "category",
                    "language",
                    "active",
                )
            },
        ),
        (
            "Conținut",
            {
                "fields": (
                    "text",
                    "tags",
                )
            },
        ),
    )

    def delete_link(self, obj):
        url = reverse("admin:journal_journalquestion_delete", args=[obj.pk])
        return format_html(
            (
                '<a href="{}" title="Delete" '
                'style="color:#dc2626; display:inline-flex; align-items:center;" '
                'aria-label="Delete">'
                '<span class="material-symbols-outlined" style="font-size:18px;">delete</span>'
                "</a>"
            ),
            url,
        )

    delete_link.short_description = "Delete"


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "created_at")
    list_filter = ("created_at",)
    readonly_fields = ("user", "question", "content", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

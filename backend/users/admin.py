from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.audit import extract_form_changes, log_admin_change

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "language",
        "is_premium",
        "vip_manual_override",
        "early_discount_eligible",
        "is_staff",
        "created_at",
    )
    list_filter = ("is_premium", "vip_manual_override", "early_discount_eligible", "is_staff")
    search_fields = ("email",)
    ordering = ("-created_at",)
    readonly_fields = ("early_discount_eligible",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Profile",
            {
                "fields": (
                    "language",
                    "is_premium",
                    "vip_manual_override",
                    "early_discount_eligible",
                )
            },
        ),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )

    def save_model(self, request, obj, form, change):
        before_data, after_data = extract_form_changes(form)
        super().save_model(request, obj, form, change)
        if change and form.changed_data:
            log_admin_change(
                actor=request.user,
                action="user_updated",
                target_obj=obj,
                before_data=before_data,
                after_data=after_data,
                reason="User account/plan updated from admin",
            )

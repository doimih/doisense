from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html

from core.audit import extract_form_changes, log_admin_change

from .models import User

_AVATAR_COLORS = [
    ("bg-violet-100", "text-violet-700"),
    ("bg-blue-100", "text-blue-700"),
    ("bg-teal-100", "text-teal-700"),
    ("bg-amber-100", "text-amber-700"),
    ("bg-rose-100", "text-rose-700"),
    ("bg-emerald-100", "text-emerald-700"),
    ("bg-orange-100", "text-orange-700"),
    ("bg-indigo-100", "text-indigo-700"),
]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    change_list_template = "admin/users/user/change_list.html"
    list_before_template = "admin/users/user/before_list.html"
    list_display = (
        "user_display",
        "email",
        "role_display",
        "status_display",
        "last_login_display",
        "created_at_display",
        "row_actions",
    )
    list_display_links = ("user_display",)
    list_filter = ("is_active", "is_staff", "is_superuser", "is_premium", "plan_tier")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-created_at",)
    readonly_fields = ("early_discount_eligible", "change_password_link")
    fieldsets = (
        (None, {"fields": ("email", "password", "change_password_link")}),
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

    # ── display helpers ──────────────────────────────────────────────────────

    def user_display(self, obj):
        name = f"{obj.first_name} {obj.last_name}".strip() or obj.email
        if obj.first_name and obj.last_name:
            initials = f"{obj.first_name[0]}{obj.last_name[0]}".upper()
        elif obj.first_name:
            initials = obj.first_name[:2].upper()
        else:
            initials = obj.email[:2].upper()
        bg, fg = _AVATAR_COLORS[(obj.pk or 0) % len(_AVATAR_COLORS)]
        return format_html(
            '<div class="flex items-center gap-2">'
            '<span class="inline-flex h-8 w-8 shrink-0 items-center justify-center'
            ' rounded-full text-xs font-bold {} {}">{}</span>'
            '<span class="font-medium text-sm">{}</span>'
            "</div>",
            bg, fg, initials, name,
        )

    user_display.short_description = "Utilizator"
    user_display.allow_tags = True

    def role_display(self, obj):
        if obj.is_superuser:
            return format_html(
                '<span class="inline-flex items-center gap-1 rounded-full border'
                ' border-violet-200 bg-violet-50 px-2 py-0.5 text-xs font-semibold text-violet-700">'
                '<span class="material-symbols-outlined" style="font-size:13px">admin_panel_settings</span>'
                " Admin</span>"
            )
        if obj.is_staff:
            return format_html(
                '<span class="inline-flex items-center gap-1 rounded-full border'
                ' border-blue-200 bg-blue-50 px-2 py-0.5 text-xs font-semibold text-blue-700">'
                '<span class="material-symbols-outlined" style="font-size:13px">manage_accounts</span>'
                " Staff</span>"
            )
        if obj.is_premium:
            return format_html(
                '<span class="inline-flex items-center gap-1 rounded-full border'
                ' border-amber-200 bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700">'
                '<span class="material-symbols-outlined" style="font-size:13px">star</span>'
                " Premium</span>"
            )
        return format_html(
            '<span class="inline-flex items-center gap-1 rounded-full border'
            ' border-stone-200 bg-stone-50 px-2 py-0.5 text-xs font-semibold text-stone-500">'
            '<span class="material-symbols-outlined" style="font-size:13px">person</span>'
            " User</span>"
        )

    role_display.short_description = "Rol"

    def status_display(self, obj):
        if obj.is_active:
            return format_html(
                '<span class="text-xs font-semibold text-emerald-600">Activ</span>'
            )
        return format_html(
            '<span class="inline-flex rounded-full bg-stone-100 px-2 py-0.5 text-xs font-semibold text-stone-500">Inactiv</span>'
        )

    status_display.short_description = "Status"

    def last_login_display(self, obj):
        if not obj.last_login:
            return format_html('<span class="text-stone-400 text-xs">—</span>')
        return format_html(
            '<span class="text-sm">{}</span>',
            obj.last_login.strftime("%d.%m.%Y %H:%M"),
        )

    last_login_display.short_description = "Ultima autentificare"

    def created_at_display(self, obj):
        return format_html(
            '<span class="text-sm">{}</span>',
            obj.created_at.strftime("%d.%m.%Y"),
        )

    created_at_display.short_description = "Înregistrat"

    def row_actions(self, obj):
        edit_url = reverse("admin:users_user_change", args=[obj.pk])
        delete_url = reverse("admin:users_user_delete", args=[obj.pk])
        return format_html(
            '<div class="flex items-center gap-2">'
            '<a href="{}" class="text-stone-400 hover:text-stone-800" title="Editează">'
            '<span class="material-symbols-outlined" style="font-size:18px">edit</span></a>'
            '<a href="{}" class="text-stone-400 hover:text-red-600" title="Șterge">'
            '<span class="material-symbols-outlined" style="font-size:18px">delete</span></a>'
            "</div>",
            edit_url,
            delete_url,
        )

    row_actions.short_description = "Acțiuni"

    # ── views ────────────────────────────────────────────────────────────────

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["user_stats"] = {
            "total": User.objects.count(),
            "active": User.objects.filter(is_active=True).count(),
            "admins": User.objects.filter(is_superuser=True).count(),
            "premium": User.objects.filter(is_premium=True).count(),
        }
        return super().changelist_view(request, extra_context=extra_context)

    # ── other helpers ────────────────────────────────────────────────────────

    def change_password_link(self, obj):
        if not obj or not obj.pk:
            return "Salveaza utilizatorul pentru a schimba parola."
        url = reverse("admin:auth_user_password_change", args=[obj.pk])
        return format_html('<a class="button" href="{}">Schimba parola</a>', url)

    change_password_link.short_description = "Parola"

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

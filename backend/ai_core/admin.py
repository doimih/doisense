from pathlib import Path

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from unfold.admin import ModelAdmin

from core.audit import extract_form_changes, log_admin_change

from .auditor import audit_prompt
from .forms import PromptAdminForm
from .monitoring import build_ai_health_dashboard_context
from .models import Prompt, PromptVersion
from .modifier import suggest_improved_prompt
from .orchestrator import build_final_prompt


def ai_health_dashboard(request):
    if not request.user.has_perm("ai_core.view_prompt"):
        raise PermissionDenied

    context = {
        **admin.site.each_context(request),
        "title": "AI Health Dashboard",
    }
    context.update(build_ai_health_dashboard_context(hours=24))
    return TemplateResponse(request, "admin/ai_core/dashboard.html", context)


def _patch_admin_urls() -> None:
    if getattr(admin.site, "_ai_core_dashboard_patched", False):
        return

    original_get_urls = admin.site.get_urls

    def get_urls_with_dashboard():
        custom_urls = [
            path(
                "ai_core/dashboard/",
                admin.site.admin_view(ai_health_dashboard),
                name="ai_core_dashboard",
            ),
        ]
        return custom_urls + original_get_urls()

    admin.site.get_urls = get_urls_with_dashboard
    admin.site._ai_core_dashboard_patched = True


_patch_admin_urls()


@admin.register(Prompt)
class PromptAdmin(ModelAdmin):
    form = PromptAdminForm
    change_form_template = "admin/prompt_change_form.html"
    list_display = ("name", "type", "language", "updated_at")
    list_filter = ("type", "language")
    search_fields = ("name", "content")
    ordering = ("type", "name")
    readonly_fields = ("ai_brain_actions", "recent_versions")

    fieldsets = (
        (
            "Prompt",
            {
                "fields": (
                    "name",
                    "type",
                    "language",
                    "content",
                ),
                "description": "All prompts must be written in English.",
            },
        ),
        (
            "AI Brain Actions",
            {
                "fields": ("ai_brain_actions", "recent_versions"),
                "description": "Use these tools to analyze and improve this prompt using the platform AI.",
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "tools/audit/",
                self.admin_site.admin_view(self.audit_hub_view),
                name="ai_core_prompt_audit_hub",
            ),
            path(
                "tools/improve/",
                self.admin_site.admin_view(self.improve_hub_view),
                name="ai_core_prompt_improve_hub",
            ),
            path(
                "tools/preview/",
                self.admin_site.admin_view(self.preview_hub_view),
                name="ai_core_prompt_preview_hub",
            ),
            path(
                "dashboard/",
                self.admin_site.admin_view(self.dashboard_redirect_view),
                name="ai_core_prompt_dashboard_redirect",
            ),
            path(
                "<path:object_id>/audit/",
                self.admin_site.admin_view(self.audit_view),
                name="ai_core_prompt_audit",
            ),
            path(
                "<path:object_id>/improve/",
                self.admin_site.admin_view(self.improve_view),
                name="ai_core_prompt_improve",
            ),
            path(
                "<path:object_id>/preview/",
                self.admin_site.admin_view(self.preview_view),
                name="ai_core_prompt_preview",
            ),
        ]
        return custom_urls + urls

    def _tool_hub_context(self, request, *, title: str, tool: str) -> dict:
        prompts = Prompt.objects.order_by("type", "name")
        rows = []
        for prompt in prompts:
            rows.append(
                {
                    "id": prompt.pk,
                    "name": prompt.name,
                    "type": prompt.get_type_display(),
                    "language": prompt.language,
                    "edit_url": reverse("admin:ai_core_prompt_change", args=[prompt.pk]),
                    "action_url": reverse(f"admin:ai_core_prompt_{tool}", args=[prompt.pk]),
                }
            )

        action_label = {
            "audit": "Run Audit",
            "improve": "Generate Improvement",
            "preview": "Generate Preview",
        }.get(tool, "Open")

        return {
            **self.admin_site.each_context(request),
            "title": title,
            "tool": tool,
            "rows": rows,
            "action_label": action_label,
        }

    def audit_hub_view(self, request, *args, **kwargs):
        context = self._tool_hub_context(request, title="Audit Prompt", tool="audit")
        return TemplateResponse(request, "admin/ai_core/prompt_tools_hub.html", context)

    def improve_hub_view(self, request, *args, **kwargs):
        context = self._tool_hub_context(request, title="Improve Prompt", tool="improve")
        return TemplateResponse(request, "admin/ai_core/prompt_tools_hub.html", context)

    def preview_hub_view(self, request, *args, **kwargs):
        context = self._tool_hub_context(request, title="Orchestrator Preview", tool="preview")
        return TemplateResponse(request, "admin/ai_core/prompt_tools_hub.html", context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            extra_context["ai_brain_action_result"] = request.session.get(
                self._admin_result_key(int(object_id)), None
            )
        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        before_data, after_data = extract_form_changes(form)
        obj._updated_by = request.user.get_username() or request.user.email or str(request.user.pk)
        super().save_model(request, obj, form, change)
        if change and form.changed_data:
            log_admin_change(
                actor=request.user,
                action="ai_brain_prompt_updated",
                target_obj=obj,
                before_data=before_data,
                after_data=after_data,
                reason="AI Brain prompt updated from admin",
            )

    def _admin_result_key(self, prompt_id: int) -> str:
        return f"ai_brain_result:{prompt_id}"

    def _store_admin_result(self, request, prompt_id: int, payload: dict) -> None:
        request.session[self._admin_result_key(prompt_id)] = payload

    def _legacy_prompt_for_type(self, prompt_type: str) -> str:
        repo_root = Path(__file__).resolve().parents[1]
        mapping = {
            Prompt.TYPE_SYSTEM: repo_root / "templates" / "ai_prompts" / "orchestrator.txt",
            Prompt.TYPE_PERSONALITY: repo_root / "templates" / "ai_prompts" / "chat.txt",
            Prompt.TYPE_RULES: repo_root / "templates" / "ai_prompts" / "chat.txt",
            Prompt.TYPE_CONTEXT: repo_root / "templates" / "ai_prompts" / "chat.txt",
            Prompt.TYPE_GREETING: repo_root / "templates" / "ai_prompts" / "chat.txt",
            Prompt.TYPE_FALLBACK: repo_root / "templates" / "ai_prompts" / "chat.txt",
            Prompt.TYPE_SKILL: repo_root / "templates" / "ai_prompts" / "guided_program.txt",
        }
        path = mapping.get(prompt_type)
        if not path:
            return ""
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""

    def _change_url(self, prompt: Prompt) -> str:
        return reverse("admin:ai_core_prompt_change", args=[prompt.pk])

    @admin.display(description="Actions")
    def ai_brain_actions(self, obj):
        if not obj.pk:
            return "Save the prompt first to enable AI Brain actions."
        audit_url = reverse("admin:ai_core_prompt_audit", args=[obj.pk])
        improve_url = reverse("admin:ai_core_prompt_improve", args=[obj.pk])
        dashboard_url = reverse("admin:ai_core_dashboard")
        return format_html(
            '<div style="display:flex; gap:12px; flex-wrap:wrap; padding:4px 0;">'
            '<a href="{}" style="display:inline-flex; align-items:center; gap:6px; '
            "padding:10px 20px; background:#7c3aed; color:#fff; border-radius:8px; "
            "font-weight:600; font-size:14px; text-decoration:none; "
            'box-shadow:0 1px 3px rgba(0,0,0,.2);">'
            "🔍 Audit Prompt</a>"
            '<a href="{}" style="display:inline-flex; align-items:center; gap:6px; '
            "padding:10px 20px; background:#059669; color:#fff; border-radius:8px; "
            "font-weight:600; font-size:14px; text-decoration:none; "
            'box-shadow:0 1px 3px rgba(0,0,0,.2);">'
            "✨ Improve Prompt</a>"
            '<a href="{}" style="display:inline-flex; align-items:center; gap:6px; '
            "padding:10px 20px; background:#0f766e; color:#fff; border-radius:8px; "
            "font-weight:600; font-size:14px; text-decoration:none; "
            'box-shadow:0 1px 3px rgba(0,0,0,.2);">'
            "📊 AI Health Dashboard</a>"
            "</div>",
            audit_url,
            improve_url,
            dashboard_url,
        )

    def dashboard_redirect_view(self, request, *args, **kwargs):
        return redirect("admin:ai_core_dashboard")

    def audit_view(self, request, object_id, *args, **kwargs):
        prompt = get_object_or_404(Prompt, pk=object_id)
        report = audit_prompt(prompt, legacy_prompt_text=self._legacy_prompt_for_type(prompt.type))
        log_admin_change(
            actor=request.user,
            action="ai_brain_prompt_audited",
            target_obj=prompt,
            before_data={},
            after_data={
                "summary": report.get("summary", ""),
                "issues_count": len(report.get("issues", [])),
                "recommendations_count": len(report.get("recommendations", [])),
            },
            reason="AI Brain prompt audited from admin",
        )
        self._store_admin_result(
            request,
            prompt.pk,
            {
                "kind": "audit",
                "title": "Prompt Audit",
                "report": report,
            },
        )
        messages.success(request, "Prompt audit completed.")
        return redirect(self._change_url(prompt))

    def improve_view(self, request, object_id, *args, **kwargs):
        prompt = get_object_or_404(Prompt, pk=object_id)

        if request.method == "POST":
            session_payload = request.session.get(self._admin_result_key(prompt.pk), {})
            improvement = session_payload.get("improvement") or {}

            if "_discard_improvement" in request.POST:
                request.session.pop(self._admin_result_key(prompt.pk), None)
                messages.info(request, "Suggested prompt improvement discarded.")
                return redirect(self._change_url(prompt))

            if "_apply_improvement" in request.POST:
                improved_prompt = improvement.get("improved_prompt")
                if not improved_prompt:
                    messages.error(request, "No suggested improvement is available to apply.")
                    return redirect(self._change_url(prompt))

                previous_content = prompt.content
                prompt.content = improved_prompt
                prompt._updated_by = (
                    request.user.get_username() or request.user.email or str(request.user.pk)
                )
                prompt._change_reason = "Applied AI Brain prompt improvement"
                prompt.save()
                log_admin_change(
                    actor=request.user,
                    action="ai_brain_prompt_improved",
                    target_obj=prompt,
                    before_data={"content": previous_content},
                    after_data={"content": prompt.content},
                    reason="Applied suggested AI Brain prompt improvement",
                )
                request.session.pop(self._admin_result_key(prompt.pk), None)
                messages.success(request, "Suggested prompt improvement applied.")
                return redirect(self._change_url(prompt))

        improvement = suggest_improved_prompt(prompt)
        self._store_admin_result(
            request,
            prompt.pk,
            {
                "kind": "improvement",
                "title": "Prompt Improvement",
                "improvement": improvement,
                "improve_url": reverse("admin:ai_core_prompt_improve", args=[prompt.pk]),
            },
        )
        messages.success(request, "Prompt improvement suggestion generated.")
        return redirect(self._change_url(prompt))

    def preview_view(self, request, object_id, *args, **kwargs):
        prompt = get_object_or_404(Prompt, pk=object_id)
        preview = build_final_prompt(
            user_message="I feel overwhelmed today and I need structured wellness support.",
            skill_name=prompt.name if prompt.type == Prompt.TYPE_SKILL else None,
            include_greeting=True,
        )
        self._store_admin_result(
            request,
            prompt.pk,
            {
                "kind": "preview",
                "title": "Orchestrator Preview",
                "preview": preview,
            },
        )
        messages.success(request, "Orchestrator preview generated.")
        return redirect(self._change_url(prompt))

    @admin.display(description="Automatic version history")
    def recent_versions(self, obj):
        if not obj.pk:
            return "The first version is created automatically after the prompt is saved."

        versions = obj.versions.order_by("-version_number", "-updated_at")[:10]
        if not versions:
            return "No automatic versions have been recorded yet."

        return format_html(
            '<div style="display:grid; gap:8px;">{}</div>',
            format_html_join(
                "",
                (
                    '<div style="padding:10px; border:1px solid var(--border-color, #ddd); border-radius:8px;">'
                    "<strong>v{}</strong> - {}<br>"
                    '<span style="color:var(--body-quiet-color, #666);">{}</span>'
                    "</div>"
                ),
                (
                    (
                        version.version_number,
                        version.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                        version.change_reason or "Automatic version snapshot",
                    )
                    for version in versions
                ),
            ),
        )


@admin.register(PromptVersion)
class PromptVersionAdmin(ModelAdmin):
    list_display = ("prompt", "version_number", "updated_at", "updated_by")
    list_filter = ("prompt", "updated_at")
    search_fields = ("prompt__name", "content_snapshot", "updated_by", "change_reason")
    ordering = ("-version_number", "-updated_at")
    readonly_fields = (
        "prompt",
        "version_number",
        "type_snapshot",
        "language_snapshot",
        "content_snapshot",
        "updated_at",
        "updated_by",
        "change_reason",
    )

    fieldsets = (
        (
            "Prompt Version",
            {
                "fields": (
                    "prompt",
                    "version_number",
                    "type_snapshot",
                    "language_snapshot",
                    "content_snapshot",
                    "updated_at",
                    "updated_by",
                    "change_reason",
                ),
                "description": "Version snapshots are created automatically by the application and are read-only in admin.",
            },
        ),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        return None

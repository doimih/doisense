from pathlib import Path
from uuid import uuid4

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from unfold.admin import ModelAdmin

from core.audit import extract_form_changes, log_admin_change

from .auditor import audit_prompt
from .forms import PromptAdminForm
from .monitoring import build_ai_health_dashboard_context
from .models import Prompt, PromptVersion, SocialMediaPost, SocialMediaSettings
from .modifier import suggest_improved_prompt
from .orchestrator import build_final_prompt
from .publish_instagram import publish_to_instagram
from .publish_linkedin import publish_to_linkedin
from .publish_tiktok import publish_to_tiktok
from .social_media import generate_social_image, generate_social_post, save_generated_post


PLATFORM_MEDIA_SPECS = {
    SocialMediaPost.PLATFORM_INSTAGRAM: {
        "image": "1080 x 1350 px (recommended feed portrait)",
        "video": "1080 x 1920 px, 9:16 (Reels)",
    },
    SocialMediaPost.PLATFORM_TIKTOK: {
        "image": "1080 x 1920 px (cover/creative)",
        "video": "1080 x 1920 px, 9:16 (required format)",
    },
    SocialMediaPost.PLATFORM_LINKEDIN: {
        "image": "1200 x 627 px (shared post image)",
        "video": "1920 x 1080 px, 16:9 (recommended)",
    },
}


def _sanitize_media_folder(folder: str, default: str) -> str:
    cleaned = (folder or "").strip().strip("/")
    return cleaned or default


def _save_uploaded_media(file_obj, target_folder: str) -> str:
    safe_name = Path(file_obj.name).name
    unique_name = f"{uuid4().hex}_{safe_name}"
    relative_path = f"{target_folder}/{unique_name}".strip("/")
    stored_path = default_storage.save(relative_path, file_obj)
    return default_storage.url(stored_path)


def ai_health_dashboard(request):
    if not request.user.has_perm("ai_core.view_prompt"):
        raise PermissionDenied

    context = {
        **admin.site.each_context(request),
        "title": "AI Health Dashboard",
    }
    context.update(build_ai_health_dashboard_context(hours=24))
    return TemplateResponse(request, "admin/ai_core/dashboard.html", context)


def social_generator_view(request):
    if not request.user.has_perm("ai_core.add_socialmediapost"):
        raise PermissionDenied

    generated = None
    selected_platform = SocialMediaPost.PLATFORM_INSTAGRAM
    topic = ""

    settings_obj = SocialMediaSettings.load()
    media_image_folder = _sanitize_media_folder(settings_obj.media_image_folder, "social/images")
    media_video_folder = _sanitize_media_folder(settings_obj.media_video_folder, "social/videos")

    if request.method == "POST":
        action = request.POST.get("action", "generate")
        selected_platform = request.POST.get("platform", SocialMediaPost.PLATFORM_INSTAGRAM).lower().strip()
        topic = request.POST.get("topic", "").strip()
        uploaded_image = request.FILES.get("image_file")
        uploaded_video = request.FILES.get("video_file")
        image_media_path = (request.POST.get("image_media_path") or "").strip().lstrip("/")
        video_media_path = (request.POST.get("video_media_path") or "").strip().lstrip("/")

        uploaded_image_url = ""
        uploaded_video_url = ""

        if uploaded_image:
            uploaded_image_url = _save_uploaded_media(uploaded_image, media_image_folder)
            messages.success(request, f"Image uploaded to media folder: {media_image_folder}")
        elif image_media_path:
            uploaded_image_url = default_storage.url(image_media_path)

        if uploaded_video:
            uploaded_video_url = _save_uploaded_media(uploaded_video, media_video_folder)
            messages.success(request, f"Video uploaded to media folder: {media_video_folder}")
        elif video_media_path:
            uploaded_video_url = default_storage.url(video_media_path)

        if action == "generate":
            generated = generate_social_post(topic=topic, platform=selected_platform)
            generated["image_url"] = uploaded_image_url or generate_social_image(
                f"{generated.get('wellness_topic', topic)} {selected_platform} social post"
            )
            generated["video_url"] = uploaded_video_url
            saved = save_generated_post(
                {
                    **generated,
                    "status": SocialMediaPost.STATUS_DRAFT,
                    "publish_log": "Auto-saved from Social Media Generator.",
                }
            )
            generated["saved_post_id"] = saved.pk
            messages.success(request, f"Post generated and saved as draft (ID: {saved.pk}).")
        elif action == "save":
            post_id = request.POST.get("post_id", "").strip()
            data = {
                "platform": selected_platform,
                "title": request.POST.get("title", "").strip(),
                "body": request.POST.get("body", "").strip(),
                "hashtags": request.POST.get("hashtags", "").strip(),
                "image_url": uploaded_image_url or request.POST.get("image_url", "").strip(),
                "video_url": uploaded_video_url or request.POST.get("video_url", "").strip(),
                "wellness_topic": request.POST.get("wellness_topic", topic).strip() or topic,
                "status": SocialMediaPost.STATUS_DRAFT,
            }
            if post_id:
                post = SocialMediaPost.objects.filter(pk=post_id).first()
                if post:
                    post.platform = data["platform"]
                    post.title = data["title"]
                    post.body = data["body"]
                    post.hashtags = data["hashtags"]
                    post.image_url = data["image_url"]
                    post.video_url = data["video_url"]
                    post.wellness_topic = data["wellness_topic"]
                    post.status = SocialMediaPost.STATUS_DRAFT
                    post.publish_log = (post.publish_log + "\nSaved from Social Media Generator.").strip()
                    post.save()
                    messages.success(request, f"Draft post #{post.pk} updated.")
                    generated = {
                        **data,
                        "saved_post_id": post.pk,
                    }
                else:
                    saved = save_generated_post({**data, "publish_log": "Saved from Social Media Generator."})
                    messages.success(request, f"Draft post #{saved.pk} saved.")
                    generated = {
                        **data,
                        "saved_post_id": saved.pk,
                    }
            else:
                saved = save_generated_post({**data, "publish_log": "Saved from Social Media Generator."})
                messages.success(request, f"Draft post #{saved.pk} saved.")
                generated = {
                    **data,
                    "saved_post_id": saved.pk,
                }

    context = {
        **admin.site.each_context(request),
        "title": "Social Media Generator",
        "generated": generated,
        "selected_platform": selected_platform,
        "topic": topic,
        "platform_choices": SocialMediaPost.PLATFORM_CHOICES,
        "platform_media_specs": PLATFORM_MEDIA_SPECS,
        "media_image_folder": media_image_folder,
        "media_video_folder": media_video_folder,
    }
    return TemplateResponse(request, "admin/ai_core/social_generator.html", context)


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
            path(
                "ai_core/social-generator/",
                admin.site.admin_view(social_generator_view),
                name="ai_core_social_generator",
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
            'padding:10px 20px; background:#7c3aed; color:#fff; border-radius:8px; '
            'font-weight:600; font-size:14px; text-decoration:none; '
            'box-shadow:0 1px 3px rgba(0,0,0,.2);">'
            '🔍 Audit Prompt</a>'
            '<a href="{}" style="display:inline-flex; align-items:center; gap:6px; '
            'padding:10px 20px; background:#059669; color:#fff; border-radius:8px; '
            'font-weight:600; font-size:14px; text-decoration:none; '
            'box-shadow:0 1px 3px rgba(0,0,0,.2);">'
            '✨ Improve Prompt</a>'
            '<a href="{}" style="display:inline-flex; align-items:center; gap:6px; '
            'padding:10px 20px; background:#0f766e; color:#fff; border-radius:8px; '
            'font-weight:600; font-size:14px; text-decoration:none; '
            'box-shadow:0 1px 3px rgba(0,0,0,.2);">'
            '📊 AI Health Dashboard</a>'
            '</div>',
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
                prompt._updated_by = request.user.get_username() or request.user.email or str(request.user.pk)
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
                    '<strong>v{}</strong> - {}<br>'
                    '<span style="color:var(--body-quiet-color, #666);">{}</span>'
                    '</div>'
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


@admin.register(SocialMediaPost)
class SocialMediaPostAdmin(ModelAdmin):
    list_display = ("platform", "title", "wellness_topic", "status", "created_at")
    list_filter = ("platform", "wellness_topic", "status")
    search_fields = ("title", "body")
    readonly_fields = ("created_at", "posted_at", "publish_log")
    actions = [
        "publish_selected_to_instagram",
        "publish_selected_to_tiktok",
        "publish_selected_to_linkedin",
    ]

    def _publish_queryset(self, request, queryset, platform: str, publisher):
        success_count = 0
        skipped_count = 0
        fail_count = 0

        for post in queryset:
            if post.platform != platform:
                skipped_count += 1
                post.publish_log = (
                    post.publish_log
                    + f"\nSkipped publish action because post platform is {post.platform}, not {platform}."
                ).strip()
                post.save(update_fields=["publish_log"])
                continue

            ok, _ = publisher(post)
            if ok:
                success_count += 1
            else:
                fail_count += 1

        if success_count:
            self.message_user(request, f"Published {success_count} post(s) to {platform.title()}.", level=messages.SUCCESS)
        if fail_count:
            self.message_user(request, f"{fail_count} post(s) failed publishing to {platform.title()}. Check publish_log.", level=messages.ERROR)
        if skipped_count:
            self.message_user(
                request,
                f"Skipped {skipped_count} post(s) because selected platform did not match action target.",
                level=messages.WARNING,
            )

    @admin.action(description="Publish to Instagram")
    def publish_selected_to_instagram(self, request, queryset):
        self._publish_queryset(request, queryset, SocialMediaPost.PLATFORM_INSTAGRAM, publish_to_instagram)

    @admin.action(description="Publish to TikTok")
    def publish_selected_to_tiktok(self, request, queryset):
        self._publish_queryset(request, queryset, SocialMediaPost.PLATFORM_TIKTOK, publish_to_tiktok)

    @admin.action(description="Publish to LinkedIn")
    def publish_selected_to_linkedin(self, request, queryset):
        self._publish_queryset(request, queryset, SocialMediaPost.PLATFORM_LINKEDIN, publish_to_linkedin)


@admin.register(SocialMediaSettings)
class SocialMediaSettingsAdmin(ModelAdmin):
    fieldsets = (
        (
            "Media",
            {
                "fields": (
                    "media_image_folder",
                    "media_video_folder",
                ),
                "description": "Subfolders relative to MEDIA_ROOT where uploads from Social Generator are stored.",
                "classes": ("tab",),
            },
        ),
        (
            "Instagram",
            {
                "fields": (
                    "instagram_app_id",
                    "instagram_app_secret",
                    "instagram_access_token",
                    "instagram_refresh_token",
                    "instagram_business_account_id",
                    "instagram_token_expires_at",
                ),
                "classes": ("tab",),
            },
        ),
        (
            "TikTok",
            {
                "fields": (
                    "tiktok_app_id",
                    "tiktok_app_secret",
                    "tiktok_access_token",
                    "tiktok_refresh_token",
                ),
                "classes": ("tab",),
            },
        ),
        (
            "LinkedIn",
            {
                "fields": (
                    "linkedin_client_id",
                    "linkedin_client_secret",
                    "linkedin_access_token",
                    "linkedin_refresh_token",
                    "linkedin_organization_id",
                    "linkedin_token_expires_at",
                ),
                "classes": ("tab",),
            },
        ),
    )

    def has_add_permission(self, request):
        if SocialMediaSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        settings_obj = SocialMediaSettings.load()
        return redirect(reverse("admin:ai_core_socialmediasettings_change", args=[settings_obj.pk]))

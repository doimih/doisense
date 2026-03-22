import csv
from decimal import Decimal

from django.conf import settings
from django.contrib import admin
from django.db.models import DecimalField, Sum
from django.db.models.functions import Coalesce
from django.db.models.functions import TruncMonth
from django.forms import TextInput
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.http import HttpResponse
from .models import (
    AIBudgetCredit,
    AIBudgetMonthlyTarget,
    AILog,
    Conversation,
    ConversationTemplate,
    DailyReport,
    EmotionalAnalysis,
    MonthlyReport,
    Question,
    WeeklyReport,
    WellnessMetric,
)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "module", "plan_tier", "created_at")
    list_filter = ("module", "plan_tier", "created_at")
    search_fields = ("user__email", "user_message", "ai_response")
    readonly_fields = ("user", "module", "plan_tier", "user_message", "ai_response", "created_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AIBudgetCredit)
class AIBudgetCreditAdmin(admin.ModelAdmin):
    list_display = ("provider", "amount_usd", "credited_at", "source_reference", "created_by", "created_at")
    list_filter = ("provider", "credited_at", "created_at")
    search_fields = ("source_reference", "notes", "created_by__email")
    date_hierarchy = "credited_at"
    ordering = ("-credited_at", "-created_at")
    readonly_fields = ("created_by", "created_at")

    fieldsets = (
        (
            "Budget Credit",
            {
                "fields": (
                    "provider",
                    "amount_usd",
                    "credited_at",
                    "source_reference",
                    "notes",
                    "created_by",
                    "created_at",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        obj.provider = (obj.provider or "").strip().lower()
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "provider":
            kwargs["widget"] = TextInput(attrs={"placeholder": "openai / anthropic / grok / gemini"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "dashboard/",
                self.admin_site.admin_view(self.cost_dashboard_view),
                name="ai_cost_dashboard",
            ),
            path(
                "dashboard/export-monthly-csv/",
                self.admin_site.admin_view(self.cost_dashboard_export_monthly_csv),
                name="ai_cost_dashboard_export_monthly_csv",
            ),
        ]
        return custom_urls + urls

    def cost_dashboard_view(self, request):
        low_budget_alert_threshold = Decimal(
            str(getattr(settings, "AI_BUDGET_ALERT_THRESHOLD_USD", "20.00"))
        )

        total_credit_rows = AIBudgetCredit.objects.values("provider").annotate(
            credits=Coalesce(
                Sum("amount_usd"),
                0,
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        total_spent_rows = AILog.objects.values("provider").annotate(
            spent=Coalesce(
                Sum("estimated_cost_usd"),
                0,
                output_field=DecimalField(max_digits=12, decimal_places=6),
            )
        )

        provider_totals_map = {}
        for row in total_credit_rows:
            provider = (row.get("provider") or "unknown").strip().lower()
            provider_totals_map[provider] = {
                "provider": provider,
                "credits": row["credits"],
                "spent": Decimal("0"),
            }
        for row in total_spent_rows:
            provider = (row.get("provider") or "unknown").strip().lower()
            if provider not in provider_totals_map:
                provider_totals_map[provider] = {
                    "provider": provider,
                    "credits": Decimal("0"),
                    "spent": row["spent"],
                }
            else:
                provider_totals_map[provider]["spent"] = row["spent"]

        monthly_spend_rows = (
            AILog.objects.exclude(estimated_cost_usd__isnull=True)
            .annotate(month=TruncMonth("created_at"))
            .values("provider", "month")
            .annotate(
                spent=Coalesce(
                    Sum("estimated_cost_usd"),
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=6),
                )
            )
            .order_by("-month", "provider")
        )

        monthly_credit_rows = (
            AIBudgetCredit.objects.annotate(month=TruncMonth("credited_at"))
            .values("provider", "month")
            .annotate(
                credits=Coalesce(
                    Sum("amount_usd"),
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .order_by("-month", "provider")
        )

        monthly_summary_map = {}
        for row in monthly_credit_rows:
            provider = (row.get("provider") or "unknown").strip().lower()
            key = (provider, row["month"])
            monthly_summary_map[key] = {
                "provider": provider,
                "month": row["month"],
                "credits": row["credits"],
                "spent": Decimal("0"),
            }
        for row in monthly_spend_rows:
            provider = (row.get("provider") or "unknown").strip().lower()
            key = (provider, row["month"])
            if key not in monthly_summary_map:
                monthly_summary_map[key] = {
                    "provider": provider,
                    "month": row["month"],
                    "credits": Decimal("0"),
                    "spent": row["spent"],
                }
            else:
                monthly_summary_map[key]["spent"] = row["spent"]

        monthly_summary = []
        for row in monthly_summary_map.values():
            row["remaining"] = row["credits"] - row["spent"]
            monthly_summary.append(row)
        monthly_summary.sort(
            key=lambda r: (r["month"] is None, r["month"]),
            reverse=True,
        )

        now = getattr(request, "timestamp", None)
        if now is None:
            from django.utils import timezone

            now = timezone.now()

        current_year = now.year
        current_month = now.month

        monthly_targets = {
            (target.provider or "unknown").strip().lower(): target
            for target in AIBudgetMonthlyTarget.objects.filter(year=current_year, month=current_month)
        }

        current_month_spent_rows = (
            AILog.objects.filter(created_at__year=current_year, created_at__month=current_month)
            .values("provider")
            .annotate(
                total=Coalesce(
                    Sum("estimated_cost_usd"),
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=6),
                )
            )
        )
        current_month_spent = {
            (row.get("provider") or "unknown").strip().lower(): row["total"]
            for row in current_month_spent_rows
        }

        provider_set = set(provider_totals_map.keys())
        provider_set.update(monthly_targets.keys())
        provider_set.update(current_month_spent.keys())

        monthly_progress = {}
        for provider in sorted(provider_set):
            target = monthly_targets.get(provider)
            spent = current_month_spent.get(provider, Decimal("0"))
            if target:
                target_value = target.target_usd
                progress_pct = min(Decimal("100.00"), (spent / target_value) * Decimal("100")) if target_value > 0 else Decimal("0")
                monthly_progress[provider] = {
                    "target": target_value,
                    "spent": spent,
                    "remaining": target_value - spent,
                    "progress_pct": progress_pct,
                    "is_over_target": spent > target_value,
                }
            else:
                monthly_progress[provider] = {
                    "target": None,
                    "spent": spent,
                    "remaining": None,
                    "progress_pct": None,
                    "is_over_target": False,
                }

        provider_cards = []
        total_credits_all = Decimal("0")
        total_spent_all = Decimal("0")
        for provider in sorted(provider_set):
            totals = provider_totals_map.get(
                provider,
                {"provider": provider, "credits": Decimal("0"), "spent": Decimal("0")},
            )
            remaining = totals["credits"] - totals["spent"]
            total_credits_all += totals["credits"]
            total_spent_all += totals["spent"]
            provider_cards.append(
                {
                    "provider": provider,
                    "display_name": provider.replace("_", " ").title(),
                    "credits": totals["credits"],
                    "spent": totals["spent"],
                    "remaining": remaining,
                    "monthly_progress": monthly_progress.get(provider),
                }
            )

        total_remaining_all = total_credits_all - total_spent_all

        low_remaining_alerts = []
        for item in provider_cards:
            if item["remaining"] < low_budget_alert_threshold:
                low_remaining_alerts.append(
                    {
                        "provider": item["display_name"],
                        "remaining": item["remaining"],
                        "threshold": low_budget_alert_threshold,
                    }
                )

        recent_cost_events = AILog.objects.exclude(estimated_cost_usd__isnull=True).order_by("-created_at")[:25]
        recent_credits = AIBudgetCredit.objects.order_by("-credited_at", "-created_at")[:25]

        context = {
            **self.admin_site.each_context(request),
            "title": "AI Cost Dashboard",
            "provider_cards": provider_cards,
            "totals": {
                "credits": total_credits_all,
                "spent": total_spent_all,
                "remaining": total_remaining_all,
            },
            "recent_cost_events": recent_cost_events,
            "recent_credits": recent_credits,
            "monthly_summary": monthly_summary[:24],
            "current_month": now,
            "monthly_progress": monthly_progress,
            "low_remaining_alerts": low_remaining_alerts,
            "low_budget_alert_threshold": low_budget_alert_threshold,
            "credits_admin_changelist_url": reverse('admin:ai_aibudgetcredit_changelist'),
            "credits_admin_add_url": reverse("admin:ai_aibudgetcredit_add"),
            "monthly_targets_changelist_url": reverse("admin:ai_aibudgetmonthlytarget_changelist"),
            "monthly_targets_add_url": reverse("admin:ai_aibudgetmonthlytarget_add"),
            "monthly_csv_export_url": reverse("admin:ai_cost_dashboard_export_monthly_csv"),
        }
        return TemplateResponse(request, "admin/ai/cost_dashboard.html", context)

    def cost_dashboard_export_monthly_csv(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="ai_budget_monthly_summary.csv"'
        writer = csv.writer(response)
        writer.writerow(["month", "provider", "credits_usd", "spent_usd", "remaining_usd"])

        monthly_spend_rows = (
            AILog.objects.exclude(estimated_cost_usd__isnull=True)
            .annotate(month=TruncMonth("created_at"))
            .values("provider", "month")
            .annotate(
                spent=Coalesce(
                    Sum("estimated_cost_usd"),
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=6),
                )
            )
            .order_by("-month", "provider")
        )

        monthly_credit_rows = (
            AIBudgetCredit.objects.annotate(month=TruncMonth("credited_at"))
            .values("provider", "month")
            .annotate(
                credits=Coalesce(
                    Sum("amount_usd"),
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .order_by("-month", "provider")
        )

        summary_map = {}
        for row in monthly_credit_rows:
            provider = (row.get("provider") or "unknown").strip().lower()
            key = (provider, row["month"])
            summary_map[key] = {
                "provider": provider,
                "month": row["month"],
                "credits": row["credits"],
                "spent": Decimal("0"),
            }
        for row in monthly_spend_rows:
            provider = (row.get("provider") or "unknown").strip().lower()
            key = (provider, row["month"])
            if key not in summary_map:
                summary_map[key] = {
                    "provider": provider,
                    "month": row["month"],
                    "credits": Decimal("0"),
                    "spent": row["spent"],
                }
            else:
                summary_map[key]["spent"] = row["spent"]

        rows = list(summary_map.values())
        rows.sort(key=lambda r: (r["month"] is None, r["month"]), reverse=True)
        for row in rows:
            remaining = row["credits"] - row["spent"]
            month_value = row["month"].strftime("%Y-%m") if row["month"] else "unknown"
            writer.writerow([month_value, row["provider"], row["credits"], row["spent"], remaining])

        return response


@admin.register(AIBudgetMonthlyTarget)
class AIBudgetMonthlyTargetAdmin(admin.ModelAdmin):
    list_display = ("provider", "year", "month", "target_usd", "updated_at")
    list_filter = ("provider", "year", "month")
    search_fields = ("notes",)
    ordering = ("-year", "-month", "provider")
    def save_model(self, request, obj, form, change):
        obj.provider = (obj.provider or "").strip().lower()
        super().save_model(request, obj, form, change)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "provider":
            kwargs["widget"] = TextInput(attrs={"placeholder": "openai / anthropic / grok / gemini"})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(ConversationTemplate)
class ConversationTemplateAdmin(admin.ModelAdmin):
    change_form_template = "admin/two_column_change_form.html"
    list_display = ("name", "language")
    fieldsets = (
        (
            "Identificare",
            {
                "fields": (
                    "name",
                    "language",
                )
            },
        ),
        (
            "Prompt",
            {
                "fields": ("prompt",)
            },
        ),
    )


@admin.register(AILog)
class AILogAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "provider", "model", "user", "input_tokens", "output_tokens", "estimated_cost_usd")
    list_filter = ("provider", "model", "created_at")
    search_fields = ("user__email", "model", "provider", "prompt_hash")
    readonly_fields = (
        "user",
        "provider",
        "model",
        "prompt_hash",
        "input_tokens",
        "output_tokens",
        "estimated_cost_usd",
        "created_at",
    )
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "updated_at")
    list_filter = ("date",)
    search_fields = ("user__email", "summary")
    readonly_fields = ("user", "date", "summary", "highlights", "challenges", "recommendations", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(WeeklyReport)
class WeeklyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "week_start", "updated_at")
    list_filter = ("week_start",)
    search_fields = ("user__email", "summary")
    readonly_fields = ("user", "week_start", "summary", "trends", "progress", "recommendations", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "year", "month", "updated_at")
    list_filter = ("year", "month")
    search_fields = ("user__email", "summary")
    readonly_fields = ("user", "year", "month", "summary", "trends", "insights", "recommendations", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EmotionalAnalysis)
class EmotionalAnalysisAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "dominant_emotion", "created_at")
    list_filter = ("dominant_emotion",)
    search_fields = ("user__email", "dominant_emotion", "observations")


@admin.register(WellnessMetric)
class WellnessMetricAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "stress_score", "energy_score", "motivation_score", "created_at")
    search_fields = ("user__email",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question_type", "priority", "created_at")
    list_filter = ("question_type", "priority")
    search_fields = ("user__email", "text", "reason")

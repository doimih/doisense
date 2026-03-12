from django.contrib import admin

from core.audit import extract_form_changes, log_admin_change

from .models import Payment, StripeWebhookEvent


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "status",
        "plan_tier",
        "cancel_at_period_end",
        "current_period_end",
        "stripe_subscription_id",
        "created_at",
    )
    list_filter = ("status", "plan_tier", "cancel_at_period_end")
    search_fields = ("user__email", "stripe_customer_id", "stripe_subscription_id")
    ordering = ("-created_at",)
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "Payment",
            {
                "fields": (
                    "user",
                    "status",
                    "plan_tier",
                    "cancel_at_period_end",
                    "current_period_end",
                ),
            },
        ),
        (
            "Stripe",
            {
                "fields": ("stripe_customer_id", "stripe_subscription_id"),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        before_data, after_data = extract_form_changes(form)
        super().save_model(request, obj, form, change)
        if change and form.changed_data:
            log_admin_change(
                actor=request.user,
                action="payment_updated",
                target_obj=obj,
                before_data=before_data,
                after_data=after_data,
                reason="Payment status/plan updated from admin",
            )


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = (
        "event_id",
        "event_type",
        "last_status",
        "delivery_attempts",
        "first_received_at",
        "last_received_at",
    )
    list_filter = ("event_type", "last_status")
    search_fields = ("event_id", "event_type")
    ordering = ("-first_received_at",)
    readonly_fields = (
        "event_id",
        "event_type",
        "last_status",
        "delivery_attempts",
        "payload_preview",
        "processing_error",
        "processed_at",
        "first_received_at",
        "last_received_at",
    )

    def payload_preview(self, obj):
        payload = obj.payload or {}
        return {
            "id": payload.get("id"),
            "type": payload.get("type"),
            "customer": payload.get("data", {}).get("object", {}).get("customer"),
            "subscription": payload.get("data", {}).get("object", {}).get("subscription"),
        }

    payload_preview.short_description = "Payload preview"

from django.contrib import admin

from .models import Payment, StripeWebhookEvent


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "stripe_subscription_id", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email", "stripe_customer_id", "stripe_subscription_id")
    ordering = ("-created_at",)
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (
            "Payment",
            {
                "fields": ("user", "status"),
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
        "payload",
        "processing_error",
        "processed_at",
        "first_received_at",
        "last_received_at",
    )

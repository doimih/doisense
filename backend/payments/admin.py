from django.contrib import admin

from .models import Payment


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

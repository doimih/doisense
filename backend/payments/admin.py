from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "stripe_subscription_id", "created_at")
    list_filter = ("status",)

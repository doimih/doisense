from django.conf import settings
from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("past_due", "Past due"),
        ("trialing", "Trialing"),
    ]
    PLAN_CHOICES = [
        ("basic", "Basic"),
        ("premium", "Premium"),
        ("premium_discounted", "Premium Discounted"),
        ("vip", "VIP"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    plan_tier = models.CharField(max_length=24, choices=PLAN_CHOICES, default="premium")
    # Billing cycle tracking (populated by Stripe webhooks)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments_payment"

    def __str__(self):
        return f"Payment for {self.user.email} - {self.status}"


class StripeWebhookEvent(models.Model):
    STATUS_RECEIVED = "received"
    STATUS_PROCESSED = "processed"
    STATUS_IGNORED = "ignored"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_RECEIVED, "Received"),
        (STATUS_PROCESSED, "Processed"),
        (STATUS_IGNORED, "Ignored"),
        (STATUS_FAILED, "Failed"),
    ]

    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    delivery_attempts = models.PositiveIntegerField(default=1)
    last_status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_RECEIVED)
    payload = models.JSONField(default=dict, blank=True)
    processing_error = models.TextField(blank=True, default="")
    processed_at = models.DateTimeField(null=True, blank=True)
    first_received_at = models.DateTimeField(auto_now_add=True)
    last_received_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments_stripewebhookevent"
        ordering = ["-first_received_at"]
        indexes = [
            models.Index(fields=["event_type", "first_received_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} ({self.event_id})"

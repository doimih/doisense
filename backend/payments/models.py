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
        ("vip", "VIP"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    plan_tier = models.CharField(max_length=10, choices=PLAN_CHOICES, default="premium")
    # Billing cycle tracking (populated by Stripe webhooks)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments_payment"

    def __str__(self):
        return f"Payment for {self.user.email} - {self.status}"

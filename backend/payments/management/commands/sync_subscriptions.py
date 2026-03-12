from django.core.management.base import BaseCommand

import stripe

from core.system_config import (
    get_stripe_price_id_basic,
    get_stripe_price_id_premium,
    get_stripe_price_id_vip,
    get_stripe_secret_key,
)
from payments.models import Payment
from users.models import User


def _price_id_to_tier(price_id: str) -> str:
    if price_id and price_id == get_stripe_price_id_basic():
        return "basic"
    if price_id and price_id == get_stripe_price_id_vip():
        return "vip"
    if price_id and price_id == get_stripe_price_id_premium():
        return "premium"
    return "premium"


class Command(BaseCommand):
    help = "Sync local payment statuses with Stripe subscriptions."

    def handle(self, *args, **options):
        stripe_key = get_stripe_secret_key()
        if not stripe_key:
            self.stdout.write(self.style.WARNING("Stripe is not configured. Skipping sync."))
            return

        stripe.api_key = stripe_key
        qs = (
            Payment.objects.exclude(stripe_subscription_id="")
            .exclude(stripe_subscription_id__isnull=True)
            .select_related("user")
        )

        checked = 0
        updated = 0
        failed = 0

        status_map = {
            "active": "active",
            "past_due": "past_due",
            "canceled": "cancelled",
            "trialing": "trialing",
        }

        for payment in qs.iterator():
            checked += 1
            try:
                sub = stripe.Subscription.retrieve(payment.stripe_subscription_id)
            except stripe.StripeError as exc:
                failed += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Failed subscription fetch for payment={payment.id}: {exc}"
                    )
                )
                continue

            stripe_status = sub.get("status", "active")
            new_status = status_map.get(stripe_status, payment.status)

            items = sub.get("items", {}).get("data", [])
            new_tier = payment.plan_tier
            if items:
                price_id = items[0].get("price", {}).get("id", "")
                new_tier = _price_id_to_tier(price_id)

            changed_fields = []
            if payment.status != new_status:
                payment.status = new_status
                changed_fields.append("status")

            if payment.plan_tier != new_tier:
                payment.plan_tier = new_tier
                changed_fields.append("plan_tier")

            period_end_ts = sub.get("current_period_end")
            if period_end_ts:
                from datetime import datetime, timezone as dt_timezone

                new_period_end = datetime.fromtimestamp(period_end_ts, tz=dt_timezone.utc)
                if payment.current_period_end != new_period_end:
                    payment.current_period_end = new_period_end
                    changed_fields.append("current_period_end")

            cancel_at_period_end = bool(sub.get("cancel_at_period_end", False))
            if payment.cancel_at_period_end != cancel_at_period_end:
                payment.cancel_at_period_end = cancel_at_period_end
                changed_fields.append("cancel_at_period_end")

            new_is_premium = new_status in ("active", "trialing")
            new_user_tier = new_tier if new_is_premium else User.PLAN_FREE
            user_changed = False
            if payment.user.is_premium != new_is_premium:
                payment.user.is_premium = new_is_premium
                user_changed = True
            if payment.user.plan_tier != new_user_tier:
                payment.user.plan_tier = new_user_tier
                user_changed = True

            if changed_fields:
                changed_fields.append("updated_at")
                payment.save(update_fields=changed_fields)
            if user_changed:
                payment.user.save(update_fields=["is_premium", "plan_tier"])

            if changed_fields or user_changed:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Subscription sync completed. checked={checked}, updated={updated}, failed={failed}"
            )
        )

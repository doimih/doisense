from django.core.management.base import BaseCommand

import stripe

from core.system_config import (
    get_stripe_secret_key,
    plan_tier_from_stripe_price_id,
)
from payments.models import Payment, StripeWebhookEvent
from users.models import User


class Command(BaseCommand):
    help = "Sync local payment statuses with Stripe subscriptions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--payment-id",
            dest="payment_ids",
            action="append",
            type=int,
            help="Restrict sync to one or multiple payment IDs.",
        )
        parser.add_argument(
            "--subscription-id",
            dest="subscription_ids",
            action="append",
            help="Restrict sync to one or multiple Stripe subscription IDs.",
        )
        parser.add_argument(
            "--failed-webhooks-only",
            action="store_true",
            help="Reconcile only subscriptions referenced by failed webhook events.",
        )
        parser.add_argument(
            "--failed-webhooks-limit",
            type=int,
            default=200,
            help="How many recent failed webhook events to inspect when --failed-webhooks-only is used.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of payments processed (0 means no limit).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Compute reconciliation changes without persisting updates.",
        )

    def _extract_subscription_id(self, payload: dict) -> str:
        if not isinstance(payload, dict):
            return ""
        sub_id = str(payload.get("subscription") or "").strip()
        if sub_id.startswith("sub_"):
            return sub_id

        payload_id = str(payload.get("id") or "").strip()
        if payload_id.startswith("sub_"):
            return payload_id
        return ""

    def handle(self, *args, **options):
        stripe_key = get_stripe_secret_key()
        if not stripe_key:
            self.stdout.write(self.style.WARNING("Stripe is not configured. Skipping sync."))
            return

        stripe.api_key = stripe_key
        dry_run = bool(options.get("dry_run", False))
        qs = (
            Payment.objects.exclude(stripe_subscription_id="")
            .exclude(stripe_subscription_id__isnull=True)
            .select_related("user")
        )

        payment_ids = options.get("payment_ids") or []
        if payment_ids:
            qs = qs.filter(id__in=payment_ids)

        subscription_ids = [str(item).strip() for item in (options.get("subscription_ids") or []) if str(item).strip()]
        if subscription_ids:
            qs = qs.filter(stripe_subscription_id__in=subscription_ids)

        if options.get("failed_webhooks_only"):
            failed_limit = max(int(options.get("failed_webhooks_limit", 200) or 200), 1)
            failed_events = StripeWebhookEvent.objects.filter(
                last_status=StripeWebhookEvent.STATUS_FAILED
            ).order_by("-last_received_at")[:failed_limit]

            failed_subscription_ids = {
                subscription_id
                for subscription_id in (
                    self._extract_subscription_id((event.payload or {})) for event in failed_events
                )
                if subscription_id
            }
            if not failed_subscription_ids:
                self.stdout.write(
                    self.style.WARNING(
                        "No failed webhook subscriptions found in the selected window. Nothing to reconcile."
                    )
                )
                return
            qs = qs.filter(stripe_subscription_id__in=failed_subscription_ids)

        record_limit = int(options.get("limit", 0) or 0)
        if record_limit > 0:
            qs = qs.order_by("-updated_at")[:record_limit]

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
                new_tier = plan_tier_from_stripe_price_id(price_id)

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
            if not payment.user.vip_manual_override:
                if payment.user.is_premium != new_is_premium:
                    payment.user.is_premium = new_is_premium
                    user_changed = True
                if payment.user.plan_tier != new_user_tier:
                    payment.user.plan_tier = new_user_tier
                    user_changed = True

            if changed_fields:
                if not dry_run:
                    changed_fields.append("updated_at")
                    payment.save(update_fields=changed_fields)
            if user_changed and not dry_run:
                payment.user.save(update_fields=["is_premium", "plan_tier"])

            if changed_fields or user_changed:
                updated += 1

        mode = "dry-run" if dry_run else "apply"
        self.stdout.write(
            self.style.SUCCESS(
                f"Subscription sync completed ({mode}). checked={checked}, updated={updated}, failed={failed}"
            )
        )

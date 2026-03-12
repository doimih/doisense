import datetime
import stripe
from django.conf import settings
from django.db.models import F
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from core.notifications import (
    create_in_app_notification,
    record_notification_delivery,
    send_payment_expiring_notification,
    send_payment_failed_notification,
    send_payment_invalid_method_notification,
    was_notification_sent,
)
from core.analytics import track_event
from core.feature_access import require_feature
from core.models import SystemErrorEvent
from core.system_config import (
    get_stripe_price_id_for_tier,
    get_stripe_secret_key,
    get_stripe_webhook_secret,
)
from users.models import User

from .models import Payment, StripeWebhookEvent


VALID_PLAN_TIERS = {"basic", "premium", "vip"}
EARLY_DISCOUNT_PERCENT = 10


class CheckoutSessionRateThrottle(UserRateThrottle):
    rate = "6/hour"


class UpgradeSessionRateThrottle(UserRateThrottle):
    rate = "12/hour"


def _is_manual_vip(user: User) -> bool:
    return bool(getattr(user, "manual_vip", False) or getattr(user, "vip_manual_override", False))


def _register_webhook_event(event: dict):
    event_id = str(event.get("id") or "").strip()
    if not event_id:
        return None, True

    event_type = str(event.get("type") or "unknown")[:100]
    payload = event.get("data", {}).get("object", {}) if isinstance(event, dict) else {}
    obj, created = StripeWebhookEvent.objects.get_or_create(
        event_id=event_id,
        defaults={"event_type": event_type, "payload": payload},
    )
    if created:
        return obj, True

    StripeWebhookEvent.objects.filter(pk=obj.pk).update(
        delivery_attempts=F("delivery_attempts") + 1,
        last_status=StripeWebhookEvent.STATUS_IGNORED,
    )
    return obj, False


def _mark_webhook_processed(webhook_event: StripeWebhookEvent | None):
    if not webhook_event:
        return
    webhook_event.last_status = StripeWebhookEvent.STATUS_PROCESSED
    webhook_event.processing_error = ""
    webhook_event.processed_at = timezone.now()
    webhook_event.save(update_fields=["last_status", "processing_error", "processed_at", "last_received_at"])


def _mark_webhook_failed(webhook_event: StripeWebhookEvent | None, error: str):
    if not webhook_event:
        return
    webhook_event.last_status = StripeWebhookEvent.STATUS_FAILED
    webhook_event.processing_error = (error or "")[:5000]
    webhook_event.save(update_fields=["last_status", "processing_error", "last_received_at"])
    try:
        SystemErrorEvent.objects.create(
            severity=SystemErrorEvent.SEVERITY_HIGH,
            component="stripe_webhook",
            endpoint=webhook_event.event_type,
            http_method="POST",
            status_code=500,
            error_type="WebhookProcessingError",
            message=(error or "")[:2000],
            context={"event_id": webhook_event.event_id, "delivery_attempts": webhook_event.delivery_attempts},
        )
    except Exception:
        return


def _send_payment_notification_once(user: User, notification_type: str, context_key: str, sender) -> None:
    if was_notification_sent(user, notification_type, context_key=context_key):
        return

    sender()
    record_notification_delivery(user, notification_type, context_key=context_key)
    title_map = {
        "payment_failed": "Payment failed",
        "payment_expiring": "Subscription expiring soon",
        "payment_invalid_method": "Update your payment method",
    }
    body_map = {
        "payment_failed": "We could not process your latest payment. Please check billing settings.",
        "payment_expiring": "Your subscription is approaching period end. Review your plan status.",
        "payment_invalid_method": "Your payment method appears invalid or near expiry.",
    }
    create_in_app_notification(
        user,
        notification_type,
        title_map.get(notification_type, "Billing update"),
        body_map.get(notification_type, "There is an update related to your subscription."),
        context_key=context_key,
    )


def _price_id_to_tier(price_id: str) -> str:
    """Reverse-map a Stripe price ID to an internal plan tier."""
    from core.system_config import (
        get_stripe_price_id_basic,
        get_stripe_price_id_premium,
        get_stripe_price_id_vip,
    )

    if price_id and price_id == get_stripe_price_id_basic():
        return "basic"
    if price_id and price_id == get_stripe_price_id_vip():
        return "vip"
    if price_id and price_id == get_stripe_price_id_premium():
        return "premium"
    return "premium"


def _is_early_discount_applicable(user: User, requested_plan_tier: str) -> bool:
    return (
        requested_plan_tier == "premium"
        and bool(getattr(user, "early_discount_eligible", False))
        and not bool(getattr(user, "vip_manual_override", False))
    )


def _resolve_internal_payment_plan_tier(user: User, requested_plan_tier: str) -> str:
    if _is_early_discount_applicable(user, requested_plan_tier):
        return "premium_discounted"
    return requested_plan_tier


def _activate_plan(
    user: User,
    plan_tier: str,
    *,
    source: str,
    customer_id: str | None = None,
    subscription_id: str | None = None,
    payment_plan_tier: str | None = None,
) -> None:
    user.is_premium = True
    user.plan_tier = plan_tier
    user.save(update_fields=["is_premium", "plan_tier"])

    Payment.objects.update_or_create(
        user=user,
        defaults={
            "stripe_customer_id": customer_id or ("" if source == "internal" else None),
            "stripe_subscription_id": subscription_id or ("" if source == "internal" else None),
            "status": "active",
            "plan_tier": payment_plan_tier or plan_tier,
        },
    )


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CheckoutSessionRateThrottle]

    @require_feature("payment_checkout")
    def post(self, request):
        plan_tier = (request.data.get("plan_tier") or "premium").lower()
        if plan_tier not in VALID_PLAN_TIERS:
            plan_tier = "premium"

        user = request.user
        if _is_manual_vip(user):
            return Response(
                {
                    "url": None,
                    "internal_activation": False,
                    "manual_vip": True,
                    "effective_tier": User.PLAN_VIP,
                    "detail": "Manual VIP users bypass checkout and subscription logic.",
                },
                status=status.HTTP_200_OK,
            )

        stripe_secret_key = get_stripe_secret_key()
        stripe_price_id = get_stripe_price_id_for_tier(plan_tier)

        base_url = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
        language = user.language or "en"
        success_url = f"{base_url}/{language}/payment-success?plan={plan_tier}"
        cancel_url = f"{base_url}/{language}/pricing"

        if not stripe_secret_key or not stripe_price_id:
            payment_plan_tier = _resolve_internal_payment_plan_tier(user, plan_tier)
            _activate_plan(
                user,
                plan_tier,
                source="internal",
                payment_plan_tier=payment_plan_tier,
            )
            track_event(
                "checkout_initiated",
                source="backend",
                user=user,
                properties={"plan_tier": plan_tier},
            )
            return Response(
                {
                    "url": success_url,
                    "internal_activation": True,
                    "plan_tier": plan_tier,
                    "applied_plan_tier": payment_plan_tier,
                    "early_discount_applied": payment_plan_tier == "premium_discounted",
                    "early_discount_percent": EARLY_DISCOUNT_PERCENT if payment_plan_tier == "premium_discounted" else 0,
                },
                status=status.HTTP_200_OK,
            )

        stripe.api_key = stripe_secret_key
        payment = Payment.objects.filter(user=user).first()
        customer_id = payment.stripe_customer_id if payment else None

        try:
            session_params = {
                "mode": "subscription",
                "line_items": [{"price": stripe_price_id, "quantity": 1}],
                "success_url": success_url,
                "cancel_url": cancel_url,
                "metadata": {"user_id": user.id, "plan_tier": plan_tier},
            }
            if customer_id:
                session_params["customer"] = customer_id
            else:
                session_params["customer_email"] = user.email

            session = stripe.checkout.Session.create(**session_params)
            track_event(
                "checkout_initiated",
                source="backend",
                user=user,
                properties={"plan_tier": plan_tier},
            )
            return Response({"url": session.url}, status=status.HTTP_200_OK)
        except stripe.StripeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class SavedCardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stripe_secret_key = get_stripe_secret_key()
        if not stripe_secret_key:
            return Response(
                {"detail": "Stripe is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        stripe.api_key = stripe_secret_key
        payment = (
            Payment.objects.filter(user=request.user)
            .exclude(stripe_customer_id="")
            .exclude(stripe_customer_id__isnull=True)
            .order_by("-updated_at")
            .first()
        )

        if not payment:
            return Response({"has_saved_card": False, "card": None}, status=status.HTTP_200_OK)

        try:
            methods = stripe.PaymentMethod.list(
                customer=payment.stripe_customer_id,
                type="card",
                limit=1,
            )
            first_method = methods.data[0] if methods and methods.data else None
            if not first_method or not getattr(first_method, "card", None):
                return Response({"has_saved_card": False, "card": None}, status=status.HTTP_200_OK)

            card = first_method.card
            return Response(
                {
                    "has_saved_card": True,
                    "card": {
                        "brand": getattr(card, "brand", None),
                        "last4": getattr(card, "last4", None),
                        "exp_month": getattr(card, "exp_month", None),
                        "exp_year": getattr(card, "exp_year", None),
                        "country": getattr(card, "country", None),
                    },
                },
                status=status.HTTP_200_OK,
            )
        except stripe.StripeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class CreateBillingPortalSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stripe_secret_key = get_stripe_secret_key()
        if not stripe_secret_key:
            return Response(
                {"detail": "Stripe is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        stripe.api_key = stripe_secret_key
        user = request.user
        payment = (
            Payment.objects.filter(user=user)
            .exclude(stripe_customer_id="")
            .exclude(stripe_customer_id__isnull=True)
            .order_by("-updated_at")
            .first()
        )

        if not payment:
            return Response(
                {"detail": "No Stripe customer found for this account yet."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        base_url = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
        language = user.language or "en"
        return_url = f"{base_url}/{language}/profile"

        try:
            session = stripe.billing_portal.Session.create(
                customer=payment.stripe_customer_id,
                return_url=return_url,
            )
            return Response({"url": session.url}, status=status.HTTP_200_OK)
        except stripe.StripeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionStatusView(APIView):
    """Return the current user's active subscription details."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if _is_manual_vip(user):
            return Response(
                {
                    "has_subscription": True,
                    "status": "manual_vip",
                    "plan_tier": User.PLAN_VIP,
                    "cancel_at_period_end": False,
                    "current_period_end": None,
                    "effective_tier": User.PLAN_VIP,
                    "manual_vip": True,
                }
            )

        payment = (
            Payment.objects.filter(user=user)
            .order_by("-updated_at")
            .first()
        )
        if not payment:
            return Response({"has_subscription": False})

        return Response({
            "has_subscription": True,
            "status": payment.status,
            "plan_tier": payment.plan_tier,
            "cancel_at_period_end": payment.cancel_at_period_end,
            "current_period_end": payment.current_period_end.isoformat() if payment.current_period_end else None,
            "effective_tier": user.effective_plan_tier(),
        })


class UpgradeSubscriptionView(APIView):
    """Upgrade or downgrade an existing Stripe subscription in-place."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [UpgradeSessionRateThrottle]

    @require_feature("payment_upgrade")
    def post(self, request):
        plan_tier = (request.data.get("plan_tier") or "premium").lower()
        if plan_tier not in VALID_PLAN_TIERS:
            return Response({"detail": "Invalid plan tier."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if _is_manual_vip(user):
            return Response(
                {
                    "upgraded": False,
                    "manual_vip": True,
                    "effective_tier": User.PLAN_VIP,
                    "detail": "Manual VIP users bypass subscription upgrade logic.",
                },
                status=status.HTTP_200_OK,
            )

        stripe_secret_key = get_stripe_secret_key()
        stripe_price_id = get_stripe_price_id_for_tier(plan_tier)

        if not stripe_secret_key or not stripe_price_id:
            # Fall back to internal activation when Stripe is not configured
            payment_plan_tier = _resolve_internal_payment_plan_tier(user, plan_tier)
            _activate_plan(
                user,
                plan_tier,
                source="internal",
                payment_plan_tier=payment_plan_tier,
            )
            track_event(
                "subscription_change_requested",
                source="backend",
                user=user,
                properties={"plan_tier": plan_tier},
            )
            return Response(
                {
                    "upgraded": True,
                    "plan_tier": plan_tier,
                    "applied_plan_tier": payment_plan_tier,
                    "early_discount_applied": payment_plan_tier == "premium_discounted",
                    "early_discount_percent": EARLY_DISCOUNT_PERCENT if payment_plan_tier == "premium_discounted" else 0,
                }
            )

        payment = (
            Payment.objects.filter(user=user, status__in=["active", "trialing", "past_due"])
            .exclude(stripe_subscription_id="")
            .exclude(stripe_subscription_id__isnull=True)
            .order_by("-updated_at")
            .first()
        )

        if not payment:
            return Response(
                {"detail": "No active subscription found. Use the checkout flow to subscribe."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stripe.api_key = stripe_secret_key
        try:
            subscription = stripe.Subscription.retrieve(payment.stripe_subscription_id)
            stripe.Subscription.modify(
                payment.stripe_subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0]["id"],
                    "price": stripe_price_id,
                }],
                proration_behavior="always_invoice",
            )
            # Optimistically update locally; webhook will reconcile if needed
            _activate_plan(
                user, plan_tier,
                source="stripe",
                customer_id=payment.stripe_customer_id,
                subscription_id=payment.stripe_subscription_id,
            )
            track_event(
                "subscription_change_requested",
                source="backend",
                user=user,
                properties={"plan_tier": plan_tier},
            )
            return Response({"upgraded": True, "plan_tier": plan_tier})
        except stripe.StripeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class CancelSubscriptionView(APIView):
    """Cancel current subscription at period end (downgrade path)."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if _is_manual_vip(user):
            return Response(
                {
                    "cancel_at_period_end": False,
                    "manual_vip": True,
                    "effective_tier": User.PLAN_VIP,
                    "detail": "Manual VIP users bypass cancellation and subscription lifecycle logic.",
                },
                status=status.HTTP_200_OK,
            )

        stripe_secret_key = get_stripe_secret_key()
        payment = (
            Payment.objects.filter(user=user, status__in=["active", "trialing", "past_due"])
            .exclude(stripe_subscription_id="")
            .exclude(stripe_subscription_id__isnull=True)
            .order_by("-updated_at")
            .first()
        )

        if not payment:
            return Response(
                {"detail": "No active subscription found to cancel."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not stripe_secret_key:
            if not payment.current_period_end:
                payment.current_period_end = timezone.now() + datetime.timedelta(days=30)
            payment.cancel_at_period_end = True
            payment.save(update_fields=["cancel_at_period_end", "current_period_end", "updated_at"])
            track_event(
                "subscription_cancel_requested",
                source="backend",
                user=user,
                properties={"plan_tier": payment.plan_tier},
            )
            return Response({"cancel_at_period_end": True, "current_period_end": payment.current_period_end})

        stripe.api_key = stripe_secret_key
        try:
            subscription = stripe.Subscription.modify(
                payment.stripe_subscription_id,
                cancel_at_period_end=True,
            )
            period_end_ts = subscription.get("current_period_end")
            if period_end_ts:
                payment.current_period_end = datetime.datetime.fromtimestamp(
                    period_end_ts, tz=datetime.timezone.utc
                )
            payment.cancel_at_period_end = True
            payment.save(update_fields=["cancel_at_period_end", "current_period_end", "updated_at"])
            track_event(
                "subscription_cancel_requested",
                source="backend",
                user=user,
                properties={"plan_tier": payment.plan_tier},
            )
            return Response({"cancel_at_period_end": True, "current_period_end": payment.current_period_end})
        except stripe.StripeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    stripe_secret_key = get_stripe_secret_key()
    stripe_webhook_secret = get_stripe_webhook_secret() or settings.STRIPE_WEBHOOK_SECRET
    if not stripe_secret_key or not stripe_webhook_secret:
        return HttpResponse(status=503)

    stripe.api_key = stripe_secret_key
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, stripe_webhook_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.SignatureVerificationError:
        return HttpResponse(status=400)

    webhook_event, should_process = _register_webhook_event(event)
    if not should_process:
        return HttpResponse(status=200)

    event_type = event["type"]

    try:
        if event_type == "checkout.session.completed":
            session = event["data"]["object"]
            user_id = session.get("metadata", {}).get("user_id")
            plan_tier = (session.get("metadata", {}).get("plan_tier") or "premium").lower()
            if plan_tier not in VALID_PLAN_TIERS:
                plan_tier = "premium"

            if user_id:
                user = User.objects.filter(id=user_id).first()
                if user:
                    customer_id = session.get("customer")
                    subscription_id = session.get("subscription")
                    _activate_plan(
                        user,
                        plan_tier,
                        source="stripe",
                        customer_id=customer_id,
                        subscription_id=subscription_id,
                    )
                    # Fetch and store billing cycle end date
                    if subscription_id and stripe_secret_key:
                        try:
                            sub = stripe.Subscription.retrieve(subscription_id)
                            period_end_ts = sub.get("current_period_end")
                            if period_end_ts:
                                Payment.objects.filter(
                                    stripe_subscription_id=subscription_id
                                ).update(
                                    current_period_end=datetime.datetime.fromtimestamp(
                                        period_end_ts, tz=datetime.timezone.utc
                                    )
                                )
                        except stripe.StripeError:
                            pass

        elif event_type == "customer.subscription.updated":
            subscription = event["data"]["object"]
            sub_id = subscription.get("id")
            stripe_status = subscription.get("status", "active")
            payment = Payment.objects.filter(stripe_subscription_id=sub_id).first()
            if payment:
                status_map = {
                    "active": "active",
                    "past_due": "past_due",
                    "canceled": "cancelled",
                    "trialing": "trialing",
                }
                payment.status = status_map.get(stripe_status, "active")
                items = subscription.get("items", {}).get("data", [])
                if items:
                    price_id = items[0].get("price", {}).get("id", "")
                    new_tier = _price_id_to_tier(price_id)
                    payment.plan_tier = new_tier
                    if not _is_manual_vip(payment.user):
                        payment.user.plan_tier = new_tier
                        payment.user.save(update_fields=["plan_tier"])
                if stripe_status == "past_due" and not _is_manual_vip(payment.user):
                    payment.user.is_premium = False
                    payment.user.save(update_fields=["is_premium"])
                # Track billing cycle dates
                period_end_ts = subscription.get("current_period_end")
                if period_end_ts:
                    payment.current_period_end = datetime.datetime.fromtimestamp(
                        period_end_ts, tz=datetime.timezone.utc
                    )
                payment.cancel_at_period_end = bool(
                    subscription.get("cancel_at_period_end", False)
                )
                payment.save(
                    update_fields=[
                        "status",
                        "plan_tier",
                        "current_period_end",
                        "cancel_at_period_end",
                    ]
                )

                if payment.cancel_at_period_end and payment.current_period_end:
                    days_left = (payment.current_period_end.date() - timezone.now().date()).days
                    if 0 <= days_left <= 7:
                        context_key = (
                            f"{sub_id}:expiring:{payment.current_period_end.date().isoformat()}"
                        )
                        _send_payment_notification_once(
                            payment.user,
                            "payment_expiring",
                            context_key,
                            lambda: send_payment_expiring_notification(
                                payment.user, payment.current_period_end
                            ),
                        )

        elif event_type == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            sub_id = subscription.get("id")
            payment = Payment.objects.filter(stripe_subscription_id=sub_id).first()
            if payment:
                if not _is_manual_vip(payment.user):
                    payment.user.is_premium = False
                    payment.user.plan_tier = User.PLAN_FREE
                    payment.user.save(update_fields=["is_premium", "plan_tier"])
                payment.status = "cancelled"
                payment.save(update_fields=["status"])

        elif event_type == "invoice.payment_failed":
            invoice = event["data"]["object"]
            sub_id = invoice.get("subscription")
            payment = Payment.objects.filter(stripe_subscription_id=sub_id).first()
            if payment:
                payment.status = "past_due"
                payment.save(update_fields=["status"])
                if not _is_manual_vip(payment.user):
                    payment.user.is_premium = False
                    payment.user.save(update_fields=["is_premium"])

                _send_payment_notification_once(
                    payment.user,
                    "payment_failed",
                    f"{sub_id}:failed",
                    lambda: send_payment_failed_notification(payment.user),
                )

                # For failed invoices we also prompt payment method update once per day/context.
                _send_payment_notification_once(
                    payment.user,
                    "payment_invalid_method",
                    f"{sub_id}:invalid-method",
                    lambda: send_payment_invalid_method_notification(payment.user),
                )

        elif event_type == "customer.source.expiring":
            source = event["data"]["object"]
            customer_id = source.get("customer")
            payment = Payment.objects.filter(stripe_customer_id=customer_id).first()
            if payment:
                _send_payment_notification_once(
                    payment.user,
                    "payment_invalid_method",
                    f"{customer_id}:source-expiring",
                    lambda: send_payment_invalid_method_notification(payment.user),
                )

        elif event_type == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            sub_id = invoice.get("subscription")
            payment = Payment.objects.filter(stripe_subscription_id=sub_id).first()
            if payment and payment.status == "past_due":
                payment.status = "active"
                payment.save(update_fields=["status"])
                if not _is_manual_vip(payment.user):
                    payment.user.is_premium = True
                    payment.user.save(update_fields=["is_premium"])

        elif event_type == "charge.refunded":
            charge = event["data"]["object"]
            invoice_id = charge.get("invoice")
            amount = int(charge.get("amount") or 0)
            amount_refunded = int(charge.get("amount_refunded") or 0)
            refunded = bool(charge.get("refunded"))
            if invoice_id and refunded and amount > 0 and amount_refunded >= amount:
                try:
                    invoice = stripe.Invoice.retrieve(invoice_id)
                    sub_id = invoice.get("subscription")
                except stripe.StripeError:
                    sub_id = None

                payment = Payment.objects.filter(stripe_subscription_id=sub_id).first() if sub_id else None
                if payment:
                    payment.status = "cancelled"
                    payment.cancel_at_period_end = False
                    payment.save(update_fields=["status", "cancel_at_period_end", "updated_at"])
                    if not _is_manual_vip(payment.user):
                        payment.user.is_premium = False
                        payment.user.plan_tier = User.PLAN_FREE
                        payment.user.save(update_fields=["is_premium", "plan_tier"])
                    track_event(
                        "subscription_refunded",
                        source="backend",
                        user=payment.user,
                        properties={"plan_tier": payment.plan_tier},
                    )

        _mark_webhook_processed(webhook_event)
    except Exception as exc:
        _mark_webhook_failed(webhook_event, str(exc))
        return HttpResponse(status=500)

    return HttpResponse(status=200)

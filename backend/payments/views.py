import datetime
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.system_config import (
    get_stripe_price_id_for_tier,
    get_stripe_secret_key,
    get_stripe_webhook_secret,
)
from users.models import User

from .models import Payment


VALID_PLAN_TIERS = {"basic", "premium", "vip"}


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


def _activate_plan(user: User, plan_tier: str, *, source: str, customer_id: str | None = None, subscription_id: str | None = None) -> None:
    user.is_premium = True
    user.plan_tier = plan_tier
    user.save(update_fields=["is_premium", "plan_tier"])

    Payment.objects.update_or_create(
        user=user,
        defaults={
            "stripe_customer_id": customer_id or ("" if source == "internal" else None),
            "stripe_subscription_id": subscription_id or ("" if source == "internal" else None),
            "status": "active",
            "plan_tier": plan_tier,
        },
    )


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_tier = (request.data.get("plan_tier") or "premium").lower()
        if plan_tier not in VALID_PLAN_TIERS:
            plan_tier = "premium"

        user = request.user
        stripe_secret_key = get_stripe_secret_key()
        stripe_price_id = get_stripe_price_id_for_tier(plan_tier)

        base_url = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
        language = user.language or "en"
        success_url = f"{base_url}/{language}/payment-success?plan={plan_tier}"
        cancel_url = f"{base_url}/{language}/pricing"

        if not stripe_secret_key or not stripe_price_id:
            _activate_plan(user, plan_tier, source="internal")
            return Response(
                {"url": success_url, "internal_activation": True, "plan_tier": plan_tier},
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

    def post(self, request):
        plan_tier = (request.data.get("plan_tier") or "premium").lower()
        if plan_tier not in VALID_PLAN_TIERS:
            return Response({"detail": "Invalid plan tier."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        stripe_secret_key = get_stripe_secret_key()
        stripe_price_id = get_stripe_price_id_for_tier(plan_tier)

        if not stripe_secret_key or not stripe_price_id:
            # Fall back to internal activation when Stripe is not configured
            _activate_plan(user, plan_tier, source="internal")
            return Response({"upgraded": True, "plan_tier": plan_tier})

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
            return Response({"upgraded": True, "plan_tier": plan_tier})
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

    event_type = event["type"]

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
                payment.user.plan_tier = new_tier
                payment.user.save(update_fields=["plan_tier"])
            if stripe_status == "past_due":
                payment.user.is_premium = False
                payment.user.save(update_fields=["is_premium"])
            # Track billing cycle dates
            period_end_ts = subscription.get("current_period_end")
            if period_end_ts:
                payment.current_period_end = datetime.datetime.fromtimestamp(
                    period_end_ts, tz=datetime.timezone.utc
                )
            payment.cancel_at_period_end = bool(subscription.get("cancel_at_period_end", False))
            payment.save(update_fields=["status", "plan_tier", "current_period_end", "cancel_at_period_end"])

    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        sub_id = subscription.get("id")
        payment = Payment.objects.filter(stripe_subscription_id=sub_id).first()
        if payment:
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
            payment.user.is_premium = False
            payment.user.save(update_fields=["is_premium"])

    elif event_type == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        sub_id = invoice.get("subscription")
        payment = Payment.objects.filter(stripe_subscription_id=sub_id).first()
        if payment and payment.status == "past_due":
            payment.status = "active"
            payment.save(update_fields=["status"])
            payment.user.is_premium = True
            payment.user.save(update_fields=["is_premium"])

    return HttpResponse(status=200)

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from .models import Payment
from core.system_config import (
    get_stripe_price_id_premium,
    get_stripe_secret_key,
    get_stripe_webhook_secret,
)


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        stripe_secret_key = get_stripe_secret_key()
        stripe_price_id = get_stripe_price_id_premium()
        if not stripe_secret_key or not stripe_price_id:
            return Response(
                {"detail": "Stripe is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        stripe.api_key = stripe_secret_key
        user = request.user
        payment = Payment.objects.filter(user=user).first()
        customer_id = payment.stripe_customer_id if payment else None

        try:
            if customer_id:
                session = stripe.checkout.Session.create(
                    customer=customer_id,
                    mode="subscription",
                    line_items=[{"price": stripe_price_id, "quantity": 1}],
                    success_url=request.build_absolute_uri("/doisense/profile?success=1"),
                    cancel_url=request.build_absolute_uri("/doisense/profile?cancel=1"),
                    metadata={"user_id": user.id},
                )
            else:
                session = stripe.checkout.Session.create(
                    customer_email=user.email,
                    mode="subscription",
                    line_items=[{"price": stripe_price_id, "quantity": 1}],
                    success_url=request.build_absolute_uri("/doisense/profile?success=1"),
                    cancel_url=request.build_absolute_uri("/doisense/profile?cancel=1"),
                    metadata={"user_id": user.id},
                )
            return Response({"url": session.url})
        except stripe.StripeError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


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

        try:
            session = stripe.billing_portal.Session.create(
                customer=payment.stripe_customer_id,
                return_url=request.build_absolute_uri("/doisense/profile"),
            )
            return Response({"url": session.url}, status=status.HTTP_200_OK)
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
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_webhook_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("metadata", {}).get("user_id")
        if user_id:
            user = User.objects.filter(id=user_id).first()
            if user:
                user.is_premium = True
                user.save()
                Payment.objects.update_or_create(
                    user=user,
                    defaults={
                        "stripe_customer_id": session.get("customer"),
                        "stripe_subscription_id": session.get("subscription"),
                        "status": "active",
                    },
                )

    elif event["type"] in ("customer.subscription.deleted", "invoice.payment_failed"):
        subscription = event["data"].get("object", {})
        sub_id = subscription.get("id")
        payment = Payment.objects.filter(stripe_subscription_id=sub_id).first()
        if payment:
            payment.user.is_premium = False
            payment.user.save()
            payment.status = "cancelled" if "deleted" in event["type"] else "past_due"
            payment.save()

    return HttpResponse(status=200)

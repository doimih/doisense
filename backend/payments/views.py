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


stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PRICE_ID_PREMIUM:
            return Response(
                {"detail": "Stripe is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        user = request.user
        payment = Payment.objects.filter(user=user).first()
        customer_id = payment.stripe_customer_id if payment else None

        try:
            if customer_id:
                session = stripe.checkout.Session.create(
                    customer=customer_id,
                    mode="subscription",
                    line_items=[{"price": settings.STRIPE_PRICE_ID_PREMIUM, "quantity": 1}],
                    success_url=request.build_absolute_uri("/doisense/profile?success=1"),
                    cancel_url=request.build_absolute_uri("/doisense/profile?cancel=1"),
                    metadata={"user_id": user.id},
                )
            else:
                session = stripe.checkout.Session.create(
                    customer_email=user.email,
                    mode="subscription",
                    line_items=[{"price": settings.STRIPE_PRICE_ID_PREMIUM, "quantity": 1}],
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


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
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

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
from core.i18n import get_user_language, translate
from core.models import SystemErrorEvent
from core.system_config import (
    get_stripe_price_id_for_tier,
    get_stripe_product_id_for_tier,
    get_stripe_secret_key,
    get_stripe_webhook_secret,
    plan_tier_from_stripe_price_id,
    plan_tier_from_stripe_product_id,
)
from users.models import User

from .models import Payment, StripeWebhookEvent


VALID_PLAN_TIERS = {"basic", "premium", "vip"}
EARLY_DISCOUNT_PERCENT = 10

_PAYMENT_COPY = {
    "ro": {
        "payment_failed_title": "Plata a esuat",
        "payment_expiring_title": "Abonamentul expira curand",
        "payment_invalid_method_title": "Actualizeaza metoda de plata",
        "payment_failed_body": "Nu am putut procesa ultima ta plata. Verifica setarile de facturare.",
        "payment_expiring_body": "Abonamentul tau se apropie de data de expirare. Verifica starea planului tau.",
        "payment_invalid_method_body": "Metoda ta de plata pare invalida sau aproape de expirare.",
        "billing_update_title": "Actualizare facturare",
        "billing_update_body": "Exista o actualizare legata de abonamentul tau.",
        "invalid_plan_tier": "plan_tier invalid. Trebuie sa fie unul din: {tiers}.",
        "manual_vip_bypass": "Utilizatorii VIP manuali ocolesc logica de checkout si abonament.",
        "manual_vip_upgrade_bypass": "Utilizatorii VIP manuali ocolesc logica de upgrade al abonamentului.",
        "manual_vip_cancel_bypass": "Utilizatorii VIP manuali ocolesc logica de anulare a abonamentului.",
        "stripe_not_configured": "Stripe nu este configurat.",
        "no_stripe_customer": "Nu exista un client Stripe asociat acestui cont.",
        "no_active_subscription": "Nu exista un abonament activ. Foloseste fluxul de checkout pentru a te abona.",
        "no_active_subscription_cancel": "Nu exista un abonament activ de anulat.",
    },
    "en": {
        "payment_failed_title": "Payment failed",
        "payment_expiring_title": "Subscription expiring soon",
        "payment_invalid_method_title": "Update your payment method",
        "payment_failed_body": "We could not process your latest payment. Please check billing settings.",
        "payment_expiring_body": "Your subscription is approaching period end. Review your plan status.",
        "payment_invalid_method_body": "Your payment method appears invalid or near expiry.",
        "billing_update_title": "Billing update",
        "billing_update_body": "There is an update related to your subscription.",
        "invalid_plan_tier": "Invalid plan_tier. Must be one of: {tiers}.",
        "manual_vip_bypass": "Manual VIP users bypass checkout and subscription logic.",
        "manual_vip_upgrade_bypass": "Manual VIP users bypass subscription upgrade logic.",
        "manual_vip_cancel_bypass": "Manual VIP users bypass cancellation and subscription lifecycle logic.",
        "stripe_not_configured": "Stripe is not configured.",
        "no_stripe_customer": "No Stripe customer found for this account yet.",
        "no_active_subscription": "No active subscription found. Use the checkout flow to subscribe.",
        "no_active_subscription_cancel": "No active subscription found to cancel.",
    },
    "de": {
        "payment_failed_title": "Zahlung fehlgeschlagen",
        "payment_expiring_title": "Abonnement laeuft bald ab",
        "payment_invalid_method_title": "Zahlungsmethode aktualisieren",
        "payment_failed_body": "Ihre letzte Zahlung konnte nicht verarbeitet werden. Bitte pruefen Sie die Abrechnungseinstellungen.",
        "payment_expiring_body": "Ihr Abonnement naehert sich dem Ende des Zeitraums. Bitte ueberpruefen Sie Ihren Planstatus.",
        "payment_invalid_method_body": "Ihre Zahlungsmethode scheint ungueltig oder nahe dem Ablaufdatum zu sein.",
        "billing_update_title": "Abrechnungsupdate",
        "billing_update_body": "Es gibt ein Update in Bezug auf Ihr Abonnement.",
        "invalid_plan_tier": "Ungueltiger plan_tier. Muss einer der folgenden sein: {tiers}.",
        "manual_vip_bypass": "Manuelle VIP-Benutzer umgehen die Checkout- und Abonnementlogik.",
        "manual_vip_upgrade_bypass": "Manuelle VIP-Benutzer umgehen die Upgrade-Logik des Abonnements.",
        "manual_vip_cancel_bypass": "Manuelle VIP-Benutzer umgehen die Kuendigungs- und Abonnementlogik.",
        "stripe_not_configured": "Stripe ist nicht konfiguriert.",
        "no_stripe_customer": "Fuer dieses Konto wurde noch kein Stripe-Kunde gefunden.",
        "no_active_subscription": "Kein aktives Abonnement gefunden. Verwende den Checkout-Prozess zum Abonnieren.",
        "no_active_subscription_cancel": "Kein aktives Abonnement zum Kuendigen gefunden.",
    },
    "fr": {
        "payment_failed_title": "Paiement echoue",
        "payment_expiring_title": "Abonnement expirant bientot",
        "payment_invalid_method_title": "Mettre a jour votre moyen de paiement",
        "payment_failed_body": "Nous n avons pas pu traiter votre dernier paiement. Veuillez verifier les parametres de facturation.",
        "payment_expiring_body": "Votre abonnement approche de sa fin de periode. Verifiez votre statut de plan.",
        "payment_invalid_method_body": "Votre moyen de paiement semble invalide ou proche de l expiration.",
        "billing_update_title": "Mise a jour de facturation",
        "billing_update_body": "Il y a une mise a jour concernant votre abonnement.",
        "invalid_plan_tier": "plan_tier invalide. Doit etre l un des suivants: {tiers}.",
        "manual_vip_bypass": "Les utilisateurs VIP manuels contournent la logique de paiement et d abonnement.",
        "manual_vip_upgrade_bypass": "Les utilisateurs VIP manuels contournent la logique de mise a niveau d abonnement.",
        "manual_vip_cancel_bypass": "Les utilisateurs VIP manuels contournent la logique d annulation d abonnement.",
        "stripe_not_configured": "Stripe n est pas configure.",
        "no_stripe_customer": "Aucun client Stripe trouve pour ce compte.",
        "no_active_subscription": "Aucun abonnement actif trouve. Utilisez le processus de paiement pour vous abonner.",
        "no_active_subscription_cancel": "Aucun abonnement actif a annuler.",
    },
    "it": {
        "payment_failed_title": "Pagamento fallito",
        "payment_expiring_title": "Abbonamento in scadenza",
        "payment_invalid_method_title": "Aggiorna il metodo di pagamento",
        "payment_failed_body": "Non siamo riusciti a elaborare il tuo ultimo pagamento. Controlla le impostazioni di fatturazione.",
        "payment_expiring_body": "Il tuo abbonamento si sta avvicinando alla fine del periodo. Controlla lo stato del tuo piano.",
        "payment_invalid_method_body": "Il tuo metodo di pagamento sembra non valido o prossimo alla scadenza.",
        "billing_update_title": "Aggiornamento fatturazione",
        "billing_update_body": "C e un aggiornamento relativo al tuo abbonamento.",
        "invalid_plan_tier": "plan_tier non valido. Deve essere uno dei seguenti: {tiers}.",
        "manual_vip_bypass": "Gli utenti VIP manuali bypassano la logica di checkout e abbonamento.",
        "manual_vip_upgrade_bypass": "Gli utenti VIP manuali bypassano la logica di aggiornamento abbonamento.",
        "manual_vip_cancel_bypass": "Gli utenti VIP manuali bypassano la logica di cancellazione abbonamento.",
        "stripe_not_configured": "Stripe non e configurato.",
        "no_stripe_customer": "Nessun cliente Stripe trovato per questo account.",
        "no_active_subscription": "Nessun abbonamento attivo trovato. Usa il flusso di checkout per abbonarti.",
        "no_active_subscription_cancel": "Nessun abbonamento attivo da annullare.",
    },
    "es": {
        "payment_failed_title": "Pago fallido",
        "payment_expiring_title": "Suscripcion por vencer",
        "payment_invalid_method_title": "Actualiza tu metodo de pago",
        "payment_failed_body": "No pudimos procesar tu ultimo pago. Por favor revisa la configuracion de facturacion.",
        "payment_expiring_body": "Tu suscripcion se acerca al final del periodo. Revisa el estado de tu plan.",
        "payment_invalid_method_body": "Tu metodo de pago parece invalido o proximo a vencer.",
        "billing_update_title": "Actualizacion de facturacion",
        "billing_update_body": "Hay una actualizacion relacionada con tu suscripcion.",
        "invalid_plan_tier": "plan_tier invalido. Debe ser uno de: {tiers}.",
        "manual_vip_bypass": "Los usuarios VIP manuales omiten la logica de pago y suscripcion.",
        "manual_vip_upgrade_bypass": "Los usuarios VIP manuales omiten la logica de actualizacion de suscripcion.",
        "manual_vip_cancel_bypass": "Los usuarios VIP manuales omiten la logica de cancelacion de suscripcion.",
        "stripe_not_configured": "Stripe no esta configurado.",
        "no_stripe_customer": "No se encontro cliente de Stripe para esta cuenta.",
        "no_active_subscription": "No se encontro suscripcion activa. Usa el flujo de pago para suscribirte.",
        "no_active_subscription_cancel": "No se encontro suscripcion activa para cancelar.",
    },
    "pl": {
        "payment_failed_title": "Platnosc nie powiodla sie",
        "payment_expiring_title": "Subskrypcja wkrotce wygasnie",
        "payment_invalid_method_title": "Zaktualizuj metode platnosci",
        "payment_failed_body": "Nie mogligmy przetworzyc Twojej ostatniej platnosci. Sprawdz ustawienia rozliczen.",
        "payment_expiring_body": "Twoja subskrypcja zblizy sie do konca okresu. Sprawdz status swojego planu.",
        "payment_invalid_method_body": "Twoja metoda platnosci wydaje sie nieprawidlowa lub bliska wygasniecia.",
        "billing_update_title": "Aktualizacja rozliczen",
        "billing_update_body": "Nastapila aktualizacja dotyczaca Twojej subskrypcji.",
        "invalid_plan_tier": "Nieprawidlowy plan_tier. Musi byc jednym z: {tiers}.",
        "manual_vip_bypass": "Reczni uzytkownicy VIP pomijaja logike kasy i subskrypcji.",
        "manual_vip_upgrade_bypass": "Reczni uzytkownicy VIP pomijaja logike aktualizacji subskrypcji.",
        "manual_vip_cancel_bypass": "Reczni uzytkownicy VIP pomijaja logike anulowania subskrypcji.",
        "stripe_not_configured": "Stripe nie jest skonfigurowany.",
        "no_stripe_customer": "Nie znaleziono klienta Stripe dla tego konta.",
        "no_active_subscription": "Nie znaleziono aktywnej subskrypcji. Uzyj procesu kasy, aby sie zapisac.",
        "no_active_subscription_cancel": "Nie znaleziono aktywnej subskrypcji do anulowania.",
    },
}


def _payment_text(user, key: str, **kwargs) -> str:
    text = translate(_PAYMENT_COPY, get_user_language(user)).get(key, _PAYMENT_COPY["en"][key])
    return text.format(**kwargs) if kwargs else text


def _build_promo_state_for_user(user: User) -> dict:
    is_manual_vip = _is_manual_vip(user)
    eligible = bool(_is_early_discount_applicable(user, "premium")) if not is_manual_vip else False
    return {
        "promo_key": "premium_early_discount",
        "is_active": eligible,
        "discount_percent": EARLY_DISCOUNT_PERCENT if eligible else 0,
        "target_plan": "premium",
        "manual_vip": is_manual_vip,
    }


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
        "payment_failed": _payment_text(user, "payment_failed_title"),
        "payment_expiring": _payment_text(user, "payment_expiring_title"),
        "payment_invalid_method": _payment_text(user, "payment_invalid_method_title"),
    }
    body_map = {
        "payment_failed": _payment_text(user, "payment_failed_body"),
        "payment_expiring": _payment_text(user, "payment_expiring_body"),
        "payment_invalid_method": _payment_text(user, "payment_invalid_method_body"),
    }
    create_in_app_notification(
        user,
        notification_type,
        title_map.get(notification_type, _payment_text(user, "billing_update_title")),
        body_map.get(notification_type, _payment_text(user, "billing_update_body")),
        context_key=context_key,
    )


def _price_id_to_tier(price_id: str) -> str:
    """Reverse-map a Stripe price ID to an internal plan tier."""
    return plan_tier_from_stripe_price_id(price_id)


def _is_early_discount_applicable(user: User, requested_plan_tier: str) -> bool:
    is_discount_eligible = bool(getattr(user, "early_discount_eligible", False)) and not _is_manual_vip(user)
    return (
        requested_plan_tier == "premium"
        and is_discount_eligible
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
            return Response(
                {"detail": _payment_text(request.user, "invalid_plan_tier", tiers=", ".join(sorted(VALID_PLAN_TIERS)))},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if _is_manual_vip(user):
            return Response(
                {
                    "url": None,
                    "internal_activation": False,
                    "manual_vip": True,
                    "effective_tier": User.PLAN_VIP,
                    "detail": _payment_text(user, "manual_vip_bypass"),
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
                {"detail": _payment_text(request.user, "stripe_not_configured")},
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
                {"detail": _payment_text(request.user, "stripe_not_configured")},
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
                {"detail": _payment_text(request.user, "no_stripe_customer")},
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


class PromoStateView(APIView):
    """Return dynamic promo state for the current user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(_build_promo_state_for_user(request.user), status=status.HTTP_200_OK)


class UpgradeSubscriptionView(APIView):
    """Upgrade or downgrade an existing Stripe subscription in-place."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [UpgradeSessionRateThrottle]

    @require_feature("payment_upgrade")
    def post(self, request):
        plan_tier = (request.data.get("plan_tier") or "premium").lower()
        if plan_tier not in VALID_PLAN_TIERS:
            return Response(
                {"detail": _payment_text(request.user, "invalid_plan_tier", tiers=", ".join(sorted(VALID_PLAN_TIERS)))},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if _is_manual_vip(user):
            return Response(
                {
                    "upgraded": False,
                    "manual_vip": True,
                    "effective_tier": User.PLAN_VIP,
                    "detail": _payment_text(user, "manual_vip_upgrade_bypass"),
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
                {"detail": _payment_text(request.user, "no_active_subscription")},
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
                    "detail": _payment_text(user, "manual_vip_cancel_bypass"),
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
                {"detail": _payment_text(request.user, "no_active_subscription_cancel")},
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

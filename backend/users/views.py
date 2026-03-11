from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, get_connection
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
import jwt
from ai.models import AILog, Conversation
from core.models import UserWellbeingCheckin
from core.system_config import get_apple_client_id, get_google_client_id, get_system_config
from journal.models import JournalEntry
from payments.models import Payment
from profiles.models import UserProfile

from .models import User
from .serializers import (
    PasswordChangeSerializer,
    SocialLoginSerializer,
    PasswordRecoveryRequestSerializer,
    PasswordResetConfirmSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserSerializer,
)


_DELETED_ACCOUNT_EMAIL = "deleted.account@doisense.local"


def _build_deleted_email(user_id: int) -> str:
    return f"deleted.user.{user_id}@doisense.local"


def _redact_known_identifiers(text: str, user: User) -> str:
    if not text:
        return text

    redacted = text
    replacements = [
        user.email,
        user.first_name,
        user.last_name,
        user.phone_contact,
    ]
    for value in replacements:
        value = (value or "").strip()
        if value:
            redacted = redacted.replace(value, "[redacted]")
    return redacted


def _anonymize_conversations(user: User) -> None:
    conversations = list(Conversation.objects.filter(user=user))
    for conversation in conversations:
        conversation.user = None
        conversation.user_message = _redact_known_identifiers(conversation.user_message, user)
        conversation.ai_response = _redact_known_identifiers(conversation.ai_response, user)
    if conversations:
        Conversation.objects.bulk_update(
            conversations,
            ["user", "user_message", "ai_response"],
        )


def _anonymize_user(user: User) -> None:
    _anonymize_conversations(user)
    AILog.objects.filter(user=user).update(user=None)
    JournalEntry.objects.filter(user=user).delete()
    UserWellbeingCheckin.objects.filter(user=user).delete()
    UserProfile.objects.filter(user=user).update(
        preferred_tone="",
        sensitivities="",
        communication_style="",
        emotional_baseline="",
        keywords={},
    )
    Payment.objects.filter(user=user).update(
        stripe_customer_id="",
        stripe_subscription_id="",
        status="cancelled",
        plan_tier=User.PLAN_BASIC,
    )

    user.email = _build_deleted_email(user.id)
    user.first_name = ""
    user.last_name = ""
    user.phone_contact = ""
    user.tax_region = ""
    user.is_active = False
    user.is_staff = False
    user.is_superuser = False
    user.is_premium = False
    user.plan_tier = User.PLAN_FREE
    user.trial_started_at = None
    user.trial_ends_at = None
    user.terms_accepted_at = None
    user.privacy_accepted_at = None
    user.ai_usage_accepted_at = None
    user.legal_consent_language = ""
    user.onboarding_completed = True
    user.set_unusable_password()
    user.save(
        update_fields=[
            "email",
            "first_name",
            "last_name",
            "phone_contact",
            "tax_region",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_premium",
            "plan_tier",
            "trial_started_at",
            "trial_ends_at",
            "terms_accepted_at",
            "privacy_accepted_at",
            "ai_usage_accepted_at",
            "legal_consent_language",
            "onboarding_completed",
            "password",
        ]
    )


def _build_personal_data_export(user: User) -> dict:
    profile = UserProfile.objects.filter(user=user).first()
    payments = list(
        Payment.objects.filter(user=user)
        .order_by("-created_at")
        .values("status", "plan_tier", "created_at", "updated_at")
    )
    journal_entries = list(
        JournalEntry.objects.filter(user=user)
        .select_related("question")
        .order_by("-created_at")
        .values(
            "id",
            "content",
            "emotions",
            "created_at",
            "question_id",
            "question__text",
            "question__category",
            "question__language",
        )
    )
    conversations = list(
        Conversation.objects.filter(user=user)
        .order_by("-created_at")
        .values(
            "id",
            "module",
            "plan_tier",
            "user_message",
            "ai_response",
            "created_at",
        )
    )
    wellbeing_checkins = list(
        UserWellbeingCheckin.objects.filter(user=user)
        .order_by("-created_at")
        .values("id", "mood", "energy_level", "created_at")
    )

    return {
        "generated_at": timezone.now().isoformat(),
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_contact": user.phone_contact,
            "tax_region": user.tax_region,
            "language": user.language,
            "plan_tier": user.plan_tier,
            "trial_started_at": user.trial_started_at,
            "trial_ends_at": user.trial_ends_at,
            "created_at": user.created_at,
            "terms_accepted_at": user.terms_accepted_at,
            "privacy_accepted_at": user.privacy_accepted_at,
            "ai_usage_accepted_at": user.ai_usage_accepted_at,
            "legal_consent_language": user.legal_consent_language,
        },
        "profile": {
            "preferred_tone": profile.preferred_tone if profile else "",
            "sensitivities": profile.sensitivities if profile else "",
            "communication_style": profile.communication_style if profile else "",
            "emotional_baseline": profile.emotional_baseline if profile else "",
            "keywords": profile.keywords if profile else {},
        },
        "payments": payments,
        "journal_entries": journal_entries,
        "conversations": conversations,
        "wellbeing_checkins": wellbeing_checkins,
    }


def _send_activation_email(user) -> None:
    config = get_system_config()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    language = (user.language or config.default_site_language or "ro").strip() or "ro"
    base_url = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    activation_url = f"{base_url}/{language}/auth/activate?uid={uid}&token={token}"

    from_email = (
        config.contact_from_email
        or config.email_host_user
        or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@doisense.app")
    )

    connection = get_connection(
        host=config.email_host,
        port=config.email_port,
        username=config.email_host_user,
        password=config.email_host_password,
        use_tls=config.email_use_tls,
        use_ssl=config.email_use_ssl,
        fail_silently=False,
    )

    message = EmailMessage(
        subject="Confirm your Doisense account",
        body=(
            "Welcome to Doisense!\n\n"
            "Please confirm your email address to activate your account:\n"
            f"{activation_url}\n\n"
            "If you did not create this account, you can safely ignore this email."
        ),
        from_email=from_email,
        to=[user.email],
        connection=connection,
    )
    message.send()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        try:
            _send_activation_email(user)
        except Exception:
            user.delete()
            return Response(
                {"detail": "We could not send the activation email right now. Please try again."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            {"detail": "Account created. Please confirm your email to activate your account."},
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        if not uid or not token:
            return Response(
                {"detail": "uid and token are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.filter(pk=user_id).first()
        except Exception:
            user = None

        if not user or not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_active:
            return Response(
                {"detail": "Account is already activated."},
                status=status.HTTP_200_OK,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])
        user.start_trial()
        return Response({"detail": "Account activated successfully."}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        password = serializer.validated_data["password"]
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {"detail": "Account is not activated. Please confirm your email first."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            access = str(token.access_token)
            return Response({"access": access})
        except Exception:
            return Response(
                {"detail": "Token is invalid or expired"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        allowed_fields = {"first_name", "last_name", "phone_contact", "language", "tax_region", "onboarding_completed"}
        payload = {key: value for key, value in request.data.items() if key in allowed_fields}
        serializer = UserSerializer(request.user, data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        user = request.user
        if user.email in {_DELETED_ACCOUNT_EMAIL, _build_deleted_email(user.id)}:
            return Response(
                {"detail": "This account cannot be deleted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            _anonymize_user(user)

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payload = _build_personal_data_export(request.user)
        response = JsonResponse(payload)
        response["Content-Disposition"] = 'attachment; filename="doisense-personal-data.json"'
        return response


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)


class SocialLoginView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def _verify_google_token(raw_token: str):
        google_client_id = get_google_client_id()
        if not google_client_id:
            raise ValueError("Google login is not configured")
        return google_id_token.verify_oauth2_token(
            raw_token,
            google_requests.Request(),
            google_client_id,
        )

    @staticmethod
    def _verify_apple_token(raw_token: str):
        apple_client_id = get_apple_client_id()
        if not apple_client_id:
            raise ValueError("Apple login is not configured")
        jwk_client = jwt.PyJWKClient("https://appleid.apple.com/auth/keys")
        signing_key = jwk_client.get_signing_key_from_jwt(raw_token)
        return jwt.decode(
            raw_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=apple_client_id,
            issuer="https://appleid.apple.com",
        )

    def post(self, request):
        serializer = SocialLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        provider = serializer.validated_data["provider"]
        raw_token = serializer.validated_data["id_token"]
        language = serializer.validated_data["language"]

        try:
            if provider == "google":
                claims = self._verify_google_token(raw_token)
            else:
                claims = self._verify_apple_token(raw_token)
        except Exception:
            return Response(
                {"detail": "Invalid social token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = (claims.get("email") or "").lower().strip()
        if not email:
            return Response(
                {"detail": "Email is not available from social provider"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()
        if not user:
            if not (
                serializer.validated_data.get("accepted_terms")
                and serializer.validated_data.get("accepted_privacy")
                and serializer.validated_data.get("accepted_ai_usage")
            ):
                return Response(
                    {"detail": "You must accept the Terms, Privacy Policy, and AI Usage Agreement before creating an account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            accepted_at = timezone.now()
            user = User.objects.create_user(
                email=email,
                password=None,
                language=language,
                onboarding_completed=False,
                terms_accepted_at=accepted_at,
                privacy_accepted_at=accepted_at,
                ai_usage_accepted_at=accepted_at,
                legal_consent_language=language,
            )
            user.set_unusable_password()
            user.save(update_fields=["password"])

        if not user.is_active:
            return Response(
                {"detail": "User account is disabled"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class PasswordRecoveryRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordRecoveryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower().strip()
        user = User.objects.filter(email=email).first()
        if user and user.is_active:
            config = get_system_config()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            language = (user.language or config.default_site_language or "ro").strip() or "ro"
            base_url = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
            reset_url = f"{base_url}/{language}/auth/recover?uid={uid}&token={token}"

            from_email = (
                config.contact_from_email
                or config.email_host_user
                or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@doisense.app")
            )
            to_email = [email]

            try:
                connection = get_connection(
                    host=config.email_host,
                    port=config.email_port,
                    username=config.email_host_user,
                    password=config.email_host_password,
                    use_tls=config.email_use_tls,
                    use_ssl=config.email_use_ssl,
                    fail_silently=False,
                )
                message = EmailMessage(
                    subject="Doisense password recovery",
                    body=(
                        "You requested a password reset. Use the link below to set a new password:\n\n"
                        f"{reset_url}\n\n"
                        "If you did not request this, you can safely ignore this email."
                    ),
                    from_email=from_email,
                    to=to_email,
                    connection=connection,
                )
                message.send()
            except Exception:
                # Return generic success response to avoid account enumeration.
                pass

        return Response(
            {"detail": "If this email exists, a recovery link has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.filter(pk=user_id).first()
        except Exception:
            user = None

        if not user or not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, get_connection
from django.http import JsonResponse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
import jwt
from core.analytics import track_event
from core.system_config import get_apple_client_id, get_google_client_id, get_system_config

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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_register"

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

        track_event(
            "user_registered",
            source="backend",
            user=user,
            properties={"auth_method": "email"},
        )

        return Response(
            {"detail": "Account created. Please confirm your email to activate your account."},
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_activate"

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
        track_event(
            "user_activated",
            source="backend",
            user=user,
            properties={"auth_method": "email"},
        )
        return Response({"detail": "Account activated successfully."}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_refresh"

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
        from ai.models import Conversation
        from core.models import UserWellbeingCheckin
        from journal.models import JournalEntry

        user = request.user

        # Remove user-owned personal records while preserving anonymized conversations.
        JournalEntry.objects.filter(user=user).delete()
        UserWellbeingCheckin.objects.filter(user=user).delete()

        conversations = Conversation.objects.filter(user=user)
        for conversation in conversations:
            if user.email:
                conversation.user_message = conversation.user_message.replace(user.email, "[redacted]")
                conversation.ai_response = conversation.ai_response.replace(user.email, "[redacted]")
            conversation.user = None
            conversation.save(update_fields=["user", "user_message", "ai_response"])

        user.is_active = False
        user.is_premium = False
        user.vip_manual_override = False
        user.early_discount_eligible = False
        user.plan_tier = User.PLAN_FREE
        user.trial_started_at = None
        user.trial_ends_at = None
        user.email = f"deleted.user.{user.id}@doisense.local"
        user.first_name = ""
        user.last_name = ""
        user.phone_contact = ""
        user.tax_region = ""
        user.onboarding_completed = True
        user.set_unusable_password()
        user.save(
            update_fields=[
                "is_active",
                "is_premium",
                "vip_manual_override",
                "early_discount_eligible",
                "plan_tier",
                "trial_started_at",
                "trial_ends_at",
                "email",
                "first_name",
                "last_name",
                "phone_contact",
                "tax_region",
                "onboarding_completed",
                "password",
            ]
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from ai.models import Conversation
        from core.models import UserWellbeingCheckin
        from journal.models import JournalEntry

        user = request.user
        payload = {
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_contact": user.phone_contact,
                "tax_region": user.tax_region,
                "language": user.language,
                "is_premium": user.is_premium,
                "plan_tier": user.plan_tier,
                "onboarding_completed": user.onboarding_completed,
                "created_at": user.created_at,
            },
            "journal_entries": [
                {
                    "id": entry.id,
                    "question_id": entry.question_id,
                    "content": entry.content,
                    "emotions": entry.emotions,
                    "created_at": entry.created_at,
                }
                for entry in JournalEntry.objects.filter(user=user).order_by("-created_at")
            ],
            "conversations": [
                {
                    "id": conversation.id,
                    "module": conversation.module,
                    "plan_tier": conversation.plan_tier,
                    "user_message": conversation.user_message,
                    "ai_response": conversation.ai_response,
                    "created_at": conversation.created_at,
                }
                for conversation in Conversation.objects.filter(user=user).order_by("-created_at")
            ],
            "wellbeing_checkins": [
                {
                    "id": checkin.id,
                    "mood": checkin.mood,
                    "energy_level": checkin.energy_level,
                    "created_at": checkin.created_at,
                }
                for checkin in UserWellbeingCheckin.objects.filter(user=user).order_by("-created_at")
            ],
        }
        response = JsonResponse(payload)
        response["Content-Disposition"] = 'attachment; filename="doisense-personal-data.json"'
        return response


class ReOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.onboarding_completed = False
        user.save(update_fields=["onboarding_completed"])
        track_event(
            "onboarding_restarted",
            source="backend",
            user=user,
            properties={"entrypoint": "profile"},
        )
        return Response({"onboarding_completed": False}, status=status.HTTP_200_OK)


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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_social"

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
            if not request.data.get("accepted_terms"):
                return Response(
                    {"detail": "Terms must be accepted for new accounts."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not request.data.get("accepted_privacy"):
                return Response(
                    {"detail": "Privacy policy must be accepted for new accounts."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not request.data.get("accepted_ai_usage"):
                return Response(
                    {"detail": "AI usage policy must be accepted for new accounts."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = User.objects.create_user(
                email=email,
                password=None,
                language=language,
                onboarding_completed=False,
            )
            now = timezone.now()
            user.terms_accepted_at = now
            user.privacy_accepted_at = now
            user.ai_usage_accepted_at = now
            user.legal_consent_language = language
            user.set_unusable_password()
            user.save(
                update_fields=[
                    "password",
                    "terms_accepted_at",
                    "privacy_accepted_at",
                    "ai_usage_accepted_at",
                    "legal_consent_language",
                ]
            )
            track_event(
                "user_registered",
                source="backend",
                user=user,
                properties={"auth_method": provider},
            )

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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_recover"

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
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_reset_confirm"

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

        try:
            validate_password(new_password, user)
        except ValidationError as exc:
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

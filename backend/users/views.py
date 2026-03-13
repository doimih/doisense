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
from core.i18n import get_request_language, get_user_language, translate
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


AUTH_COPY = {
    "ro": {
        "activation_email_subject": "Confirma contul tau Doisense",
        "activation_email_body": (
            "Bine ai venit la Doisense!\n\n"
            "Te rugam sa confirmi adresa de email pentru a-ti activa contul:\n"
            "{activation_url}\n\n"
            "Daca nu ai creat acest cont, poti ignora in siguranta acest email."
        ),
        "activation_email_failed": "Nu am putut trimite emailul de activare acum. Te rugam sa incerci din nou.",
        "account_created": "Cont creat. Verifica emailul pentru a activa contul.",
        "uid_token_required": "uid si token sunt obligatorii.",
        "invalid_activation_link": "Link de activare invalid sau expirat.",
        "account_already_activated": "Contul este deja activat.",
        "account_activated": "Cont activat cu succes.",
        "invalid_credentials": "Datele de autentificare sunt invalide.",
        "account_not_activated": "Contul nu este activat. Confirma mai intai adresa de email.",
        "refresh_required": "Tokenul de refresh este obligatoriu.",
        "token_invalid": "Token invalid sau expirat.",
        "password_updated": "Parola a fost actualizata cu succes.",
        "invalid_social_token": "Token social invalid.",
        "social_email_missing": "Emailul nu este disponibil de la furnizorul social.",
        "terms_required": "Trebuie sa accepti Termenii pentru conturile noi.",
        "privacy_required": "Trebuie sa accepti Politica de confidentialitate pentru conturile noi.",
        "ai_usage_required": "Trebuie sa accepti politica de utilizare AI pentru conturile noi.",
        "user_disabled": "Contul de utilizator este dezactivat.",
        "recovery_email_subject": "Recuperare parola Doisense",
        "recovery_email_body": (
            "Ai cerut resetarea parolei. Foloseste linkul de mai jos pentru a seta o parola noua:\n\n"
            "{reset_url}\n\n"
            "Daca nu ai facut aceasta cerere, poti ignora in siguranta acest email."
        ),
        "recovery_link_sent": "Daca acest email exista, a fost trimis un link de recuperare.",
        "invalid_reset_link": "Link de resetare invalid sau expirat.",
        "invalid_password": "Parola noua nu respecta cerintele de securitate.",
    },
    "en": {
        "activation_email_subject": "Confirm your Doisense account",
        "activation_email_body": (
            "Welcome to Doisense!\n\n"
            "Please confirm your email address to activate your account:\n"
            "{activation_url}\n\n"
            "If you did not create this account, you can safely ignore this email."
        ),
        "activation_email_failed": "We could not send the activation email right now. Please try again.",
        "account_created": "Account created. Please confirm your email to activate your account.",
        "uid_token_required": "uid and token are required.",
        "invalid_activation_link": "Invalid or expired activation link.",
        "account_already_activated": "Account is already activated.",
        "account_activated": "Account activated successfully.",
        "invalid_credentials": "Invalid credentials.",
        "account_not_activated": "Account is not activated. Please confirm your email first.",
        "refresh_required": "Refresh token is required.",
        "token_invalid": "Token is invalid or expired.",
        "password_updated": "Password updated successfully.",
        "invalid_social_token": "Invalid social token.",
        "social_email_missing": "Email is not available from the social provider.",
        "terms_required": "Terms must be accepted for new accounts.",
        "privacy_required": "Privacy policy must be accepted for new accounts.",
        "ai_usage_required": "AI usage policy must be accepted for new accounts.",
        "user_disabled": "User account is disabled.",
        "recovery_email_subject": "Doisense password recovery",
        "recovery_email_body": (
            "You requested a password reset. Use the link below to set a new password:\n\n"
            "{reset_url}\n\n"
            "If you did not request this, you can safely ignore this email."
        ),
        "recovery_link_sent": "If this email exists, a recovery link has been sent.",
        "invalid_reset_link": "Invalid or expired reset link.",
        "invalid_password": "The new password does not meet the security requirements.",
    },
    "de": {
        "activation_email_subject": "Bestaetige dein Doisense-Konto",
        "activation_email_body": (
            "Willkommen bei Doisense!\n\n"
            "Bitte bestaetige deine E-Mail-Adresse, um dein Konto zu aktivieren:\n"
            "{activation_url}\n\n"
            "Falls du dieses Konto nicht erstellt hast, kannst du diese E-Mail ignorieren."
        ),
        "activation_email_failed": "Die Aktivierungs-E-Mail konnte momentan nicht gesendet werden. Bitte versuche es erneut.",
        "account_created": "Konto erstellt. Bitte bestaetige deine E-Mail, um das Konto zu aktivieren.",
        "uid_token_required": "uid und token sind erforderlich.",
        "invalid_activation_link": "Ungueltiger oder abgelaufener Aktivierungslink.",
        "account_already_activated": "Das Konto ist bereits aktiviert.",
        "account_activated": "Konto erfolgreich aktiviert.",
        "invalid_credentials": "Ungueltige Zugangsdaten.",
        "account_not_activated": "Das Konto ist noch nicht aktiviert. Bitte bestaetige zuerst deine E-Mail.",
        "refresh_required": "Ein Refresh-Token ist erforderlich.",
        "token_invalid": "Token ist ungueltig oder abgelaufen.",
        "password_updated": "Passwort erfolgreich aktualisiert.",
        "invalid_social_token": "Ungueltiges Social-Login-Token.",
        "social_email_missing": "Vom Social-Provider wurde keine E-Mail-Adresse bereitgestellt.",
        "terms_required": "Die Nutzungsbedingungen muessen fuer neue Konten akzeptiert werden.",
        "privacy_required": "Die Datenschutzrichtlinie muss fuer neue Konten akzeptiert werden.",
        "ai_usage_required": "Die KI-Nutzungsrichtlinie muss fuer neue Konten akzeptiert werden.",
        "user_disabled": "Das Benutzerkonto ist deaktiviert.",
        "recovery_email_subject": "Doisense Passwort-Wiederherstellung",
        "recovery_email_body": (
            "Du hast eine Passwortzuruecksetzung angefordert. Nutze den Link unten, um ein neues Passwort zu setzen:\n\n"
            "{reset_url}\n\n"
            "Falls du dies nicht angefordert hast, kannst du diese E-Mail ignorieren."
        ),
        "recovery_link_sent": "Falls diese E-Mail existiert, wurde ein Wiederherstellungslink gesendet.",
        "invalid_reset_link": "Ungueltiger oder abgelaufener Reset-Link.",
        "invalid_password": "Das neue Passwort erfuellt die Sicherheitsanforderungen nicht.",
    },
    "fr": {
        "activation_email_subject": "Confirmez votre compte Doisense",
        "activation_email_body": (
            "Bienvenue sur Doisense !\n\n"
            "Veuillez confirmer votre adresse e-mail pour activer votre compte :\n"
            "{activation_url}\n\n"
            "Si vous n'avez pas cree ce compte, vous pouvez ignorer cet e-mail."
        ),
        "activation_email_failed": "Nous n'avons pas pu envoyer l'e-mail d'activation pour le moment. Veuillez reessayer.",
        "account_created": "Compte cree. Veuillez confirmer votre e-mail pour activer votre compte.",
        "uid_token_required": "uid et token sont obligatoires.",
        "invalid_activation_link": "Lien d'activation invalide ou expire.",
        "account_already_activated": "Le compte est deja active.",
        "account_activated": "Compte active avec succes.",
        "invalid_credentials": "Identifiants invalides.",
        "account_not_activated": "Le compte n'est pas active. Veuillez d'abord confirmer votre e-mail.",
        "refresh_required": "Le jeton de rafraichissement est obligatoire.",
        "token_invalid": "Jeton invalide ou expire.",
        "password_updated": "Mot de passe mis a jour avec succes.",
        "invalid_social_token": "Jeton social invalide.",
        "social_email_missing": "L'adresse e-mail n'est pas disponible chez le fournisseur social.",
        "terms_required": "Les Conditions doivent etre acceptees pour les nouveaux comptes.",
        "privacy_required": "La Politique de confidentialite doit etre acceptee pour les nouveaux comptes.",
        "ai_usage_required": "La politique d'utilisation de l'IA doit etre acceptee pour les nouveaux comptes.",
        "user_disabled": "Le compte utilisateur est desactive.",
        "recovery_email_subject": "Recuperation du mot de passe Doisense",
        "recovery_email_body": (
            "Vous avez demande une reinitialisation du mot de passe. Utilisez le lien ci-dessous pour definir un nouveau mot de passe :\n\n"
            "{reset_url}\n\n"
            "Si vous n'avez pas fait cette demande, vous pouvez ignorer cet e-mail."
        ),
        "recovery_link_sent": "Si cet e-mail existe, un lien de recuperation a ete envoye.",
        "invalid_reset_link": "Lien de reinitialisation invalide ou expire.",
        "invalid_password": "Le nouveau mot de passe ne respecte pas les exigences de securite.",
    },
    "it": {
        "activation_email_subject": "Conferma il tuo account Doisense",
        "activation_email_body": (
            "Benvenuto su Doisense!\n\n"
            "Conferma il tuo indirizzo email per attivare l'account:\n"
            "{activation_url}\n\n"
            "Se non hai creato questo account, puoi ignorare questa email."
        ),
        "activation_email_failed": "Non siamo riusciti a inviare l'email di attivazione in questo momento. Riprova.",
        "account_created": "Account creato. Conferma la tua email per attivarlo.",
        "uid_token_required": "uid e token sono obbligatori.",
        "invalid_activation_link": "Link di attivazione non valido o scaduto.",
        "account_already_activated": "L'account e gia attivo.",
        "account_activated": "Account attivato con successo.",
        "invalid_credentials": "Credenziali non valide.",
        "account_not_activated": "L'account non e attivo. Conferma prima la tua email.",
        "refresh_required": "Il token di refresh e obbligatorio.",
        "token_invalid": "Token non valido o scaduto.",
        "password_updated": "Password aggiornata con successo.",
        "invalid_social_token": "Token social non valido.",
        "social_email_missing": "L'email non e disponibile dal provider social.",
        "terms_required": "Devi accettare i Termini per i nuovi account.",
        "privacy_required": "Devi accettare l'informativa sulla privacy per i nuovi account.",
        "ai_usage_required": "Devi accettare la politica di utilizzo dell'AI per i nuovi account.",
        "user_disabled": "L'account utente e disabilitato.",
        "recovery_email_subject": "Recupero password Doisense",
        "recovery_email_body": (
            "Hai richiesto il reset della password. Usa il link qui sotto per impostarne una nuova:\n\n"
            "{reset_url}\n\n"
            "Se non hai effettuato questa richiesta, puoi ignorare questa email."
        ),
        "recovery_link_sent": "Se questa email esiste, e stato inviato un link di recupero.",
        "invalid_reset_link": "Link di reset non valido o scaduto.",
        "invalid_password": "La nuova password non soddisfa i requisiti di sicurezza.",
    },
    "es": {
        "activation_email_subject": "Confirma tu cuenta de Doisense",
        "activation_email_body": (
            "Bienvenido a Doisense.\n\n"
            "Confirma tu direccion de correo para activar tu cuenta:\n"
            "{activation_url}\n\n"
            "Si no creaste esta cuenta, puedes ignorar este correo."
        ),
        "activation_email_failed": "No pudimos enviar el correo de activacion en este momento. Intentalo de nuevo.",
        "account_created": "Cuenta creada. Confirma tu correo para activar la cuenta.",
        "uid_token_required": "uid y token son obligatorios.",
        "invalid_activation_link": "Enlace de activacion invalido o caducado.",
        "account_already_activated": "La cuenta ya esta activada.",
        "account_activated": "Cuenta activada correctamente.",
        "invalid_credentials": "Credenciales invalidas.",
        "account_not_activated": "La cuenta no esta activada. Confirma primero tu correo.",
        "refresh_required": "El token de refresco es obligatorio.",
        "token_invalid": "El token es invalido o ha caducado.",
        "password_updated": "Contrasena actualizada correctamente.",
        "invalid_social_token": "Token social invalido.",
        "social_email_missing": "El proveedor social no ha proporcionado el correo electronico.",
        "terms_required": "Debes aceptar los Terminos para las cuentas nuevas.",
        "privacy_required": "Debes aceptar la Politica de privacidad para las cuentas nuevas.",
        "ai_usage_required": "Debes aceptar la politica de uso de IA para las cuentas nuevas.",
        "user_disabled": "La cuenta de usuario esta deshabilitada.",
        "recovery_email_subject": "Recuperacion de contrasena de Doisense",
        "recovery_email_body": (
            "Has solicitado restablecer tu contrasena. Usa el siguiente enlace para crear una nueva:\n\n"
            "{reset_url}\n\n"
            "Si no solicitaste esto, puedes ignorar este correo."
        ),
        "recovery_link_sent": "Si este correo existe, se ha enviado un enlace de recuperacion.",
        "invalid_reset_link": "Enlace de restablecimiento invalido o caducado.",
        "invalid_password": "La nueva contrasena no cumple los requisitos de seguridad.",
    },
    "pl": {
        "activation_email_subject": "Potwierdz swoje konto Doisense",
        "activation_email_body": (
            "Witamy w Doisense.\n\n"
            "Potwierdz swoj adres e-mail, aby aktywowac konto:\n"
            "{activation_url}\n\n"
            "Jesli nie utworzyles tego konta, mozesz zignorowac ta wiadomosc."
        ),
        "activation_email_failed": "Nie udalo sie wyslac wiadomosci aktywacyjnej. Sprobuj ponownie.",
        "account_created": "Konto utworzone. Potwierdz email, aby je aktywowac.",
        "uid_token_required": "uid i token sa wymagane.",
        "invalid_activation_link": "Link aktywacyjny jest nieprawidlowy lub wygasl.",
        "account_already_activated": "Konto jest juz aktywne.",
        "account_activated": "Konto zostalo aktywowane.",
        "invalid_credentials": "Nieprawidlowe dane logowania.",
        "account_not_activated": "Konto nie jest aktywne. Najpierw potwierdz adres email.",
        "refresh_required": "Token odswiezania jest wymagany.",
        "token_invalid": "Token jest nieprawidlowy lub wygasl.",
        "password_updated": "Haslo zostalo zaktualizowane.",
        "invalid_social_token": "Nieprawidlowy token logowania spolecznosciowego.",
        "social_email_missing": "Adres email nie jest dostepny od dostawcy spolecznosciowego.",
        "terms_required": "Musisz zaakceptowac Regulamin dla nowych kont.",
        "privacy_required": "Musisz zaakceptowac Polityke prywatnosci dla nowych kont.",
        "ai_usage_required": "Musisz zaakceptowac zasady korzystania z AI dla nowych kont.",
        "user_disabled": "Konto uzytkownika jest wylaczone.",
        "recovery_email_subject": "Odzyskiwanie hasla Doisense",
        "recovery_email_body": (
            "Poproszono o reset hasla. Uzyj ponizszego linku, aby ustawic nowe haslo:\n\n"
            "{reset_url}\n\n"
            "Jesli to nie Ty wyslales te prosbe, mozesz zignorowac te wiadomosc."
        ),
        "recovery_link_sent": "Jesli ten email istnieje, wyslalismy link odzyskiwania.",
        "invalid_reset_link": "Link resetujacy jest nieprawidlowy lub wygasl.",
        "invalid_password": "Nowe haslo nie spelnia wymagan bezpieczenstwa.",
    },
}


def _auth_text(language: str, key: str, **kwargs) -> str:
    template = translate(AUTH_COPY, language)[key]
    return template.format(**kwargs) if kwargs else template


def _send_activation_email(user) -> None:
    config = get_system_config()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    language = get_user_language(user, default=get_user_language(None, default="ro"))
    base_url = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    activation_url = f"{base_url}/{language}/auth/activate?uid={uid}&token={token}"

    from_email = (
        config.contact_from_email
        or config.email_host_user
        or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@doisense.eu")
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
        subject=_auth_text(language, "activation_email_subject"),
        body=_auth_text(language, "activation_email_body", activation_url=activation_url),
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
        language = get_request_language(request, default="en")
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        try:
            _send_activation_email(user)
        except Exception:
            user.delete()
            return Response(
                {"detail": _auth_text(language, "activation_email_failed")},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        track_event(
            "user_registered",
            source="backend",
            user=user,
            properties={"auth_method": "email"},
        )

        return Response(
            {"detail": _auth_text(language, "account_created")},
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_activate"

    def post(self, request):
        language = get_request_language(request, default="en")
        uid = request.data.get("uid")
        token = request.data.get("token")
        if not uid or not token:
            return Response(
                {"detail": _auth_text(language, "uid_token_required")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.filter(pk=user_id).first()
        except Exception:
            user = None

        if not user or not default_token_generator.check_token(user, token):
            return Response(
                {"detail": _auth_text(language, "invalid_activation_link")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        language = get_request_language(request, user=user, default="en")

        if user.is_active:
            return Response(
                {"detail": _auth_text(language, "account_already_activated")},
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
        return Response({"detail": _auth_text(language, "account_activated")}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_login"

    def post(self, request):
        request_language = get_request_language(request, default="en")
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        password = serializer.validated_data["password"]
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response(
                {"detail": _auth_text(request_language, "invalid_credentials")},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            language = get_request_language(request, user=user, default="en")
            return Response(
                {"detail": _auth_text(language, "account_not_activated")},
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
        language = get_request_language(request, default="en")
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": _auth_text(language, "refresh_required")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            access = str(token.access_token)
            return Response({"access": access})
        except Exception:
            return Response(
                {"detail": _auth_text(language, "token_invalid")},
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
        language = get_request_language(request, user=request.user, default="en")
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        return Response({"detail": _auth_text(language, "password_updated")}, status=status.HTTP_200_OK)


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
        language = get_request_language(request, default="en")
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
                {"detail": _auth_text(language, "invalid_social_token")},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = (claims.get("email") or "").lower().strip()
        if not email:
            return Response(
                {"detail": _auth_text(language, "social_email_missing")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()
        if not user:
            if not request.data.get("accepted_terms"):
                return Response(
                    {"detail": _auth_text(language, "terms_required")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not request.data.get("accepted_privacy"):
                return Response(
                    {"detail": _auth_text(language, "privacy_required")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not request.data.get("accepted_ai_usage"):
                return Response(
                    {"detail": _auth_text(language, "ai_usage_required")},
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
            language = get_request_language(request, user=user, default="en")
            return Response(
                {"detail": _auth_text(language, "user_disabled")},
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
        request_language = get_request_language(request, default="en")
        serializer = PasswordRecoveryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"].lower().strip()
        user = User.objects.filter(email=email).first()
        if user and user.is_active:
            config = get_system_config()
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            language = get_user_language(user, default=get_user_language(None, default="ro"))
            base_url = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
            reset_url = f"{base_url}/{language}/auth/recover?uid={uid}&token={token}"

            from_email = (
                config.contact_from_email
                or config.email_host_user
                or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@doisense.eu")
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
                    subject=_auth_text(language, "recovery_email_subject"),
                    body=_auth_text(language, "recovery_email_body", reset_url=reset_url),
                    from_email=from_email,
                    to=to_email,
                    connection=connection,
                )
                message.send()
            except Exception:
                # Return generic success response to avoid account enumeration.
                pass

        return Response(
            {"detail": _auth_text(request_language, "recovery_link_sent")},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth_reset_confirm"

    def post(self, request):
        language = get_request_language(request, default="en")
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
                {"detail": _auth_text(language, "invalid_reset_link")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        language = get_request_language(request, user=user, default="en")

        try:
            validate_password(new_password, user)
        except ValidationError as exc:
            _ = exc
            return Response({"detail": _auth_text(language, "invalid_password")}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response({"detail": _auth_text(language, "password_updated")}, status=status.HTTP_200_OK)

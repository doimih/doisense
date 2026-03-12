from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from core.validators import validate_language

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    language = serializers.CharField(max_length=2, default="en", required=False)
    accepted_terms = serializers.BooleanField(write_only=True)
    accepted_privacy = serializers.BooleanField(write_only=True)
    accepted_ai_usage = serializers.BooleanField(write_only=True)
    first_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=120, required=False, allow_blank=True)
    phone_contact = serializers.CharField(max_length=30, required=False, allow_blank=True)
    tax_region = serializers.CharField(max_length=120, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "language",
            "accepted_terms",
            "accepted_privacy",
            "accepted_ai_usage",
            "first_name",
            "last_name",
            "phone_contact",
            "tax_region",
        )

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate_language(self, value):
        validate_language(value)
        return value

    def validate(self, attrs):
        if not attrs.get("accepted_terms"):
            raise serializers.ValidationError({"accepted_terms": "Terms must be accepted."})
        if not attrs.get("accepted_privacy"):
            raise serializers.ValidationError({"accepted_privacy": "Privacy policy must be accepted."})
        if not attrs.get("accepted_ai_usage"):
            raise serializers.ValidationError({"accepted_ai_usage": "AI usage policy must be accepted."})
        return attrs

    def create(self, validated_data):
        accepted_terms = validated_data.pop("accepted_terms", False)
        accepted_privacy = validated_data.pop("accepted_privacy", False)
        accepted_ai_usage = validated_data.pop("accepted_ai_usage", False)
        language = validated_data.get("language") or "en"

        user = User.objects.create_user(is_active=False, onboarding_completed=False, **validated_data)
        now = timezone.now()
        updates = []
        if accepted_terms:
            user.terms_accepted_at = now
            updates.append("terms_accepted_at")
        if accepted_privacy:
            user.privacy_accepted_at = now
            updates.append("privacy_accepted_at")
        if accepted_ai_usage:
            user.ai_usage_accepted_at = now
            updates.append("ai_usage_accepted_at")
        user.legal_consent_language = language
        updates.append("legal_consent_language")
        user.save(update_fields=updates)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordRecoveryRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        if not user.check_password(attrs["current_password"]):
            raise serializers.ValidationError({"current_password": "Current password is incorrect."})

        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New password confirmation does not match."}
            )

        validate_password(attrs["new_password"], user)
        return attrs


class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["google", "apple"])
    id_token = serializers.CharField(write_only=True)
    language = serializers.CharField(max_length=2, default="en", required=False)
    accepted_terms = serializers.BooleanField(required=False, write_only=True)
    accepted_privacy = serializers.BooleanField(required=False, write_only=True)
    accepted_ai_usage = serializers.BooleanField(required=False, write_only=True)

    def validate_language(self, value):
        validate_language(value)
        return value


class UserSerializer(serializers.ModelSerializer):
    membership_tier = serializers.SerializerMethodField()
    has_saved_card = serializers.SerializerMethodField()
    manual_vip = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_contact",
            "tax_region",
            "language",
            "is_premium",
            "plan_tier",
            "manual_vip",
            "early_discount_eligible",
            "onboarding_completed",
            "membership_tier",
            "has_saved_card",
            "is_superuser",
            "created_at",
        )
        read_only_fields = (
            "id",
            "email",
            "is_premium",
            "plan_tier",
            "manual_vip",
            "early_discount_eligible",
            "onboarding_completed",
            "membership_tier",
            "has_saved_card",
            "is_superuser",
            "created_at",
        )

    def get_membership_tier(self, obj):
        return "premium" if obj.effective_plan_tier() in (User.PLAN_PREMIUM, User.PLAN_VIP) else "normal"

    def get_manual_vip(self, obj):
        return bool(getattr(obj, "manual_vip", False))

    def get_has_saved_card(self, obj):
        return obj.payments.exclude(stripe_customer_id="").exclude(stripe_customer_id__isnull=True).exists()

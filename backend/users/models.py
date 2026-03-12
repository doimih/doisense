from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

from core.validators import validate_language


TRIAL_DAYS = 7
EARLY_DISCOUNT_USER_LIMIT = 500


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        return self.create_user(email, password, **kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    PLAN_FREE = "free"
    PLAN_TRIAL = "trial"
    PLAN_BASIC = "basic"
    PLAN_PREMIUM = "premium"
    PLAN_VIP = "vip"

    PLAN_CHOICES = [
        (PLAN_FREE, "Free"),
        (PLAN_TRIAL, "Trial"),
        (PLAN_BASIC, "Basic"),
        (PLAN_PREMIUM, "Premium"),
        (PLAN_VIP, "VIP"),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    phone_contact = models.CharField(max_length=30, blank=True)
    tax_region = models.CharField(max_length=120, blank=True)
    language = models.CharField(max_length=2, default="en", validators=[validate_language])
    is_premium = models.BooleanField(default=False)
    vip_manual_override = models.BooleanField(default=False)
    early_discount_eligible = models.BooleanField(default=False)
    plan_tier = models.CharField(max_length=10, choices=PLAN_CHOICES, default=PLAN_FREE)
    trial_started_at = models.DateTimeField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    privacy_accepted_at = models.DateTimeField(null=True, blank=True)
    ai_usage_accepted_at = models.DateTimeField(null=True, blank=True)
    legal_consent_language = models.CharField(max_length=2, blank=True, default="")
    onboarding_completed = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users_user"

    def __str__(self):
        return self.email

    def is_in_trial(self) -> bool:
        return (
            self.plan_tier == self.PLAN_TRIAL
            and self.trial_ends_at is not None
            and timezone.now() < self.trial_ends_at
        )

    def has_unlimited_platform_access(self) -> bool:
        return self.is_superuser or self.is_staff

    def effective_plan_tier(self) -> str:
        if self.has_unlimited_platform_access():
            return self.PLAN_VIP
        if self.plan_tier == self.PLAN_TRIAL and not self.is_in_trial():
            return self.PLAN_FREE
        if self.plan_tier in (self.PLAN_BASIC, self.PLAN_PREMIUM, self.PLAN_VIP) and not self.is_premium:
            return self.PLAN_FREE
        return self.plan_tier

    def has_paid_access(self) -> bool:
        if self.has_unlimited_platform_access():
            return True
        tier = self.effective_plan_tier()
        return tier in (self.PLAN_TRIAL, self.PLAN_BASIC, self.PLAN_PREMIUM, self.PLAN_VIP)

    def start_trial(self) -> None:
        if self.plan_tier != self.PLAN_FREE or self.trial_started_at is not None:
            return
        now = timezone.now()
        self.plan_tier = self.PLAN_TRIAL
        self.is_premium = True
        self.trial_started_at = now
        self.trial_ends_at = now + timezone.timedelta(days=TRIAL_DAYS)
        self.save(update_fields=["plan_tier", "is_premium", "trial_started_at", "trial_ends_at"])

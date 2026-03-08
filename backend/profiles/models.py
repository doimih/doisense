from django.conf import settings
from django.db import models

from core.validators import validate_language


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    preferred_tone = models.CharField(max_length=100, blank=True)
    sensitivities = models.TextField(blank=True)
    communication_style = models.CharField(max_length=100, blank=True)
    emotional_baseline = models.CharField(max_length=100, blank=True)
    keywords = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "profiles_userprofile"

    def __str__(self):
        return f"Profile of {self.user.email}"

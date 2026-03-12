from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import EARLY_DISCOUNT_USER_LIMIT, User
from profiles.models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

    eligible = instance.expected_early_discount_eligibility()
    if instance.early_discount_eligible != eligible:
        User.objects.filter(pk=instance.pk).update(early_discount_eligible=eligible)

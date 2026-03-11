import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="test@example.com", password="testpass123", language="en")


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def paid_user(db):
    from django.utils import timezone
    import datetime
    u = User.objects.create_user(email="paid@example.com", password="testpass123", language="en")
    u.plan_tier = "trial"
    u.is_premium = True
    u.trial_started_at = timezone.now() - datetime.timedelta(days=1)
    u.trial_ends_at = timezone.now() + datetime.timedelta(days=6)
    u.save()
    return u


@pytest.fixture
def paid_client(paid_user):
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken
    client = APIClient()
    refresh = RefreshToken.for_user(paid_user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def journal_question(db):
    from journal.models import JournalQuestion
    return JournalQuestion.objects.create(
        text="How do you feel today?",
        category="daily",
        language="en",
        active=True,
    )

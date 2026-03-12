import pytest

from core.admin_dashboard import _mrr_estimate
from core.middleware import SystemErrorLoggingMiddleware
from core.models import SystemErrorEvent
from payments.models import Payment


@pytest.mark.django_db
def test_mrr_includes_discounted_premium(user):
    Payment.objects.create(user=user, status="active", plan_tier="premium_discounted")
    assert _mrr_estimate() == 116.1


@pytest.mark.django_db
def test_exception_middleware_logs_system_error(rf, user):
    request = rf.get("/api/payments/subscribe/?plan=premium")
    request.user = user

    middleware = SystemErrorLoggingMiddleware(get_response=lambda req: None)
    middleware.process_exception(request, RuntimeError("boom"))

    event = SystemErrorEvent.objects.first()
    assert event is not None
    assert event.component == "api"
    assert event.status_code == 500
    assert event.error_type == "RuntimeError"

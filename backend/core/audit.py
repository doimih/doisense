from datetime import date, datetime
from decimal import Decimal

from django.db import models

from .models import AdminAuditLog

_SENSITIVE_KEYWORDS = (
    "password",
    "secret",
    "token",
    "key",
    "api",
    "credential",
)


def _serialize_value(value):
    if isinstance(value, models.Model):
        return str(value.pk)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _serialize_value(v) for k, v in value.items()}
    return value


def _is_sensitive(field_name: str) -> bool:
    normalized = (field_name or "").lower()
    return any(keyword in normalized for keyword in _SENSITIVE_KEYWORDS)


def extract_form_changes(form):
    before_data = {}
    after_data = {}
    for field_name in form.changed_data:
        if _is_sensitive(field_name):
            before_data[field_name] = "***"
            after_data[field_name] = "***"
            continue
        before_data[field_name] = _serialize_value(form.initial.get(field_name))
        after_data[field_name] = _serialize_value(form.cleaned_data.get(field_name))
    return before_data, after_data


def log_admin_change(*, actor, action: str, target_obj, before_data=None, after_data=None, reason: str = ""):
    if not actor or not getattr(actor, "is_authenticated", False):
        return
    AdminAuditLog.objects.create(
        actor=actor,
        action=action,
        target_model=target_obj._meta.label_lower,
        target_object_id=str(target_obj.pk),
        before_data=before_data or {},
        after_data=after_data or {},
        reason=reason,
    )

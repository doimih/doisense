"""Notification templates and sending logic."""

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.utils import timezone

from core.i18n import get_user_language
from core.localized_notifications import render_notification
from core.models import InAppNotification, NotificationDelivery
from core.system_config import get_system_config


def _get_mail_connection():
    """Get configured email connection from system config."""
    config = get_system_config()
    return get_connection(
        host=config.email_host,
        port=config.email_port,
        username=config.email_host_user,
        password=config.email_host_password,
        use_tls=config.email_use_tls,
        use_ssl=config.email_use_ssl,
        fail_silently=False,
    )


def _get_from_email():
    """Get configured from email address."""
    config = get_system_config()
    return (
        config.contact_from_email
        or config.email_host_user
        or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@doisense.eu")
    )


def was_notification_sent(user, notification_type: str, *, date=None, context_key: str = "") -> bool:
    sent_for_date = date or timezone.localdate()
    return NotificationDelivery.objects.filter(
        user=user,
        notification_type=notification_type,
        sent_for_date=sent_for_date,
        context_key=context_key,
    ).exists()


def record_notification_delivery(
    user,
    notification_type: str,
    *,
    date=None,
    context_key: str = "",
):
    sent_for_date = date or timezone.localdate()
    return NotificationDelivery.objects.get_or_create(
        user=user,
        notification_type=notification_type,
        sent_for_date=sent_for_date,
        context_key=context_key,
    )


def create_in_app_notification(
    user,
    notification_type: str,
    title: str,
    body: str,
    *,
    context_key: str = "",
):
    if context_key:
        existing = InAppNotification.objects.filter(
            user=user,
            notification_type=notification_type,
            context_key=context_key,
        ).first()
        if existing:
            return existing

    return InAppNotification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        body=body,
        context_key=context_key,
    )


def send_trial_expiration_warning(user, days_left: int) -> None:
    """Send trial expiration warning email (days 5, 6, 7)."""
    if bool(getattr(user, "manual_vip", False) or getattr(user, "vip_manual_override", False)):
        return

    language = get_user_language(user)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    payload = render_notification(
        "trial_expiration_warning",
        language,
        first_name=user.first_name,
        days_left=days_left,
        url=f"{frontend_base}/{language}/pricing",
    )

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=payload["subject"],
        body=payload["body"],
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_inactivity_reminder(user, days_inactive: int) -> None:
    """Send inactivity reminder email (e.g., no chat in 7+ days)."""
    language = get_user_language(user)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    payload = render_notification(
        "inactivity_reminder",
        language,
        first_name=user.first_name,
        days_inactive=days_inactive,
        url=f"{frontend_base}/{language}/chat",
    )

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=payload["subject"],
        body=payload["body"],
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_journal_reminder(user) -> None:
    """Send journal prompt reminder email (no entry yet today)."""
    language = get_user_language(user)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    payload = render_notification(
        "journal_reminder",
        language,
        first_name=user.first_name,
        url=f"{frontend_base}/{language}/journal",
    )

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=payload["subject"],
        body=payload["body"],
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_daily_plan_reminder(user) -> None:
    """Send daily reminder to review/start daily plan."""
    language = get_user_language(user)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    payload = render_notification(
        "daily_plan_reminder",
        language,
        first_name=user.first_name,
        url=f"{frontend_base}/{language}/chat?module=coaching",
    )

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=payload["subject"],
        body=payload["body"],
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_wellbeing_checkin_reminder(user) -> None:
    """Send reminder to complete daily wellbeing check-in."""
    language = get_user_language(user)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    payload = render_notification(
        "wellbeing_checkin_reminder",
        language,
        first_name=user.first_name,
        url=f"{frontend_base}/{language}/chat",
    )

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=payload["subject"],
        body=payload["body"],
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_upgrade_recommendation(user, reason: str) -> None:
    """Send targeted upgrade email based on user behavior."""
    if bool(getattr(user, "manual_vip", False) or getattr(user, "vip_manual_override", False)):
        return

    language = get_user_language(user)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    kind = {
        "journal_limit": "upgrade_recommendation_journal_limit",
        "report_limit": "upgrade_recommendation_report_limit",
    }.get(reason, "upgrade_recommendation_generic")
    payload = render_notification(
        kind,
        language,
        first_name=user.first_name,
        url=f"{frontend_base}/{language}/pricing",
    )

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=payload["subject"],
        body=payload["body"],
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_goal_reminder(user, goals: list[str], days_since_focus: int) -> None:
    """Send a goal-focused reminder using goals inferred from the user profile."""
    language = get_user_language(user)
    visible_goals = [goal.strip() for goal in goals if goal and goal.strip()][:3]
    goal_lines = "\n".join(f"- {goal}" for goal in visible_goals)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    payload = render_notification(
        "goal_reminder",
        language,
        first_name=user.first_name,
        days_since_focus=days_since_focus,
        goal_lines=goal_lines or "-",
        url=f"{frontend_base}/{language}/chat?module=coaching",
    )

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=payload["subject"],
        body=payload["body"],
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_payment_failed_notification(user) -> None:
    language = get_user_language(user)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    payload = render_notification(
        "payment_failed_notification",
        language,
        first_name=user.first_name,
        url=f"{frontend_base}/{language}/profile",
    )

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=payload["subject"],
        body=payload["body"],
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_payment_expiring_notification(user, period_end) -> None:
    language = get_user_language(user)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    end_label = period_end.strftime("%Y-%m-%d") if period_end else "soon"
    payload = render_notification(
        "payment_expiring_notification",
        language,
        first_name=user.first_name,
        end_label=end_label,
        url=f"{frontend_base}/{language}/profile",
    )

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=payload["subject"],
        body=payload["body"],
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_payment_invalid_method_notification(user) -> None:
    language = get_user_language(user)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
    payload = render_notification(
        "payment_invalid_method_notification",
        language,
        first_name=user.first_name,
        url=f"{frontend_base}/{language}/profile",
    )

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=payload["subject"],
        body=payload["body"],
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()

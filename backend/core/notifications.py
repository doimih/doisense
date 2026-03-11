"""Notification templates and sending logic."""

from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.utils import timezone

from core.models import NotificationDelivery
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
        or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@doisense.app")
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


def send_trial_expiration_warning(user, days_left: int) -> None:
    """Send trial expiration warning email (days 5, 6, 7)."""
    language = (user.language or "en").lower()
    
    if language.startswith("ro"):
        subject = f"⏰ Doar {days_left} zile rămase din trial gratuit!"
        body = f"""Salut {user.first_name or 'there'}!

Trialul tău gratuit expiră în {days_left} zile la Doisense.

Activa un abonament pentru a continua accesul la:
✓ Chat AI nelimitat
✓ Rapoarte și analize
✓ Planuri de wellness personalizate
✓ Și mult mai mult...

Alege planul care se potrivește ritmului tău și continuă creșterea personală.

=== Link rapid ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/ro/pricing

Cu atenție,
Echipa Doisense"""
    else:
        subject = f"⏰ Only {days_left} days left in your free trial!"
        body = f"""Hi {user.first_name or 'there'}!

Your free trial at Doisense expires in {days_left} days.

Activate a subscription to keep access to:
✓ Unlimited AI chat
✓ Reports and insights
✓ Personalized wellness plans
✓ And more...

Choose the plan that fits your rhythm and continue your growth journey.

=== Quick link ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/{language}/pricing

Warmly,
The Doisense Team"""

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_inactivity_reminder(user, days_inactive: int) -> None:
    """Send inactivity reminder email (e.g., no chat in 7+ days)."""
    language = (user.language or "en").lower()
    
    if language.startswith("ro"):
        subject = "❤️ Te-am găsit! Revino pe Doisense și continuă creșterea ta"
        body = f"""Salut {user.first_name or 'there'}!

Nu te-am mai văzut pe platformă de {days_inactive} zile. Ți-am dor de tine!

Ajutor zilnic la:
✓ Gestionarea stresului
✓ Dezvoltarea de obiceiuri sănătoase
✓ Înțelegerea ta emoțională
✓ Atingerea obiectivelor personale

Revino pe Doisense și reia dialogul cu AI coachul tău.

=== Intră acum ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/ro/chat

Te așteptam,
Doisense"""
    else:
        subject = "❤️ We miss you! Come back to Doisense and continue your journey"
        body = f"""Hi {user.first_name or 'there'}!

We haven't seen you on Doisense for {days_inactive} days. We miss you!

Daily support with:
✓ Stress management
✓ Building healthy habits
✓ Understanding your emotions
✓ Reaching your personal goals

Come back and reconnect with your AI coach.

=== Jump back in ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/{language}/chat

See you soon,
Doisense"""

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_journal_reminder(user) -> None:
    """Send journal prompt reminder email (no entry yet today)."""
    language = (user.language or "en").lower()
    
    if language.startswith("ro"):
        subject = "📔 Reflecție zilei - Ce ai pe gând azi?"
        body = f"""Salut {user.first_name or 'there'}!

Nu ai făcut o intrare în jurnal azi. Momentul é perfect pentru auto-reflecție.

Răspunde la întrebări personalizate și:
✓ Înțelege mai bine stările tale emoționale
✓ Identifică pattern-uri în comportament
✓ Construiești o bază pentru creștere personală

Deschide jurnal și dedică 5 minute pentru introspectie.

=== Deschide jurnal ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/ro/journal

Reflecția zilei,
Doisense"""
    else:
        subject = "📔 Reflection prompt - What's on your mind today?"
        body = f"""Hi {user.first_name or 'there'}!

You haven't made a journal entry yet today. This is a perfect moment for self-reflection.

Answer personalized prompts and:
✓ Understand your emotions better
✓ Spot patterns in your behavior
✓ Build a foundation for personal growth

Open your journal and spend 5 minutes with your thoughts.

=== Open journal ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/{language}/journal

Today's reflection,
Doisense"""

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_daily_plan_reminder(user) -> None:
    """Send daily reminder to review/start daily plan."""
    language = (user.language or "en").lower()
    
    if language.startswith("ro"):
        subject = "🎯 Planul tău pentru azi - Gata?"
        body = f"""Salut {user.first_name or 'there'}!

Cuvântul zilei: Intenție clară = succes clar.

Ia 2 minute să-ți planifici ziua:
✓ Ce 1-3 lucruri vrei să realizezi azi?
✓ Ce ți-ar da energie?
✓ Cum vei celebra gata-facerile?

Deschide chat-ul cu coachul tău și planifică-ți ziua. Rezultatele urmează.

=== Planifică azi ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/ro/chat?module=coaching

Mult succes,
Doisense"""
    else:
        subject = "🎯 Your plan for today - Ready?"
        body = f"""Hi {user.first_name or 'there'}!

Today's thought: Clear intention = clear success.

Spend 2 minutes planning your day:
✓ What 1–3 things do you want to accomplish?
✓ What will energize you?
✓ How will you celebrate your wins?

Chat with your coach and plan your day. Results follow.

=== Plan today ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/{language}/chat?module=coaching

Go for it,
Doisense"""

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_wellbeing_checkin_reminder(user) -> None:
    """Send reminder to complete daily wellbeing check-in."""
    language = (user.language or "en").lower()
    
    if language.startswith("ro"):
        subject = "💚 Check-in zilei - Cum te simți?"
        body = f"""Salut {user.first_name or 'there'}!

Starea ta emoțională contează. Ia 1 minut pentru check-in zilei:
✓ Care ti-e starea emoțională azi?
✓ Nivelul tău de energie?
✓ Ce te-ar face mai bine?

Datele tale ajută IA să te înțeleagă mai bine și să-ți ofere suport personalizat.

=== Check-in acum ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/ro/chat

Îngrijire de sine,
Doisense"""
    else:
        subject = "💚 Today's check-in - How are you feeling?"
        body = f"""Hi {user.first_name or 'there'}!

Your emotional state matters. Take 1 minute for today's check-in:
✓ What's your mood today?
✓ Your energy level?
✓ What would help you feel better?

Your data helps our AI understand you better and offer personalized support.

=== Check in now ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/{language}/chat

Self-care,
Doisense"""

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_upgrade_recommendation(user, reason: str) -> None:
    """Send targeted upgrade email based on user behavior."""
    language = (user.language or "en").lower()
    
    if reason == "journal_limit":
        if language.startswith("ro"):
            subject = "📊 Răspunde la mai multe întrebări cu PREMIUM"
            body = f"""Salut {user.first_name or 'there'}!

Ți-au plăcut întrebările din jurnal? PREMIUM te lasă să accesezi catalog complet:
✓ 50+ întrebări de reflecție
✓ Integrare cu AI coach
✓ Rapoarte de progres
✓ Analize emoționale

Upgrade azi și accelerează dezvoltarea ta.

=== Upgrade acum ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/ro/pricing"""
        else:
            subject = "📊 Answer more questions with PREMIUM"
            body = f"""Hi {user.first_name or 'there'}!

Enjoyed your journal prompts? PREMIUM unlocks:
✓ 50+ reflection questions
✓ AI coach integration
✓ Progress reports
✓ Emotional insights

Upgrade today and accelerate your growth.

=== Upgrade now ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/{language}/pricing"""
    
    elif reason == "report_limit":
        if language.startswith("ro"):
            subject = "📈 Vezi rapoarte detaliate cu PREMIUM"
            body = f"""Salut {user.first_name or 'there'}!

În urma conversațiilor tale, putem genera rapoarte detaliate.
Cu PREMIUM accesezi: 
✓ Rapoarte zilnice
✓ Analize săptămânale
✓ Pattern-uri comportamentale
✓ Recomandări bazate pe AI

Upgrade azi și obții insight-uri profunde.

=== Upgrade acum ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/ro/pricing"""
        else:
            subject = "📈 Unlock detailed reports with PREMIUM"
            body = f"""Hi {user.first_name or 'there'}!

Based on your conversations, we can generate detailed insights.
With PREMIUM unlock:
✓ Daily reports
✓ Weekly analysis
✓ Behavioral patterns
✓ AI-powered recommendations

Upgrade today and get deep insights.

=== Upgrade now ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/{language}/pricing"""
    
    else:
        # Generic upgrade
        if language.startswith("ro"):
            subject = "⭐ Explorez capacități nelimitate cu PREMIUM"
            body = f"""Salut {user.first_name or 'there'}!

Poți accesa mai mult pe PREMIUM:
✓ Chat AI nelimitat
✓ Rapoarte detaliate
✓ Planuri personalizate
✓ Prioritate în suport

Alege PREMIUM și maximizează beneficiile.

=== Upgrade acum ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/ro/pricing"""
        else:
            subject = "⭐ Unlock unlimited capabilities with PREMIUM"
            body = f"""Hi {user.first_name or 'there'}!

Access more with PREMIUM:
✓ Unlimited AI chat
✓ Detailed reports
✓ Personalized plans
✓ Priority support

Choose PREMIUM and maximize your benefits.

=== Upgrade now ===
{getattr(settings, 'FRONTEND_BASE_URL', 'https://projects.doimih.net/doisense')}/{language}/pricing"""

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()


def send_goal_reminder(user, goals: list[str], days_since_focus: int) -> None:
    """Send a goal-focused reminder using goals inferred from the user profile."""
    language = (user.language or "en").lower()
    visible_goals = [goal.strip() for goal in goals if goal and goal.strip()][:3]
    goal_lines = "\n".join(f"- {goal}" for goal in visible_goals)
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")

    if language.startswith("ro"):
        subject = "🎯 Revino la obiectivele tale cu un pas mic azi"
        body = f"""Salut {user.first_name or 'there'}!

Ai setat câteva direcții importante pentru tine și nu ai mai revenit la ele de {days_since_focus} zile.

Obiectivele tale active acum:
{goal_lines}

Un check-in scurt azi te poate ajuta să recapeți ritmul:
✓ clarifici ce contează azi
✓ notezi un pas mic realist
✓ păstrezi continuitatea fără presiune

=== Revino la focus ===
{frontend_base}/ro/chat?module=coaching

Cu răbdare,
Doisense"""
    else:
        subject = "🎯 Reconnect with your goals through one small step today"
        body = f"""Hi {user.first_name or 'there'}!

You set a few meaningful goals for yourself and you haven't revisited them in {days_since_focus} days.

Your active focus areas right now:
{goal_lines}

A short check-in today can help you regain momentum:
✓ clarify what matters today
✓ choose one realistic next step
✓ keep continuity without pressure

=== Refocus now ===
{frontend_base}/{language}/chat?module=coaching

Warmly,
Doisense"""

    connection = _get_mail_connection()
    message = EmailMessage(
        subject=subject,
        body=body,
        from_email=_get_from_email(),
        to=[user.email],
        connection=connection,
    )
    message.send()

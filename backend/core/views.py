from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.db import connections
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timezone as dt_timezone
from datetime import timedelta
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from pathlib import Path
import imghdr
import re
import json
import smtplib
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.core.mail import EmailMessage, get_connection
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from journal.models import JournalQuestion
from programs.models import GuidedProgram
from core.analytics import track_event

from .image_utils import convert_uploaded_image_to_webp
from .models import (
    AnalyticsEvent,
    BackupRestoreRequest,
    BackupVerificationLog,
    CMSPage,
    InAppNotification,
    SupportTicketMessage,
    SystemErrorEvent,
    SystemConfig,
    SupportTicket,
    UserNotificationPreference,
    UserWellbeingCheckin,
)
from .serializers import AnalyticsTrackSerializer, CMSPageSerializer, WellbeingCheckinCreateSerializer


def public_cache_response(data, *, max_age: int = 300):
    response = Response(data)
    response["Cache-Control"] = f"public, max-age={max_age}, stale-while-revalidate={max_age * 2}"
    return response


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        db_ok = True
        cache_ok = True

        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:
            db_ok = False

        try:
            cache.set("healthcheck:ping", "ok", timeout=5)
            cache_ok = cache.get("healthcheck:ping") == "ok"
        except Exception:
            cache_ok = False

        status_code = status.HTTP_200_OK if db_ok and cache_ok else status.HTTP_503_SERVICE_UNAVAILABLE
        if status_code != status.HTTP_200_OK:
            SystemErrorEvent.objects.create(
                severity=SystemErrorEvent.SEVERITY_HIGH,
                component="healthcheck",
                endpoint="/api/health",
                http_method="GET",
                status_code=status_code,
                error_type="HealthDegraded",
                message="Healthcheck returned degraded status.",
                context={"database_ok": db_ok, "cache_ok": cache_ok},
            )
        return Response(
            {
                "status": "ok" if status_code == status.HTTP_200_OK else "degraded",
                "checks": {
                    "database": "ok" if db_ok else "error",
                    "cache": "ok" if cache_ok else "error",
                },
            },
            status=status_code,
        )


class CMSPageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        serializer = CMSPageSerializer(CMSPage.objects.all(), many=True)
        return Response(serializer.data)


class CMSPageDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slug):
        if not request.user.is_superuser:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        language = (request.query_params.get("language") or "ro").strip().lower()
        if language not in settings.SUPPORTED_LANGUAGES:
            language = "ro"

        page = CMSPage.objects.filter(slug=slug, language=language).first()
        if not page:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(CMSPageSerializer(page).data)

    def put(self, request, slug):
        if not request.user.is_superuser:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        language = (request.data.get("language") or "ro").strip().lower()
        if language not in settings.SUPPORTED_LANGUAGES:
            language = "ro"

        page = CMSPage.objects.filter(slug=slug, language=language).first()
        payload = {
            "slug": slug,
            "title": request.data.get("title") or slug.replace("-", " ").title(),
            "language": language,
            "content": request.data.get("content", ""),
            "is_published": bool(request.data.get("is_published", True)),
            "show_in_header": bool(request.data.get("show_in_header", False)),
            "show_in_footer": bool(request.data.get("show_in_footer", False)),
            "menu_order": int(request.data.get("menu_order", 100)),
        }

        if page:
            serializer = CMSPageSerializer(page, data=payload, partial=True)
        else:
            serializer = CMSPageSerializer(data=payload)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CMSPublicPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        language = (request.query_params.get("language") or "ro").strip()
        if language not in settings.SUPPORTED_LANGUAGES:
            language = "ro"

        page = CMSPage.objects.filter(
            slug=slug,
            language=language,
            is_published=True,
        ).first()
        if not page and language != "en":
            page = CMSPage.objects.filter(
                slug=slug,
                language="en",
                is_published=True,
            ).first()
        if not page and language != "ro":
            page = CMSPage.objects.filter(
                slug=slug,
                language="ro",
                is_published=True,
            ).first()
        if not page:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        return public_cache_response(CMSPageSerializer(page).data, max_age=300)


class CMSPublicPreviewPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        language = (request.query_params.get("language") or "ro").strip().lower()
        if language not in settings.SUPPORTED_LANGUAGES:
            language = "ro"

        page = CMSPage.objects.filter(slug=slug, language=language, is_published=True).first()
        if not page and language != "en":
            page = CMSPage.objects.filter(slug=slug, language="en", is_published=True).first()
        if not page:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        return render(
            request,
            "cms/public_preview.html",
            {
                "page": page,
            },
        )


class CMSMenuLinksView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        language = (request.query_params.get("language") or "ro").strip()
        pages = CMSPage.objects.filter(is_published=True, language=language).order_by("menu_order", "slug")

        header = [
            {"slug": p.slug, "title": p.title, "path": f"/cms/{p.slug}"}
            for p in pages
            if p.show_in_header
        ]
        footer = [
            {"slug": p.slug, "title": p.title, "path": f"/cms/{p.slug}"}
            for p in pages
            if p.show_in_footer
        ]

        return public_cache_response({"header": header, "footer": footer}, max_age=300)


class GeoLanguageView(APIView):
    permission_classes = [AllowAny]

    COUNTRY_LANGUAGE_MAP = {
        "RO": "ro",
        "MD": "ro",
        "DE": "de",
        "AT": "de",
        "CH": "de",
        "FR": "fr",
        "IT": "it",
        "ES": "es",
        "MX": "es",
        "AR": "es",
        "CO": "es",
        "PL": "pl",
    }

    def get(self, request):
        country = self._get_country(request)
        language = self.COUNTRY_LANGUAGE_MAP.get(country, "en")

        if language not in settings.SUPPORTED_LANGUAGES:
            language = "en"

        return public_cache_response({"country": country, "language": language}, max_age=3600)

    def _get_country(self, request):
        header_country = (
            request.META.get("HTTP_CF_IPCOUNTRY")
            or request.META.get("HTTP_X_COUNTRY_CODE")
            or request.META.get("HTTP_X_APPENGINE_COUNTRY")
            or ""
        ).strip().upper()
        if len(header_country) == 2:
            return header_country

        ip = self._get_client_ip(request)
        if not ip:
            return ""

        try:
            req = Request(
                f"https://ipapi.co/{ip}/json/",
                headers={"User-Agent": "Doisense/1.0"},
            )
            with urlopen(req, timeout=2.0) as response:
                payload = json.loads(response.read().decode("utf-8"))
            country = str(payload.get("country_code") or "").strip().upper()
            if len(country) == 2:
                return country
        except Exception:
            return ""

        return ""

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return (request.META.get("REMOTE_ADDR") or "").strip()


class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        language = request.query_params.get("language") or "en"
        if language not in settings.SUPPORTED_LANGUAGES:
            language = "en"

        if len(query) < 2:
            return Response(
                {
                    "query": query,
                    "results": {
                        "programs": [],
                        "journal_questions": [],
                        "cms_pages": [],
                    },
                }
            )

        user = request.user if request.user and request.user.is_authenticated else None

        programs_qs = GuidedProgram.objects.filter(
            active=True,
            language=language,
        ).filter(Q(title__icontains=query) | Q(description__icontains=query))
        if not user or not user.has_paid_access():
            programs_qs = programs_qs.filter(is_premium=False)

        programs = [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "path": f"/programs/{p.id}",
                "is_premium": p.is_premium,
            }
            for p in programs_qs[:20]
        ]

        questions_qs = JournalQuestion.objects.filter(
            active=True,
            language=language,
        ).filter(Q(text__icontains=query) | Q(category__icontains=query))

        journal_questions = [
            {
                "id": q.id,
                "text": q.text,
                "category": q.category,
                "path": "/journal",
            }
            for q in questions_qs[:20]
        ]

        cms_qs = CMSPage.objects.filter(is_published=True, language=language).filter(
            Q(title__icontains=query) | Q(content__icontains=query) | Q(slug__icontains=query)
        )
        cms_pages = [
            {
                "slug": p.slug,
                "title": p.title,
                "path": f"/cms/{p.slug}",
            }
            for p in cms_qs[:20]
        ]

        return Response(
            {
                "query": query,
                "results": {
                    "programs": programs,
                    "journal_questions": journal_questions,
                    "cms_pages": cms_pages,
                },
            }
        )


class AnalyticsTrackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AnalyticsTrackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event_name = serializer.validated_data["event_name"]
        source = serializer.validated_data.get("source", "frontend")
        session_id = serializer.validated_data.get("session_id", "")
        properties = serializer.validated_data.get("properties") or {}

        user = request.user if request.user and request.user.is_authenticated else None
        track_event(
            event_name,
            source=source,
            user=user,
            session_id=session_id,
            properties=properties,
        )

        return Response({"tracked": True}, status=status.HTTP_201_CREATED)


class WellbeingCheckinView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WellbeingCheckinCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        checkin = serializer.save(user=request.user)
        return Response(
            {
                "id": checkin.id,
                "mood": checkin.mood,
                "energy_level": checkin.energy_level,
                "created_at": checkin.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class WellbeingSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        effective_tier = user.effective_plan_tier()
        if effective_tier in ("vip", "premium", "trial"):
            plan_days = 30
        elif effective_tier == "basic":
            plan_days = 14
        else:
            plan_days = 7

        checkins = UserWellbeingCheckin.objects.filter(user=user)
        mood_items = list(
            checkins.exclude(mood="")
            .order_by("created_at")
            .values("created_at", "mood")[:180]
        )
        energy_items = list(
            checkins.filter(energy_level__isnull=False)
            .order_by("created_at")
            .values("created_at", "energy_level")[:180]
        )

        latest_mood = (
            checkins.exclude(mood="").order_by("-created_at").values_list("mood", flat=True).first()
            or "ok"
        )
        latest_energy = (
            checkins.filter(energy_level__isnull=False)
            .order_by("-created_at")
            .values_list("energy_level", flat=True)
            .first()
        )
        if latest_energy is None:
            latest_energy = 3

        if not mood_items:
            mood_items = [{"created_at": user.created_at, "mood": latest_mood}]
        if not energy_items:
            energy_items = [{"created_at": user.created_at, "energy_level": latest_energy}]

        activity_dates = set(
            d.date() if hasattr(d, "date") else d
            for d in checkins.dates("created_at", "day")
        )
        activity_dates.update(
            d.date() if hasattr(d, "date") else d
            for d in user.journal_entries.dates("created_at", "day")
        )

        streak_days = 0
        day_cursor = timezone.localdate()
        while day_cursor in activity_dates:
            streak_days += 1
            day_cursor -= timedelta(days=1)

        return Response(
            {
                "plan": effective_tier,
                "plan_days": plan_days,
                "streak_days": streak_days,
                "current_mood": latest_mood,
                "current_energy": latest_energy,
                "mood_history": [
                    {
                        "at": item["created_at"],
                        "mood": item["mood"],
                    }
                    for item in mood_items
                ],
                "energy_history": [
                    {
                        "at": item["created_at"],
                        "energy_level": item["energy_level"],
                    }
                    for item in energy_items
                ],
            }
        )


class InAppNotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        limit_raw = request.query_params.get("limit", "50")
        try:
            limit = max(1, min(int(limit_raw), 100))
        except ValueError:
            limit = 50

        rows = InAppNotification.objects.filter(user=request.user).order_by("-created_at")[:limit]
        unread = InAppNotification.objects.filter(user=request.user, is_read=False).count()

        return Response(
            {
                "unread_count": unread,
                "items": [
                    {
                        "id": row.id,
                        "notification_type": row.notification_type,
                        "title": row.title,
                        "body": row.body,
                        "context_key": row.context_key,
                        "is_read": row.is_read,
                        "read_at": row.read_at,
                        "created_at": row.created_at,
                    }
                    for row in rows
                ],
            }
        )


class InAppNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id):
        row = InAppNotification.objects.filter(id=notification_id, user=request.user).first()
        if not row:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if not row.is_read:
            row.is_read = True
            row.read_at = timezone.now()
            row.save(update_fields=["is_read", "read_at"])

        return Response({"ok": True})


class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prefs, _ = UserNotificationPreference.objects.get_or_create(user=request.user)
        return Response({"push_enabled": prefs.push_enabled})

    def post(self, request):
        push_enabled = bool(request.data.get("push_enabled", False))
        prefs, _ = UserNotificationPreference.objects.get_or_create(user=request.user)
        prefs.push_enabled = push_enabled
        prefs.save(update_fields=["push_enabled", "updated_at"])
        return Response({"push_enabled": prefs.push_enabled})


class SupportTicketListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _serialize_message(row: SupportTicketMessage):
        return {
            "id": row.id,
            "sender_role": row.sender_role,
            "author_id": row.author_id,
            "author_email": getattr(row.author, "email", "") if row.author_id else "",
            "message": row.message,
            "is_internal": row.is_internal,
            "created_at": row.created_at,
        }

    @classmethod
    def _serialize_ticket(cls, row: SupportTicket, *, include_messages: bool = False, include_internal: bool = False):
        payload = {
            "id": row.id,
            "user_id": row.user_id,
            "user_email": getattr(row.user, "email", ""),
            "subject": row.subject,
            "message": row.message,
            "priority": row.priority,
            "status": row.status,
            "assigned_to_id": row.assigned_to_id,
            "assigned_to_email": getattr(row.assigned_to, "email", "") if row.assigned_to_id else "",
            "first_response_due_at": row.first_response_due_at,
            "resolution_due_at": row.resolution_due_at,
            "first_responded_at": row.first_responded_at,
            "resolved_at": row.resolved_at,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
        if include_messages:
            qs = row.messages.select_related("author").order_by("created_at")
            if not include_internal:
                qs = qs.filter(is_internal=False)
            payload["messages"] = [cls._serialize_message(item) for item in qs]
        return payload

    def get(self, request):
        tickets = SupportTicket.objects.filter(user=request.user).select_related("user", "assigned_to").order_by("-created_at")[:100]
        return Response(
            {
                "items": [self._serialize_ticket(row) for row in tickets]
            }
        )

    def post(self, request):
        subject = str(request.data.get("subject") or "").strip()
        message = str(request.data.get("message") or "").strip()

        if not subject:
            return Response({"detail": "subject is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not message:
            return Response({"detail": "message is required."}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        ticket = SupportTicket.objects.create(
            user=request.user,
            subject=subject[:180],
            message=message,
            first_response_due_at=now + timedelta(hours=4),
            resolution_due_at=now + timedelta(hours=48),
        )
        SupportTicketMessage.objects.create(
            ticket=ticket,
            author=request.user,
            sender_role=SupportTicketMessage.SENDER_USER,
            message=message,
            is_internal=False,
        )
        track_event(
            "support_ticket_created",
            source="backend",
            user=request.user,
            properties={},
        )
        return Response(self._serialize_ticket(ticket, include_messages=True), status=status.HTTP_201_CREATED)


class SupportTicketDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _is_staff_user(user) -> bool:
        return bool(getattr(user, "is_staff", False) or getattr(user, "is_superuser", False))

    def _get_ticket_for_request(self, request, ticket_id: int) -> SupportTicket | None:
        qs = SupportTicket.objects.select_related("user", "assigned_to")
        if self._is_staff_user(request.user):
            return qs.filter(id=ticket_id).first()
        return qs.filter(id=ticket_id, user=request.user).first()

    def get(self, request, ticket_id: int):
        ticket = self._get_ticket_for_request(request, ticket_id)
        if not ticket:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        include_internal = self._is_staff_user(request.user)
        return Response(SupportTicketListCreateView._serialize_ticket(ticket, include_messages=True, include_internal=include_internal))

    def post(self, request, ticket_id: int):
        ticket = self._get_ticket_for_request(request, ticket_id)
        if not ticket:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        message = str(request.data.get("message") or "").strip()
        if not message:
            return Response({"detail": "message is required."}, status=status.HTTP_400_BAD_REQUEST)

        is_staff = self._is_staff_user(request.user)
        is_internal = bool(request.data.get("is_internal", False)) if is_staff else False
        sender_role = SupportTicketMessage.SENDER_ADMIN if is_staff else SupportTicketMessage.SENDER_USER

        reply = SupportTicketMessage.objects.create(
            ticket=ticket,
            author=request.user,
            sender_role=sender_role,
            message=message[:4000],
            is_internal=is_internal,
        )

        now = timezone.now()
        if is_staff:
            new_status = str(request.data.get("status") or "").strip()
            if new_status in {choice[0] for choice in SupportTicket.STATUS_CHOICES}:
                ticket.status = new_status

            new_priority = str(request.data.get("priority") or "").strip()
            if new_priority in {choice[0] for choice in SupportTicket.PRIORITY_CHOICES}:
                ticket.priority = new_priority

            if ticket.assigned_to_id is None:
                ticket.assigned_to = request.user

            if not is_internal and ticket.first_responded_at is None:
                ticket.first_responded_at = now

            if ticket.status == SupportTicket.STATUS_RESOLVED:
                if ticket.resolved_at is None:
                    ticket.resolved_at = now
            else:
                ticket.resolved_at = None

            ticket.save()

            if not is_internal:
                InAppNotification.objects.create(
                    user=ticket.user,
                    notification_type="support_ticket_reply",
                    title=f"Support ticket #{ticket.id} updated",
                    body=message[:180],
                    context_key=str(ticket.id),
                )
                track_event(
                    "support_ticket_updated",
                    source="backend",
                    user=ticket.user,
                    properties={"ticket_id": ticket.id, "status": ticket.status},
                )
        else:
            if ticket.status == SupportTicket.STATUS_RESOLVED:
                ticket.status = SupportTicket.STATUS_IN_PROGRESS
                ticket.resolved_at = None
                ticket.save()

        include_internal = is_staff
        return Response(
            {
                "ok": True,
                "reply": SupportTicketListCreateView._serialize_message(reply),
                "ticket": SupportTicketListCreateView._serialize_ticket(ticket, include_messages=True, include_internal=include_internal),
            },
            status=status.HTTP_201_CREATED,
        )


class SupportTicketAdminListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        status_filter = str(request.query_params.get("status") or "").strip()
        qs = SupportTicket.objects.select_related("user", "assigned_to").order_by("-updated_at")
        if status_filter in {choice[0] for choice in SupportTicket.STATUS_CHOICES}:
            qs = qs.filter(status=status_filter)

        items = [
            SupportTicketListCreateView._serialize_ticket(row)
            for row in qs[:200]
        ]
        return Response({"items": items})


class BackupRestoreRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        rows = BackupRestoreRequest.objects.order_by("-created_at")[:50]
        return Response(
            {
                "items": [
                    {
                        "id": row.id,
                        "status": row.status,
                        "restore_point": row.restore_point,
                        "reason": row.reason,
                        "requested_by": row.requested_by_id,
                        "approved_by": row.approved_by_id,
                        "created_at": row.created_at,
                        "updated_at": row.updated_at,
                    }
                    for row in rows
                ]
            }
        )

    def post(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        restore_point = str(request.data.get("restore_point") or "").strip()
        reason = str(request.data.get("reason") or "").strip()
        confirmation = str(request.data.get("confirmation") or "").strip()

        if not restore_point:
            return Response({"detail": "restore_point is required."}, status=status.HTTP_400_BAD_REQUEST)
        if confirmation != "CONFIRM_RESTORE":
            return Response(
                {"detail": "Invalid confirmation token. Use CONFIRM_RESTORE."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        row = BackupRestoreRequest.objects.create(
            requested_by=request.user,
            restore_point=restore_point,
            reason=reason,
            confirmation_token=confirmation,
        )
        track_event(
            "backup_restore_requested",
            source="backend",
            user=request.user,
            properties={"restore_point": restore_point},
        )
        return Response(
            {
                "id": row.id,
                "status": row.status,
                "restore_point": row.restore_point,
                "created_at": row.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class AnalyticsFunnelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        now = timezone.now()
        start = now - timedelta(days=30)
        counts = {
            "onboarding_started": AnalyticsEvent.objects.filter(event_name="onboarding_started", created_at__gte=start).count(),
            "onboarding_completed": AnalyticsEvent.objects.filter(event_name="onboarding_completed", created_at__gte=start).count(),
            "checkout_initiated": AnalyticsEvent.objects.filter(event_name="checkout_initiated", created_at__gte=start).count(),
            "subscription_change_requested": AnalyticsEvent.objects.filter(
                event_name="subscription_change_requested", created_at__gte=start
            ).count(),
            "program_completed": AnalyticsEvent.objects.filter(event_name="program_completed", created_at__gte=start).count(),
        }
        return Response({"period_days": 30, "funnel": counts})


class AnalyticsCohortRetentionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        today = timezone.localdate()
        start_date = today - timedelta(days=30)
        cohort_rows = (
            AnalyticsEvent.objects.filter(event_name="onboarding_completed", created_at__date__gte=start_date)
            .values("created_at__date")
            .annotate(total=Count("id"))
            .order_by("created_at__date")
        )

        active_after_7d = AnalyticsEvent.objects.filter(
            event_name="chat_message_sent",
            created_at__date__gte=today - timedelta(days=23),
        ).count()

        return Response(
            {
                "cohorts": [
                    {"cohort_date": row["created_at__date"], "users": row["total"]}
                    for row in cohort_rows
                ],
                "retention_proxy": {
                    "window_days": 7,
                    "active_events": active_after_7d,
                },
            }
        )


class OperationalAlertsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        since = timezone.now() - timedelta(hours=24)
        scheduler_failures = SystemErrorEvent.objects.filter(
            component="scheduler",
            severity__in=[SystemErrorEvent.SEVERITY_HIGH, SystemErrorEvent.SEVERITY_CRITICAL],
            created_at__gte=since,
        ).count()
        health_degraded = SystemErrorEvent.objects.filter(
            component="healthcheck",
            created_at__gte=since,
        ).count()
        backup_failures = BackupVerificationLog.objects.filter(
            status=BackupVerificationLog.STATUS_FAILED,
            created_at__gte=since,
        ).count()

        return Response(
            {
                "window_hours": 24,
                "alerts": {
                    "scheduler_failures": scheduler_failures,
                    "health_degraded": health_degraded,
                    "backup_verification_failed": backup_failures,
                },
            }
        )


class SettingsImageLibraryView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
    ALLOWED_TYPES = {"jpeg", "png", "webp", "gif"}
    MAX_UPLOAD_SIZE = 8 * 1024 * 1024
    FOLDER = "settings-images"

    def get(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        folder = Path(settings.MEDIA_ROOT) / self.FOLDER
        folder.mkdir(parents=True, exist_ok=True)

        images = []
        for item in sorted(folder.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True):
            if not item.is_file():
                continue
            extension = item.suffix.lstrip(".").lower()
            if extension not in self.ALLOWED_EXTENSIONS:
                continue

            stat = item.stat()
            images.append(
                {
                    "name": item.name,
                    "url": f"{settings.MEDIA_URL}{self.FOLDER}/{item.name}",
                    "size": stat.st_size,
                    "updated_at": timezone.datetime.fromtimestamp(stat.st_mtime, tz=dt_timezone.utc),
                }
            )

        return Response({"items": images})

    def post(self, request):
        if not request.user.is_superuser:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        upload = request.FILES.get("image")
        if not upload:
            return Response({"detail": "Missing image file."}, status=status.HTTP_400_BAD_REQUEST)

        if upload.size > self.MAX_UPLOAD_SIZE:
            return Response({"detail": "File too large. Max allowed is 8MB."}, status=status.HTTP_400_BAD_REQUEST)

        image_type = imghdr.what(upload)
        if image_type not in self.ALLOWED_TYPES:
            return Response(
                {"detail": "Unsupported image format. Allowed: jpg, png, webp, gif."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        upload.seek(0)
        try:
            webp_file, stem = convert_uploaded_image_to_webp(upload)
        except ValueError:
            return Response({"detail": "Failed to process image."}, status=status.HTTP_400_BAD_REQUEST)

        path = default_storage.save(
            f"{self.FOLDER}/{stem}.webp",
            webp_file,
        )
        filename = Path(path).name

        return Response(
            {
                "name": filename,
                "url": f"{settings.MEDIA_URL}{self.FOLDER}/{filename}",
            },
            status=status.HTTP_201_CREATED,
        )


class ContactConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        config = SystemConfig.get_solo()
        return public_cache_response(
            {
                "recaptcha_enabled": bool(config.recaptcha_enabled and config.recaptcha_site_key),
                "recaptcha_site_key": config.recaptcha_site_key or "",
            },
            max_age=300,
        )


class ContactSubmitView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        full_name = str(request.data.get("full_name") or "").strip()
        email = str(request.data.get("email") or "").strip().lower()
        subject = str(request.data.get("subject") or "").strip()
        message = str(request.data.get("message") or "").strip()
        recaptcha_token = str(request.data.get("recaptcha_token") or "").strip()

        if not full_name:
            return Response({"detail": "Full name is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not subject:
            return Response({"detail": "Subject is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not message:
            return Response({"detail": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_email(email)
        except ValidationError:
            return Response({"detail": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)

        config = SystemConfig.get_solo()
        if config.recaptcha_enabled:
            if not config.recaptcha_secret_key:
                return Response(
                    {"detail": "reCAPTCHA is enabled but not configured on server."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            if not recaptcha_token:
                return Response({"detail": "reCAPTCHA token is required."}, status=status.HTTP_400_BAD_REQUEST)

            ok, score = self._verify_recaptcha(config.recaptcha_secret_key, recaptcha_token)
            min_score = float(config.recaptcha_min_score or 0.5)
            if not ok or score < min_score:
                return Response(
                    {"detail": "reCAPTCHA verification failed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        target_email = config.contact_notification_email or ""
        if not target_email:
            return Response(
                {"detail": "Contact destination email is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        from_email = (
            config.contact_from_email
            or config.email_host_user
            or getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@doisense.eu")
        )

        body = (
            f"New contact form submission\n\n"
            f"Name: {full_name}\n"
            f"Email: {email}\n"
            f"Subject: {subject}\n\n"
            f"Message:\n{message}\n"
        )

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
            EmailMessage(
                subject=f"[Contact] {subject}",
                body=body,
                from_email=from_email,
                to=[target_email],
                reply_to=[email],
                connection=connection,
            ).send()
        except smtplib.SMTPException:
            return Response(
                {"detail": "Unable to send message right now. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception:
            return Response(
                {"detail": "Unable to send message right now. Please try again later."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"detail": "Message sent successfully."}, status=status.HTTP_200_OK)

    def _verify_recaptcha(self, secret_key: str, token: str) -> tuple[bool, float]:
        payload = urlencode({"secret": secret_key, "response": token}).encode("utf-8")
        request = Request(
            "https://www.google.com/recaptcha/api/siteverify",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        try:
            with urlopen(request, timeout=4.0) as response:
                data = json.loads(response.read().decode("utf-8"))
        except Exception:
            return False, 0.0

        success = bool(data.get("success"))
        score = float(data.get("score") or 0.0)
        return success, score

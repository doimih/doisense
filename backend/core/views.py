from django.conf import settings
from django.db.models import Q
from urllib.request import urlopen, Request
import json
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from journal.models import JournalQuestion
from programs.models import GuidedProgram

from .models import CMSPage
from .serializers import CMSPageSerializer


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

        return Response(CMSPageSerializer(page).data)


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

        return Response({"header": header, "footer": footer})


class GeoLanguageView(APIView):
    permission_classes = [AllowAny]

    COUNTRY_LANGUAGE_MAP = {
        "RO": "ro",
        "MD": "ro",
        "DE": "de",
        "AT": "de",
        "CH": "de",
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

        return Response({"country": country, "language": language})

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
        if not user or not user.is_premium:
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

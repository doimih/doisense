from django.conf import settings
from django.db.models import Q
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
        page = CMSPage.objects.filter(slug=slug).first()
        if not page:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(CMSPageSerializer(page).data)

    def put(self, request, slug):
        if not request.user.is_superuser:
            return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        page = CMSPage.objects.filter(slug=slug).first()
        payload = {
            "slug": slug,
            "title": request.data.get("title") or slug.replace("-", " ").title(),
            "content": request.data.get("content", ""),
            "is_published": bool(request.data.get("is_published", True)),
        }

        if page:
            serializer = CMSPageSerializer(page, data=payload, partial=True)
        else:
            serializer = CMSPageSerializer(data=payload)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


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

        cms_qs = CMSPage.objects.filter(is_published=True).filter(
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

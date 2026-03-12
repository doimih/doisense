from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.analytics import track_event
from core.feature_access import require_feature
from core.quota import check_and_consume

from .models import JournalQuestion, JournalEntry
from .serializers import JournalQuestionSerializer, JournalEntrySerializer


MIN_JOURNAL_QUESTIONS = 12
DEFAULT_RO_QUESTIONS = [
    {
        "text": "Ce emotie a fost cea mai prezenta azi si ce anume a declansat-o?",
        "category": "emotion",
        "tags": ["emotii", "constientizare"],
    },
    {
        "text": "Ce situatie te-a consumat cel mai mult astazi si de ce?",
        "category": "reflection",
        "tags": ["claritate", "evenimente"],
    },
    {
        "text": "Ce ai facut bine astazi, chiar daca pare un lucru mic?",
        "category": "gratitude",
        "tags": ["progres", "recunostinta"],
    },
    {
        "text": "Care a fost cel mai dificil gand de azi si cum l-ai putea reformula mai bland?",
        "category": "mindset",
        "tags": ["ganduri", "auto-compasiune"],
    },
    {
        "text": "Ce ai invatat despre tine in urma unei reactii avute azi?",
        "category": "self-awareness",
        "tags": ["autocunoastere", "reactii"],
    },
    {
        "text": "Ce ai amanat astazi si ce te-a blocat concret?",
        "category": "productivity",
        "tags": ["amanare", "blocaje"],
    },
    {
        "text": "Ce ai nevoie maine pentru a te simti mai echilibrat?",
        "category": "planning",
        "tags": ["planificare", "echilibru"],
    },
    {
        "text": "Cum ai avut grija de corpul tau astazi (somn, masa, miscare)?",
        "category": "wellbeing",
        "tags": ["sanatate", "rutina"],
    },
    {
        "text": "Ce conversatie ti-a ramas in minte si ce mesaj a avut pentru tine?",
        "category": "relationships",
        "tags": ["relatii", "comunicare"],
    },
    {
        "text": "Ce limita personala ai respectat sau ai fi vrut sa respecti azi?",
        "category": "boundaries",
        "tags": ["limite", "respect de sine"],
    },
    {
        "text": "Ce gand te-a ajutat astazi sa mergi mai departe?",
        "category": "mindset",
        "tags": ["resurse", "rezilienta"],
    },
    {
        "text": "Pentru ce esti recunoscator in aceasta seara, in mod sincer?",
        "category": "gratitude",
        "tags": ["recunostinta", "seara"],
    },
]


def _ensure_minimum_questions(language: str) -> None:
    if language != "ro":
        return

    current_count = JournalQuestion.objects.filter(active=True, language=language).count()
    if current_count >= MIN_JOURNAL_QUESTIONS:
        return

    existing_texts = set(
        JournalQuestion.objects.filter(language=language).values_list("text", flat=True)
    )
    for item in DEFAULT_RO_QUESTIONS:
        if item["text"] in existing_texts:
            continue
        JournalQuestion.objects.create(
            text=item["text"],
            category=item["category"],
            language=language,
            tags=item["tags"],
            active=True,
        )
        existing_texts.add(item["text"])


class JournalQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("journal_access")
    def get(self, request):
        language = request.query_params.get("language") or request.user.language or "en"
        if language not in settings.SUPPORTED_LANGUAGES:
            language = "en"

        _ensure_minimum_questions(language)
        qs = JournalQuestion.objects.filter(active=True, language=language)
        serializer = JournalQuestionSerializer(qs, many=True)
        return Response(serializer.data)


class JournalEntriesView(APIView):
    permission_classes = [IsAuthenticated]

    @require_feature("journal_access")
    def post(self, request):
        allowed, remaining, limit = check_and_consume(request.user, "journal_entries", amount=1)
        if not allowed:
            base_url = getattr(settings, "FRONTEND_BASE_URL", "https://projects.doimih.net/doisense")
            language = request.user.language or "en"
            return Response(
                {
                    "detail": "Monthly journal quota exceeded for your tier.",
                    "code": "quota_exceeded",
                    "metric": "journal_entries",
                    "limit": limit,
                    "remaining": remaining,
                    "cta_url": f"{base_url}/{language}/pricing",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = JournalEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        track_event(
            "journal_entry_created",
            source="backend",
            user=request.user,
            properties={"question_id": serializer.data.get("question")},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

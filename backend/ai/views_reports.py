from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DailyReport, MonthlyReport, WeeklyReport


def _allowed_report_types_for_user(user) -> set[str]:
    tier = user.effective_plan_tier()
    if tier in {"vip"}:
        return {"daily", "weekly", "monthly"}
    if tier in {"premium", "trial"}:
        return {"daily", "weekly"}
    return set()


class ReportListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        report_type = str(request.query_params.get("type") or "daily").strip().lower()
        limit_raw = request.query_params.get("limit", "20")
        try:
            limit = max(1, min(int(limit_raw), 100))
        except ValueError:
            limit = 20

        allowed = _allowed_report_types_for_user(request.user)
        if report_type not in {"daily", "weekly", "monthly"}:
            return Response({"detail": "Invalid report type."}, status=status.HTTP_400_BAD_REQUEST)
        if report_type not in allowed:
            return Response({"detail": "This report type is not available for your plan."}, status=status.HTTP_403_FORBIDDEN)

        if report_type == "daily":
            rows = DailyReport.objects.filter(user=request.user).order_by("-date")[:limit]
            items = [
                {
                    "type": "daily",
                    "id": row.id,
                    "date": row.date,
                    "summary": row.summary,
                    "highlights": row.highlights,
                    "challenges": row.challenges,
                    "recommendations": row.recommendations,
                    "updated_at": row.updated_at,
                }
                for row in rows
            ]
        elif report_type == "weekly":
            rows = WeeklyReport.objects.filter(user=request.user).order_by("-week_start")[:limit]
            items = [
                {
                    "type": "weekly",
                    "id": row.id,
                    "week_start": row.week_start,
                    "summary": row.summary,
                    "trends": row.trends,
                    "progress": row.progress,
                    "recommendations": row.recommendations,
                    "updated_at": row.updated_at,
                }
                for row in rows
            ]
        else:
            rows = MonthlyReport.objects.filter(user=request.user).order_by("-year", "-month")[:limit]
            items = [
                {
                    "type": "monthly",
                    "id": row.id,
                    "year": row.year,
                    "month": row.month,
                    "summary": row.summary,
                    "trends": row.trends,
                    "insights": row.insights,
                    "recommendations": row.recommendations,
                    "updated_at": row.updated_at,
                }
                for row in rows
            ]

        return Response({"type": report_type, "items": items}, status=status.HTTP_200_OK)

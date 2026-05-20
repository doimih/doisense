from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProgramListView.as_view(), name="programs-list"),
    path("active", views.ProgramActiveView.as_view(), name="program-active"),
    path("<int:program_id>", views.ProgramDetailView.as_view(), name="program-detail"),
    path("<int:program_id>/activate", views.ProgramActivateView.as_view(), name="program-activate"),
    path(
        "<int:program_id>/complete-day",
        views.ProgramCompleteDayView.as_view(),
        name="program-complete-day",
    ),
    path(
        "<int:program_id>/days/<int:day_number>", views.ProgramDayView.as_view(), name="program-day"
    ),
    path("<int:program_id>/progress", views.ProgramProgressView.as_view(), name="program-progress"),
    path("<int:program_id>/start", views.ProgramStartView.as_view(), name="program-start"),
    path("<int:program_id>/complete", views.ProgramCompleteView.as_view(), name="program-complete"),
    path("<int:program_id>/pause", views.ProgramPauseView.as_view(), name="program-pause"),
    path("<int:program_id>/resume", views.ProgramResumeView.as_view(), name="program-resume"),
    path(
        "<int:program_id>/reflection",
        views.ProgramReflectionView.as_view(),
        name="program-reflection",
    ),
]

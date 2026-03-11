from django.urls import path

from . import views

urlpatterns = [
    path("", views.ProgramListView.as_view(), name="programs-list"),
    path("<int:program_id>/days/<int:day_number>", views.ProgramDayView.as_view(), name="program-day"),
    path("<int:program_id>/progress", views.ProgramProgressView.as_view(), name="program-progress"),
]

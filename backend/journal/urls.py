from django.urls import path

from . import views

urlpatterns = [
    path("questions", views.JournalQuestionsView.as_view(), name="journal-questions"),
    path("entries", views.JournalEntriesView.as_view(), name="journal-entries"),
]

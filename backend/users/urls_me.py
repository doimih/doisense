from django.urls import path

from . import views

urlpatterns = [
    path("me", views.MeView.as_view(), name="me"),
    path("me/export", views.MeExportView.as_view(), name="me-export"),
    path("me/re-onboarding", views.ReOnboardingView.as_view(), name="me-re-onboarding"),
    path("me/change-password", views.ChangePasswordView.as_view(), name="me-change-password"),
]

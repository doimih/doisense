from django.urls import path

from . import views

urlpatterns = [
    path("register", views.RegisterView.as_view(), name="auth-register"),
    path("activate", views.ActivateAccountView.as_view(), name="auth-activate"),
    path("login", views.LoginView.as_view(), name="auth-login"),
    path("social", views.SocialLoginView.as_view(), name="auth-social-login"),
    path("refresh", views.RefreshView.as_view(), name="auth-refresh"),
    path("recover", views.PasswordRecoveryRequestView.as_view(), name="auth-recover"),
    path("recover/confirm", views.PasswordResetConfirmView.as_view(), name="auth-recover-confirm"),
]

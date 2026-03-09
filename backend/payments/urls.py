from django.urls import path

from . import views

urlpatterns = [
    path("create-checkout-session", views.CreateCheckoutSessionView.as_view(), name="create-checkout-session"),
    path("create-billing-portal-session", views.CreateBillingPortalSessionView.as_view(), name="create-billing-portal-session"),
    path("saved-card", views.SavedCardView.as_view(), name="saved-card"),
    path("webhook", views.stripe_webhook, name="stripe-webhook"),
]

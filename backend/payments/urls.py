from django.urls import path

from . import views

urlpatterns = [
    path("create-checkout-session", views.CreateCheckoutSessionView.as_view(), name="create-checkout-session"),
    path("create-billing-portal-session", views.CreateBillingPortalSessionView.as_view(), name="create-billing-portal-session"),
    path("saved-card", views.SavedCardView.as_view(), name="saved-card"),
    path("upgrade", views.UpgradeSubscriptionView.as_view(), name="upgrade-subscription"),
    path("cancel", views.CancelSubscriptionView.as_view(), name="cancel-subscription"),
    path("status", views.SubscriptionStatusView.as_view(), name="subscription-status"),
    path("webhook", views.stripe_webhook, name="stripe-webhook"),
]

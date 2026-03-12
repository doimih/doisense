from django.urls import path

from . import views

urlpatterns = [
    path("cms/pages", views.CMSPageListView.as_view(), name="cms-pages-list"),
    path("cms/pages/<slug:slug>", views.CMSPageDetailView.as_view(), name="cms-page-detail"),
    path("cms/public/<slug:slug>", views.CMSPublicPageView.as_view(), name="cms-page-public"),
    path("cms/preview/<slug:slug>", views.CMSPublicPreviewPageView.as_view(), name="cms-page-preview"),
    path("cms/menu-links", views.CMSMenuLinksView.as_view(), name="cms-menu-links"),
    path("geo/language", views.GeoLanguageView.as_view(), name="geo-language"),
    path("search", views.SearchView.as_view(), name="full-search"),
    path("analytics/track", views.AnalyticsTrackView.as_view(), name="analytics-track"),
    path("contact/config", views.ContactConfigView.as_view(), name="contact-config"),
    path("contact/submit", views.ContactSubmitView.as_view(), name="contact-submit"),
    path("settings/images", views.SettingsImageLibraryView.as_view(), name="settings-images"),
    path("wellbeing/checkins", views.WellbeingCheckinView.as_view(), name="wellbeing-checkins"),
    path("wellbeing/summary", views.WellbeingSummaryView.as_view(), name="wellbeing-summary"),
    path("notifications", views.InAppNotificationListView.as_view(), name="notifications-list"),
    path("notifications/<int:notification_id>/read", views.InAppNotificationReadView.as_view(), name="notifications-read"),
    path("notifications/preferences", views.NotificationPreferenceView.as_view(), name="notifications-preferences"),
    path("support/tickets", views.SupportTicketListCreateView.as_view(), name="support-tickets"),
]

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
    path("newsletter/subscribe", views.NewsletterSubscribeView.as_view(), name="newsletter-subscribe"),
    path("wellbeing/checkins", views.WellbeingCheckinView.as_view(), name="wellbeing-checkins"),
    path("wellbeing/summary", views.WellbeingSummaryView.as_view(), name="wellbeing-summary"),
]

from django.urls import path

from . import views

urlpatterns = [
    path("cms/pages", views.CMSPageListView.as_view(), name="cms-pages-list"),
    path("cms/pages/<slug:slug>", views.CMSPageDetailView.as_view(), name="cms-page-detail"),
    path("search", views.SearchView.as_view(), name="full-search"),
]

from django.urls import path

from .api_views import SocialGenerateView, SocialPostsListView, SocialPublishView


urlpatterns = [
    path("posts/", SocialPostsListView.as_view(), name="social-posts-list"),
    path("generate/", SocialGenerateView.as_view(), name="social-generate"),
    path("publish/", SocialPublishView.as_view(), name="social-publish"),
]
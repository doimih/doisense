from django.urls import path
from . import views_support

urlpatterns = [
    path("ask", views_support.SupportChatView.as_view(), name="support-ask"),
]

from django.urls import path

from . import views_chat
from . import views_reports

urlpatterns = [
    path("send", views_chat.SendChatView.as_view(), name="chat-send"),
    path("send-stream", views_chat.SendChatStreamView.as_view(), name="chat-send-stream"),
    path("history", views_chat.ChatHistoryView.as_view(), name="chat-history"),
    path("translate-draft", views_chat.TranslateDraftView.as_view(), name="chat-translate-draft"),
    path("reports", views_reports.ReportListView.as_view(), name="chat-reports"),
]

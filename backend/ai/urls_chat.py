from django.urls import path

from . import views_chat
from . import views_reports

urlpatterns = [
    path("send", views_chat.SendChatView.as_view(), name="chat-send"),
    path("history", views_chat.ChatHistoryView.as_view(), name="chat-history"),
    path("reports", views_reports.ReportListView.as_view(), name="chat-reports"),
]

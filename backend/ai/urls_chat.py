from django.urls import path

from . import views_chat

urlpatterns = [
    path("send", views_chat.SendChatView.as_view(), name="chat-send"),
]

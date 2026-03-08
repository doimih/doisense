# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.MyModelListView.as_view(), name="mymodel-list"),
]

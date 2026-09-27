from django.urls import path
from .views import analyze_github, chat_analysis

urlpatterns = [
    path("analyze/", analyze_github, name="analyze_github"),
    path("chat/", chat_analysis, name="chat"),
]
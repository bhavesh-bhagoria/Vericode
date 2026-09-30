from django.urls import path

from .views import analyze_github, chat_analysis
from .auth_views import register, login, refresh
from .auth_views import register, login, refresh, verify_email
from .auth_views import register, login, refresh, verify_email, me
from .views import (
    analyze_github,
    chat_analysis,
    list_analyses
)

urlpatterns = [
    path("auth/register/", register, name="register"),
    path("auth/login/", login, name="login"),
    path("auth/refresh/", refresh, name="refresh"),
    path(
        "auth/verify-email/<str:token>/",
        verify_email,
        name="verify_email"
    ),
    path("auth/me/", me, name="me"),
    path("analyze/", analyze_github, name="analyze_github"),
    path("chat/", chat_analysis, name="chat"),
    path("analyses/", list_analyses, name="list_analyses"),
]
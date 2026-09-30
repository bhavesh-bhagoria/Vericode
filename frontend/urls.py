from django.contrib import admin
from django.urls import path, include
from frontend.views import home
from frontend.views import home, login_page, register_page

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("detector.urls")),

    path("login/", login_page, name="login"),

    path(
        "register/",
        register_page,
        name="register"
    ),

    path("", home),
]

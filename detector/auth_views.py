from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


@api_view(["POST"])
def register(request):

    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {
                "error": "Username and password are required"
            },
            status=400
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {
                "error": "Username already exists"
            },
            status=400
        )

    user = User.objects.create_user(
        username=username,
        password=password
    )

    return Response(
        {
            "message": "User registered successfully"
        },
        status=201
    )


@api_view(["POST"])
def login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {
                "error": "Invalid username or password"
            },
            status=401
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
    )


@api_view(["POST"])
def refresh(request):

    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response(
            {
                "error": "Refresh token is required"
            },
            status=400
        )

    try:
        refresh = RefreshToken(refresh_token)

        return Response(
            {
                "access": str(refresh.access_token)
            }
        )

    except Exception:
        return Response(
            {
                "error": "Invalid refresh token"
            },
            status=401
        )
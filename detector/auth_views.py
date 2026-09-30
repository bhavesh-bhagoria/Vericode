from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import secrets
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from .models import Profile


@api_view(["POST"])
def register(request):

    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")
    confirm_password = request.data.get("confirm_password")

    if not username or not email or not password or not confirm_password:
        return Response(
            {"error": "All fields are required"},
            status=400
        )

    if password != confirm_password:
        return Response(
            {"error": "Passwords do not match"},
            status=400
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=400
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"},
            status=400
        )

    try:

        with transaction.atomic():

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            verification_token = secrets.token_urlsafe(32)

            Profile.objects.create(
                user=user,
                email_verified=False,
                verification_token=verification_token,
                token_created_at=timezone.now()
            )

            verification_link = (
                f"http://127.0.0.1:8000/"
                f"verify-email/{verification_token}/"
            )

            send_mail(
                subject="Verify your VeriCode account",
                message=(
                    f"Welcome to VeriCode!\n\n"
                    f"Please verify your email by clicking this link:\n\n"
                    f"{verification_link}\n\n"
                    f"This link expires in 24 hours."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

    except Exception as error:

        return Response(
            {"error": f"Registration failed: {str(error)}"},
            status=500
        )

    return Response(
        {
            "message": (
                "Registration successful. "
                "Please check your email to verify your account."
            )
        },
        status=201
    )

@api_view(["GET"])
def verify_email(request, token):

    try:
        profile = Profile.objects.get(
            verification_token=token
        )
    except Profile.DoesNotExist:
        return Response(
            {"error": "Invalid verification link"},
            status=400
        )

    if profile.email_verified:
        return Response(
            {"message": "Email is already verified"},
            status=200
        )

    token_age = timezone.now() - profile.token_created_at

    if token_age > timedelta(hours=24):
        return Response(
            {"error": "Verification link has expired"},
            status=400
        )

    profile.email_verified = True
    profile.verification_token = None
    profile.token_created_at = None
    profile.save()

    return Response(
        {"message": "Email verified successfully"},
        status=200
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
            {"error": "Invalid username or password"},
            status=401
        )

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response(
            {"error": "Email verification is required"},
            status=403
        )

    if not profile.email_verified:
        return Response(
            {"error": "Please verify your email before logging in"},
            status=403
        )

    refresh = RefreshToken.for_user(user)

    return Response(
    {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username
    }
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({
        "username": request.user.username,
        "email": request.user.email
    })


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
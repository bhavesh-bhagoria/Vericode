from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    email_verified = models.BooleanField(
        default=False
    )

    verification_token = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    token_created_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


class Analysis(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    github_url = models.URLField()

    analysis_result = models.JSONField()

    source_code = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.github_url}"
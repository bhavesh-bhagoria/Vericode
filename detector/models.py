from django.db import models
from django.contrib.auth.models import User


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
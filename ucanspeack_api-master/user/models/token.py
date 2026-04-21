import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class UserToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    key = models.CharField(max_length=64, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    last_used_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Последнее использование"
    )
    expires_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Истекает"
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="IP"
    )
    user_agent = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="User-Agent"
    )

    class Meta:
        verbose_name = "Токен авторизации"
        verbose_name_plural = "Токены авторизации"
        indexes = [
            models.Index(fields=['expires_at']),
            models.Index(fields=['user', 'created']),
        ]

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = uuid.uuid4().hex
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

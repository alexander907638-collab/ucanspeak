from django.conf import settings
from django.db import models
from django.utils import timezone


class UserSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='active_sessions',
        verbose_name='Пользователь',
    )

    # Идентификатор JWT refresh токена. Используется чтобы связать сессию с token_blacklist.
    # Берётся из payload JWT (jti claim).
    refresh_jti = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='JTI refresh токена',
    )

    user_agent = models.TextField(blank=True, default='', verbose_name='User-Agent')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')

    # Парсенное для UI представление
    device_name = models.CharField(
        max_length=120,
        default='Неизвестное устройство',
        verbose_name='Устройство',
    )
    browser_name = models.CharField(
        max_length=60,
        default='',
        verbose_name='Браузер',
    )
    os_name = models.CharField(
        max_length=60,
        default='',
        verbose_name='ОС',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    last_activity_at = models.DateTimeField(auto_now=True, verbose_name='Последняя активность')

    class Meta:
        ordering = ['-last_activity_at']
        verbose_name = 'Сессия пользователя'
        verbose_name_plural = 'Сессии пользователей'
        indexes = [
            models.Index(fields=['user', '-last_activity_at']),
        ]

    def __str__(self):
        return f'{self.user} — {self.device_name} ({self.ip_address})'

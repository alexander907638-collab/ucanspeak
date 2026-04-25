from djoser.serializers import TokenCreateSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from user.models import UserToken

User = get_user_model()


def get_client_ip(request):
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class CustomTokenCreateSerializer(TokenCreateSerializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        from user.utils import find_user_by_login_or_email

        login = attrs.get("login")
        password = attrs.get("password")

        user = find_user_by_login_or_email(login)
        if user is None:
            raise serializers.ValidationError({"detail": "Пользователь не найден"})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Неверный пароль"})

        # cleanup просроченных токенов перед подсчётом лимита
        UserToken.objects.filter(user=user, expires_at__lt=timezone.now()).delete()

        max_logins = user.max_logins or 5
        active_count = UserToken.objects.filter(user=user).count()
        if active_count >= max_logins:
            raise serializers.ValidationError({
                "max_sessions_reached": True,
                "detail": f"Превышен лимит одновременных сессий ({max_logins})"
            })

        attrs["user"] = user
        return attrs

    def create_token(self, request):
        """Вызывается из view после успешной валидации."""
        user = self.validated_data["user"]
        ip = get_client_ip(request)
        ua = (request.headers.get("User-Agent") or "")[:500]
        token = UserToken.objects.create(
            user=user,
            ip_address=ip,
            user_agent=ua,
        )
        return token

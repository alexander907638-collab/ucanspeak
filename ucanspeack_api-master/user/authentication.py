from datetime import timedelta

from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from user.models import UserToken


class MultiTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Token "):
            return None

        key = auth.replace("Token ", "")

        try:
            token = UserToken.objects.select_related("user").get(key=key)
        except UserToken.DoesNotExist:
            raise AuthenticationFailed("Invalid token")

        if token.is_expired():
            token.delete()
            raise AuthenticationFailed("Token expired")

        # обновляем last_used_at не чаще раза в минуту
        now = timezone.now()
        if token.last_used_at is None or (now - token.last_used_at) > timedelta(minutes=1):
            UserToken.objects.filter(pk=token.pk).update(last_used_at=now)

        return (token.user, token)

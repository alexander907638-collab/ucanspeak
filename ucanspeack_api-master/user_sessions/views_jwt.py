from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.response import Response
from rest_framework import status

from .models import UserSession
from .utils import parse_user_agent, get_client_ip


class LoginWithSessionView(TokenObtainPairView):
    """Обычный Djoser login + создание UserSession."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code != 200:
            return response

        refresh = response.data.get('refresh')
        if not refresh:
            return response

        # Парсим JTI из refresh токена
        token = RefreshToken(refresh)
        jti = token['jti']

        # Находим юзера по access токену (он содержит user_id)
        access = response.data.get('access')
        user_id = UntypedToken(access)['user_id']

        ua_info = parse_user_agent(request.META.get('HTTP_USER_AGENT', ''))
        UserSession.objects.create(
            user_id=user_id,
            refresh_jti=jti,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:2000],
            ip_address=get_client_ip(request),
            **ua_info,
        )

        return response


class RefreshWithSessionView(TokenRefreshView):
    """При rotate refresh — обновляем JTI в UserSession."""

    def post(self, request, *args, **kwargs):
        old_refresh = request.data.get('refresh')
        response = super().post(request, *args, **kwargs)
        if response.status_code != 200:
            return response

        new_refresh = response.data.get('refresh')
        if not old_refresh or not new_refresh:
            return response

        try:
            old_jti = RefreshToken(old_refresh)['jti']
        except Exception:
            return response

        try:
            new_jti = RefreshToken(new_refresh)['jti']
        except Exception:
            return response

        # Обновляем JTI у существующей сессии
        UserSession.objects.filter(refresh_jti=old_jti).update(refresh_jti=new_jti)
        return response

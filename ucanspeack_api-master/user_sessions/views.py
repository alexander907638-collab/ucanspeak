from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from .models import UserSession
from .serializers import UserSessionSerializer


def _get_current_jti(request):
    """Извлекает JTI access-токена из заголовка Authorization. У access и refresh разные JTI,
    поэтому прямо сопоставить невозможно — используем другое поле. Для MVP возвращаем None
    и помечаем is_current на фронте по IP+user-agent совпадению текущего запроса."""
    # Упрощение: ставим is_current на последнюю активную сессию с таким же UA.
    return None


class UserSessionViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSession.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['current_ua'] = self.request.META.get('HTTP_USER_AGENT', '')
        return ctx

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        current_ua = request.META.get('HTTP_USER_AGENT', '')

        # Определяем текущую сессию: самая свежая с таким же UA
        current_session_id = None
        if current_ua:
            current = qs.filter(user_agent=current_ua).order_by('-last_activity_at').first()
            if current:
                current_session_id = current.id

        data = self.get_serializer(qs, many=True).data
        for item in data:
            item['is_current'] = item['id'] == current_session_id

        return Response({
            'count': len(data),
            'max_sessions': getattr(request.user, 'max_logins', 1),
            'results': data,
        })

    def destroy(self, request, *args, **kwargs):
        """Удалить конкретную сессию (== выйти на этом устройстве).
        Блэклистит все refresh токены этой сессии."""
        session = self.get_object()

        # Blacklist refresh токен
        try:
            outstanding = OutstandingToken.objects.get(jti=session.refresh_jti)
            BlacklistedToken.objects.get_or_create(token=outstanding)
        except OutstandingToken.DoesNotExist:
            pass

        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='terminate-all')
    def terminate_all(self, request):
        """Выйти со ВСЕХ устройств, кроме текущего.
        Если include_current=true — включая текущее (полный логаут отовсюду)."""
        include_current = request.data.get('include_current', False)

        qs = self.get_queryset()

        if not include_current:
            current_ua = request.META.get('HTTP_USER_AGENT', '')
            current = qs.filter(user_agent=current_ua).order_by('-last_activity_at').first()
            if current:
                qs = qs.exclude(pk=current.pk)

        # Blacklist все refresh токены
        jtis = list(qs.values_list('refresh_jti', flat=True))
        outstanding_qs = OutstandingToken.objects.filter(jti__in=jtis)
        for token in outstanding_qs:
            BlacklistedToken.objects.get_or_create(token=token)

        count = qs.count()
        qs.delete()

        return Response({'terminated': count})

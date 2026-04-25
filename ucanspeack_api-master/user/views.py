from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from user.models import School, UserToken
from user.serializers.me import UserSerializer
from user.serializers.auth import get_client_ip
from djoser.views import TokenCreateView
from rest_framework import generics, viewsets, parsers

import logging

from user.serializers.school import SchoolSerializer

logger = logging.getLogger(__name__)




class CustomTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        token = serializer.create_token(self.request)
        return Response({"auth_token": token.key}, status=200)

class GetUser(generics.RetrieveAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        print(self.request.user)
        return self.request.user


class SchoolData(APIView):
    def get(self, request):
        slug = request.GET.get('slug', None)
        result = {'image':None}
        if slug:
            qs = School.objects.filter(slug=slug)
            if qs.exists():
                school = qs.first()
                serializer = SchoolSerializer(school)
                result = serializer.data
        return Response(result, status=200)

class UpdateUser(APIView):
    def patch(self, request):
        print(request.data)
        serializer = UserSerializer(instance=request.user, data=request.data)
        password = request.data.get('password', None)
        logo = request.FILES.get('logo', None)


        if serializer.is_valid():
            user = serializer.save()

            if password:
                user.set_password(password)
                user.save()

            if logo:
                school_obj = School.objects.get(admin=user)
                school_obj.image = logo
                school_obj.save()

            return Response(status=200)
        else:
            print(serializer.errors)
            return Response(serializer.errors,status=400)


class ForceLoginView(APIView):
    """
    Удаляет ВСЕ токены пользователя и создаёт новый.
    Используется когда у юзера превышен лимит сессий и он
    сознательно хочет выгнать остальные устройства.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        login = request.data.get("login")
        password = request.data.get("password")
        if not login or not password:
            return Response(
                {"detail": "login и password обязательны"}, status=400
            )

        from user.utils import find_user_by_login_or_email

        user = find_user_by_login_or_email(login)
        if user is None:
            return Response({"detail": "Пользователь не найден"}, status=400)

        if not user.check_password(password):
            return Response({"detail": "Неверный пароль"}, status=400)

        # удаляем все существующие токены
        UserToken.objects.filter(user=user).delete()

        # создаём новый
        ip = get_client_ip(request)
        ua = (request.headers.get("User-Agent") or "")[:500]
        token = UserToken.objects.create(
            user=user,
            ip_address=ip,
            user_agent=ua,
        )
        return Response({"auth_token": token.key}, status=200)


# Сессия 2 — UserToken: expires, IP, user-agent, лимит сессий

Контекст: S1 + S1.5 уже выполнены. Теперь делаем правильную работу с токенами.

Все пути — от родительской папки:
- `ucanspeack_api-master/` — Django бэк
- `ucanspeak_front-master/` — Nuxt фронт

Цели:
- Токены живут 7 дней с момента создания
- На каждом аутентифицированном запросе обновляется `last_used_at` (но не чаще чем раз в минуту)
- Сохраняются IP и user-agent (для админки)
- Истёкшие токены удаляются при попытке использования и при логине
- Когда лимит сессий превышен — фронт показывает модалку «Превышен лимит, выйти отовсюду и войти?». По кнопке — все токены пользователя удаляются и создаётся новый.
- Модалка реализована через обычный PrimeVue `<Dialog>` (не `useConfirm()` — `ConfirmationService` в этом проекте не подключён, см. `app/plugins/primevue.ts`).

Выполни 5 задач последовательно. После каждой — короткий отчёт. В конце — финальная сводка с инструкциями по миграциям.

---

## Задача 1 — расширить модель UserToken

Файл: `ucanspeack_api-master/user/models/token.py`.

Сейчас в модели только `user`, `key`, `created`. Нужно:
- `last_used_at` — когда токен использовался последний раз
- `expires_at` — когда токен истечёт. По умолчанию `now + 7 days` при создании
- `ip_address` — IP клиента (GenericIPAddressField, nullable)
- `user_agent` — User-Agent (CharField max=500, nullable)
- метод `is_expired()`
- индексы для быстрых cleanup-запросов и FIFO

Перепиши файл целиком так:
```python
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
```

Важно: для существующих токенов `expires_at` будет `NULL` (миграция установит default только для новых). Чтобы старые токены не разлогинили живых пользователей, метод `is_expired` для `expires_at IS NULL` возвращает `False` — намеренно. Новые токены получают 7-дневный TTL.

---

## Задача 2 — обновить MultiTokenAuthentication

Файл: `ucanspeack_api-master/user/authentication.py`.

Нужно:
- Проверять `is_expired` — если истёк, удалять токен и кидать `AuthenticationFailed("Token expired")`
- Обновлять `last_used_at` — но не чаще раза в минуту (чтобы не было лишнего UPDATE на каждый GET)

Перепиши файл так:
```python
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
```

Используем `UserToken.objects.filter(pk=token.pk).update(...)` вместо `token.save()` чтобы не триггерить переустановку `expires_at`.

---

## Задача 3 — переделать CustomTokenCreateSerializer

Файл: `ucanspeack_api-master/user/serializers/auth.py`.

Сейчас:
- Токен создаётся в `validate()` (антипаттерн — validate должен быть чистым)
- При превышении лимита возвращается строка, фронт не понимает что делать

Должно быть:
- Логика создания токена выделена в `create_token(request)` (вызывается из view)
- При превышении лимита — `ValidationError({"max_sessions_reached": True, "detail": "..."})`
- Cleanup истёкших токенов перед подсчётом лимита
- IP и user-agent сохраняются в токене
- Вспомогательная функция `get_client_ip` экспортируется (используется в ForceLoginView)

Перепиши файл целиком так:
```python
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
        login = attrs.get("login")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=login)
        except User.DoesNotExist:
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
```

---

## Задача 4 — CustomTokenCreateView + ForceLoginView + URL

### 4a. CustomTokenCreateView

Файл: `ucanspeack_api-master/user/views.py`.

Сейчас `CustomTokenCreateView._action` вызывает `serializer.is_valid()` и возвращает `validated_data`. После задачи 3 — токен надо создавать здесь, через `create_token(request)`.

Найди класс `CustomTokenCreateView` и перепиши его метод `_action`:
```python
class CustomTokenCreateView(TokenCreateView):
    def _action(self, serializer):
        token = serializer.create_token(self.request)
        return Response({"auth_token": token.key}, status=200)
```

(в Djoser `_action` получает уже валидированный сериализатор; `is_valid()` вызывается родителем до этого)

### 4b. ForceLoginView

В тот же файл `ucanspeack_api-master/user/views.py` добавь:
```python
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from user.serializers.auth import get_client_ip


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

        User = get_user_model()
        try:
            user = User.objects.get(email=login)
        except User.DoesNotExist:
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
```

Проверь импорт `UserToken` в этом файле — он должен быть. Если нет, добавь в существующую строку с импортами `from user.models import ...`.

### 4c. URL

Файл: `ucanspeack_api-master/user/urls.py`. Добавь маршрут (рядом с другими `path`):
```python
path('force_login', views.ForceLoginView.as_view()),
```

---

## Задача 5 — фронт + админка UserToken

### 5a. Метод force_login в auth repository

Файл: `ucanspeak_front-master/app/repository/auth/index.ts`.

Добавь в возвращаемый объект (рядом с `register`, `login`):
```typescript
force_login(body: any) {
    return appFetch('/api/user/force_login', {
        method: 'POST',
        body
    })
},
```

### 5b. Модалка «лимит сессий» в Login.vue

Файл: `ucanspeak_front-master/app/components/Form/Login.vue`.

Сейчас в `catch` блока `login()` обращение к `error.data.non_field_errors[0]`. После S2 формат ошибок другой. Плюс нужна модалка для `max_sessions_reached`.

`ConfirmationService` в проекте не подключён, поэтому делаем модалку через обычный `<Dialog>`.

Перепиши `<script setup>` целиком так:
```vue
<script setup lang="ts">
const emits = defineEmits(['change_form'])
import { useToast } from 'primevue/usetoast';
const toast = useToast()
const {$api} = useNuxtApp()
const loading = ref(false)
defineProps(['school_auth'])

const form_data = ref({
  login: '',
  password: '',
})

const max_sessions_dialog_visible = ref(false)
const max_sessions_message = ref('')
const force_loading = ref(false)

watch(
    () => form_data.value.login,
    (newEmail) => {
      form_data.value.login = newEmail.toLowerCase()
    }
)

const setAuthCookieAndRedirect = (token: string) => {
  const authCookie = useCookie('auth_token', {
    maxAge: 60 * 60 * 24 * 7,
  })
  authCookie.value = token
  window.location.href = '/courses'
}

const login = async () => {
  loading.value = true
  try {
    const response = await $api.auth.login(form_data.value)
    setAuthCookieAndRedirect(response.auth_token)
    toast.add({ severity: 'success', summary: 'Успешно', detail: 'Получение данных пользователя...', life: 3000 })
  } catch (error: any) {
    const data = error?.data
    if (data?.max_sessions_reached === true) {
      max_sessions_message.value = data.detail || 'Превышен лимит одновременных сессий'
      max_sessions_dialog_visible.value = true
    } else if (data?.detail) {
      toast.add({ severity: 'error', summary: 'Ошибка', detail: data.detail, life: 3000 })
    } else {
      toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось войти', life: 3000 })
    }
  } finally {
    loading.value = false
  }
}

const forceLogin = async () => {
  force_loading.value = true
  try {
    const response = await $api.auth.force_login(form_data.value)
    max_sessions_dialog_visible.value = false
    setAuthCookieAndRedirect(response.auth_token)
  } catch (error: any) {
    const data = error?.data
    toast.add({
      severity: 'error',
      summary: 'Ошибка',
      detail: data?.detail || 'Не удалось войти',
      life: 3000
    })
  } finally {
    force_loading.value = false
  }
}
</script>
```

В `<template>` добавь Dialog после `</CardBase>`, перед закрывающим `</template>`:
```vue
<Dialog
    v-model:visible="max_sessions_dialog_visible"
    modal
    header="Превышен лимит сессий"
    :style="{ width: '420px' }"
>
  <p class="mb-4">{{ max_sessions_message }}</p>
  <p class="text-sm text-gray-500 mb-2">
    Если нажмёте «Выйти отовсюду и войти» — все ваши активные сессии на других устройствах будут завершены, и вы войдёте на этом устройстве.
  </p>
  <template #footer>
    <Button
        label="Отмена"
        severity="secondary"
        text
        @click="max_sessions_dialog_visible = false"
    />
    <Button
        label="Выйти отовсюду и войти"
        severity="danger"
        :loading="force_loading"
        @click="forceLogin"
    />
  </template>
</Dialog>
```

### 5c. Админка UserToken — показать новые поля

Файл: `ucanspeack_api-master/user/admin.py`.

Замени класс `UserTokenAdmin` целиком на:
```python
@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "user_email", "user_login",
        "created", "last_used_at", "expires_at", "is_expired_display",
        "ip_address", "user_agent_short", "short_key",
    )
    list_select_related = ("user",)
    search_fields = (
        "user__email", "user__login", "user__full_name",
        "key", "ip_address",
    )
    list_filter = ("created", "expires_at")
    ordering = ("-created",)
    readonly_fields = ("created", "key", "last_used_at")

    @admin.display(description="Email", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Login", ordering="user__login")
    def user_login(self, obj):
        return obj.user.login

    @admin.display(description="Token")
    def short_key(self, obj):
        return obj.key[:12] + "..."

    @admin.display(description="UA", ordering="user_agent")
    def user_agent_short(self, obj):
        if not obj.user_agent:
            return "-"
        return obj.user_agent[:50] + ("..." if len(obj.user_agent) > 50 else "")

    @admin.display(description="Истёк?", boolean=True)
    def is_expired_display(self, obj):
        return obj.is_expired()
```

---

## Финальная сводка

Выведи:
1. Список всех изменённых файлов
2. **Команды для Александра — выполнить вручную в виртуальном окружении:**
   ```
   cd ucanspeack_api-master
   python manage.py makemigrations user
   python manage.py migrate user
   ```
   В миграции добавляется 4 поля (`last_used_at`, `expires_at`, `ip_address`, `user_agent`) + 2 индекса. Дефолты на уровне БД не ставятся, новые поля будут NULL для существующих токенов — это намеренно (не разлогинит живых юзеров).
3. **Чеклист ручной проверки:**
   - Старые сессии не разлогинило (открыть приложение в браузере где уже залогинен — должно работать)
   - Логин под новым устройством: в админке `/admin/user/usertoken/` появился токен с заполненными `expires_at` (на 7 дней вперёд), `ip_address`, `user_agent`
   - Через минуту-полторы использования — `last_used_at` обновился
   - В psql вручную: `UPDATE user_usertoken SET expires_at = now() - interval '1 day' WHERE id = <твой токен>;` — следующий запрос с этим токеном вернёт 401, токен исчезнет из БД
   - Чтобы проверить модалку: создай тестового юзера с `max_logins=1`, залогинься в обычном браузере, потом в инкогнито тем же email/паролем — должен получить модалку, кнопка «Выйти отовсюду и войти» работает: создаётся новый токен, старый удаляется (юзер в обычном браузере получит 401 на следующем запросе)
4. Что НЕ сделано в этой сессии (для будущих):
   - Rate-limiting на `force_login` (защита от брутфорса) — отдельная мини-сессия
   - Endpoint «выгнать ученика» школьным админом (заглушка из S1.5 ждёт настоящего endpoint)

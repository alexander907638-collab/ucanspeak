# Сессия 1 — критические security-фиксы и мелкие баги

Контекст проекта: два репозитория в соседних папках.
- `ucanspeack_api-master/` — Django 5 + DRF + Djoser, Token authentication (не JWT), PostgreSQL
- `ucanspeak_front-master/` — Nuxt 4, Pinia, TypeScript, Tailwind, Vite, SPA

Все пути ниже указаны от родительской папки, в которой запущен Claude Code.

Выполни последовательно 5 задач. После каждой — коротко отчитайся (изменённые файлы, что именно сделано, без воды). Не жди подтверждения, иди к следующей. В конце — финальная сводка.

Не запускай `makemigrations` и не меняй зависимости. Это Сессия 1, только код.

---

## Задача 1 — удалить небезопасный эндпоинт массового логаута

В `ucanspeack_api-master/user/views.py` существует класс `LogoutUser`. Он принимает `user_id` из body без проверки авторизации и удаляет все токены указанного пользователя. Это дыра — любой авторизованный пользователь может разлогинить любого другого.

Параллельно существует корректный `CustomLogoutView` (`ucanspeack_api-master/user/logout.py`), подключённый в `ucanspeack_api-master/ucanspeack_api/urls.py` как `/auth/token/logout/`. Он и должен использоваться.

Сделай:
1. В `ucanspeack_api-master/user/views.py` удали целиком класс `LogoutUser` (включая импорты, которые станут неиспользуемыми после удаления).
2. В `ucanspeack_api-master/user/urls.py` удали строку `path('logout', views.LogoutUser.as_view()),`. Остальные пути не трогай.
3. Во фронте (`ucanspeak_front-master/`) найди использование метода `logout_user`:
   - В `app/repository/auth/index.ts` удали метод `logout_user` (вызов на `/api/user/logout` с `user_id` в body).
   - Grep по всему фронту (`app/**/*.{vue,ts,js}`) на подстроки `logout_user` и `api.auth.logout_user`. Если найдёшь вызовы — замени их на TODO-комментарий: `// TODO(ucanspeak): небезопасный принудительный логаут ученика удалён. Нужен отдельный endpoint для admin школы с IsSchoolAdmin permission`. Не ломай работоспособность окружающего кода — если это был `await ...` внутри функции, замени на `// TODO` и удали await так, чтобы функция оставалась синтаксически корректной.

Проверка: `grep -r "LogoutUser" ucanspeack_api-master/` должен выдать совпадения только в миграциях и комментариях (если они есть). `grep -rn "logout_user" ucanspeak_front-master/app/` — только в комментариях/TODO.

---

## Задача 2 — закрыть write-поля в UserSerializer

В `ucanspeack_api-master/user/serializers/me.py` класс `UserSerializer` имеет в `extra_kwargs` строку `'is_superuser': {'read_only': False}`. Это дыра: любой юзер через `PATCH /api/user/update` может установить себе `is_superuser=true`.

Тот же `UserSerializer` переиспользуется в `SchoolPupilViewSet.create` (создание ученика школьным админом) — и там та же дыра: школьный админ может при создании ученика назначить его суперюзером.

Сделай:
1. В `UserSerializer.Meta.read_only_fields` добавь: `'is_superuser'`, `'subscription_expire'`, `'is_school'`, `'last_lesson_url'`. Обоснование: `is_school` не должно меняться после регистрации, `subscription_expire` меняется биллингом (будущее), `last_lesson_url` устанавливается сервером в `ModuleViewSet.retrieve`.
2. Из `extra_kwargs` полностью удали ключ `'is_superuser'` (с его `'read_only': False`). Ключ `'password'` с `{'required': False}` оставь как есть — это ок для PATCH.

После этого ожидаемое поведение: `PATCH /api/user/update` с body `{"is_superuser": true}` — проходит, но поле игнорируется, `is_superuser` остаётся прежним.

---

## Задача 3 — закрыть content API от записи + удалить мёртвый код

В `ucanspeack_api-master/lesson/views.py` классы `CourseViewSet`, `LevelViewSet`, `LessonViewSet`, `ModuleViewSet`, `VideoViewSet`, `PhraseViewSet`, `DictionaryGroupViewSet`, `DictionaryItemViewSet` — это `ModelViewSet` без `permission_classes`. Любой неавторизованный пользователь может удалить курс через `DELETE /api/lesson/courses/<slug>/`.

Нужно закрыть mutator-методы (PUT/PATCH/DELETE), но сохранить:
- GET (чтение контента)
- POST на custom actions через `@action(methods=['post'])` (`toggle_favorite`, `toggle_block`)

Сделай:
1. Для каждого из перечисленных ViewSet'ов добавь в класс атрибут:
   ```python
   http_method_names = ['get', 'head', 'options', 'post']
   ```
   POST оставляем потому что custom actions используют POST. Прямой `POST /api/lesson/courses/` (создание) всё равно не поломает ничего: роутер DRF для этого вызовет `create()`, который на `ModelViewSet` есть, но без валидных прав будет доступен — так что дополнительно:
2. Добавь `permission_classes = [IsAuthenticatedOrReadOnly]` в каждый из этих ViewSet'ов. Импорт: `from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated`.
3. Для конкретных custom actions, которые должны быть доступны ТОЛЬКО авторизованным, добавь `permission_classes=[IsAuthenticated]` в декораторе `@action(...)`. Это касается:
   - `ModuleViewSet.toggle_favorite`
   - `ModuleViewSet.toggle_block`
   - `DictionaryItemViewSet.toggle_favorite`
4. Удали класс `CourseViewSetOld` полностью — это мёртвый дубликат `CourseViewSet`.
5. Удали файл `ucanspeack_api-master/user/services.py` (НЕ папку `user/services/` — именно одноимённый файл рядом с папкой). Внутри него функции `generate_password` и `send_tg_mgs`, которые нигде не используются. Убедись перед удалением — `grep -rn "from user.services import\|from user import services" ucanspeack_api-master/` не должен давать совпадений на этот файл (папка `user/services/` с `__init__.py` — это другое, её не трогай).

---

## Задача 4 — IsAuthenticated на эндпоинтах тренажёра

В `ucanspeack_api-master/train/views.py` классы `TopicDetailView`, `TopicDoneAPIView`, `ToggleFavoriteAPIView`, `FavoriteListAPIView` обращаются к `request.user` как к объекту юзера, без проверки авторизации. Для `AnonymousUser` это кидает 500.

Классы `CourseListView`, `LevelListByCourseView`, `TopicListByLevelView` — это витрина для неавторизованных (юзер смотрит что купить). Их НЕ трогаем.

Сделай:
1. В `ucanspeack_api-master/train/views.py` добавь импорт: `from rest_framework.permissions import IsAuthenticated`.
2. В классах `TopicDetailView`, `TopicDoneAPIView`, `ToggleFavoriteAPIView`, `FavoriteListAPIView` добавь атрибут класса:
   ```python
   permission_classes = [IsAuthenticated]
   ```
3. `CourseListView`, `LevelListByCourseView`, `TopicListByLevelView` — не трогай.

---

## Задача 5 — фронтовые фиксы (три независимых)

### 5a. Длинная фраза в словаре ломает вёрстку

Файл: `ucanspeak_front-master/app/components/Card/DictionaryItem.vue`.

Симптом: длинная фраза типа «шутить, разыгрывать» выпирает из карточки и налезает на соседние элементы сбоку.

Фикс (Tailwind-классы):
- На обёртке карточки с текстом — `max-w-full break-words` (чтобы длинные слова переносились)
- Если в компоненте используется `flex` — добавь `min-w-0` на flex-child с текстом (без этого flex-ребёнок не ужимается)
- Если в родительском компоненте (там, где рендерится список `DictionaryItem`) используется `flex-wrap`, он и сейчас работает — не трогай
- Текст с переносами: `whitespace-normal` если где-то стоит `whitespace-nowrap`

Принеси мне исходный `<template>` и `<script>` этого файла в отчёте по задаче 5a (чтобы я мог оценить правку).

### 5b. Аудио тренажёра: 0:00/0:00, не проигрывается

Симптом: на странице `ucanspeak_front-master/app/pages/courses/trainer/[course_slug]/[level_slug]/[topic_slug]/index.vue` вкладка «Аудиоурок» показывает плеер с 0:00/0:00, mp3 не играет.

Корневая причина: в `ucanspeack_api-master/train/serializers.py::AudioFileSerializer` поле `file` отдаётся как относительный путь (`/media/trainer/mp3/xxx.mp3`), фронт кладёт это в `<audio :src>` без префикса apiUrl. Браузер резолвит относительно фронт-домена → 404 → плеер показывает 0:00.

Эталонный паттерн — в `ucanspeack_api-master/lesson/serializers.py::VideoSerializer.get_file`.

Сделай:
1. В `AudioFileSerializer`:
   - Убери `file` из перечисления полей как ModelField
   - Добавь `file = serializers.SerializerMethodField()`
   - Метод:
     ```python
     def get_file(self, obj):
         request = self.context.get("request")
         if obj.file and request:
             return request.build_absolute_uri(obj.file.url)
         return None
     ```
2. Аналогично для `train/serializers.py::PhraseSerializer` — то же поле `file` через `SerializerMethodField` и тот же метод. Причина: на вкладке «Тест» тренажёра аудио фраз тоже может не играть по этой же причине.
3. Убедись что `TopicDetailView` в `train/views.py` передаёт request в контекст сериализатора. По умолчанию DRF для Generic-views делает это автоматически через `get_serializer_context()`. Проверь вызов `self.get_serializer(topic)` в `TopicDetailView.retrieve` — если он идёт без явного `context={...}`, всё ок. Если с явным контекстом без request — добавь request туда.

### 5c. Фронт не чистит auth_token при 401

Файл: `ucanspeak_front-master/app/plugins/fetch.ts`.

Сейчас в `onResponseError` при `response.status === 401` выполняется `navigateTo('/')`, но кука `auth_token` не очищается. Результат: следующий `fetch` на защищённый endpoint снова 401, петля.

Фикс в обработчике 401, перед `navigateTo`:
```typescript
const authCookie = useCookie('auth_token')
authCookie.value = null
```

---

## Финальная сводка

Выведи:
1. Список всех изменённых файлов с путями
2. Нужны ли миграции Django (я запретил их делать; если нужны — просто скажи какие модели изменились и почему)
3. Что потенциально сломано на фронте и требует ручной проверки
4. Чеклист ручной проверки:
   - логин/регистрация
   - `GET /api/lesson/courses/` для анонима и авторизованного
   - `DELETE /api/lesson/courses/<slug>/` для авторизованного — должен быть 405
   - `PATCH /api/user/update` с `{"is_superuser": true}` — юзер не должен стать суперюзером (проверить через `/api/user/me` после запроса)
   - `GET /api/trainer/topics/<slug>/` для анонима — 401/403, не 500
   - Страница урока: длинный словарный элемент не ломает вёрстку
   - Тренажёр: аудио играет, показывает длительность
   - Истекший токен на фронте: один редирект на `/`, без петли

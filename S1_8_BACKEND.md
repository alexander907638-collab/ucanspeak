# Сессия 1.8 Backend — Прогресс, thumbnail, Redis cache, оптимизации

Контекст: платформа Ucanspeak (Django 5 + DRF + PostgreSQL). Уже задеплоена. Нужно: (1) починить прогресс, чтоб блоки-информация не блокировали галочку «урок пройден», (2) добавить thumbnail к видео чтоб не генерировать первый кадр на фронте каждый раз, (3) подключить Redis cache и gzip + gunicorn воркеры для масштабирования до 200 одновременных юзеров.

Все пути от `ucanspeack_api-master/`. Все команды — **только фиксы в коде**, не запускать миграции и не трогать прод. Миграции Александр применит потом вручную.

**В моделях уже есть поле `ModuleBlock.can_be_done: bool` (default=True).** Его используем.

Выполни 6 задач последовательно.

---

## Задача 1 — Прогресс: исключить блоки с `can_be_done=False` из подсчёта

Файл: `lesson/views.py`. Найди **все аннотации `Count` по блокам** (всего 7 мест). Везде где считается `total_blocks` или `done_blocks` через Count'ы от `modules__blocks` или `blocks`, добавь фильтр по `can_be_done=True`.

### Место 1 — `LevelViewSet.get_queryset()` — `lessons_qs` (около строки 131)

Было:
```python
lessons_qs = Lesson.objects.annotate(
    total_blocks=Count('modules__blocks', distinct=True),
    done_blocks=Count(
        'modules__blocks__moduleblockdone',
        filter=Q(modules__blocks__moduleblockdone__user=user),
        distinct=True
    ),
)
```

Стало:
```python
lessons_qs = Lesson.objects.annotate(
    total_blocks=Count(
        'modules__blocks',
        filter=Q(modules__blocks__can_be_done=True),
        distinct=True
    ),
    done_blocks=Count(
        'modules__blocks__moduleblockdone',
        filter=Q(
            modules__blocks__moduleblockdone__user=user,
            modules__blocks__can_be_done=True
        ),
        distinct=True
    ),
)
```

Также в ветке `else:` (для незалогиненных) поправь `total_blocks` так же.

### Место 2 — `LevelViewSet.get_queryset()` — `levels.annotate()` блок прогресса уровня

Там считается `done_lessons=Count('lessons', filter=Q(lessons__modules__blocks__moduleblockdone__user=user), distinct=True)`. Это **не трогаем** — там считается сколько уроков выполнено, а не блоков. Урок считается выполненным когда `LessonDone` есть. Это уже правильно.

### Место 3 — `LessonViewSet.get_queryset()` — `modules_qs` (около строки 251)

Было:
```python
modules_qs = Module.objects.annotate(
    total_blocks=Count('blocks', distinct=True),
    done_blocks=Count(
        'blocks__moduleblockdone',
        filter=Q(blocks__moduleblockdone__user=user),
        distinct=True
    )
)
```

Стало:
```python
modules_qs = Module.objects.annotate(
    total_blocks=Count(
        'blocks',
        filter=Q(blocks__can_be_done=True),
        distinct=True
    ),
    done_blocks=Count(
        'blocks__moduleblockdone',
        filter=Q(
            blocks__moduleblockdone__user=user,
            blocks__can_be_done=True
        ),
        distinct=True
    )
)
```

И в `else` ветке (для незалогиненных) — поправь `total_blocks` так же.

### Место 4 — `LessonViewSet.get_queryset()` — `lessons_qs` (около строки 275)

Аналогично месту 1. Но здесь поле идёт через `modules__blocks`, так что:
```python
total_blocks=Count(
    'modules__blocks',
    filter=Q(modules__blocks__can_be_done=True),
    distinct=True
),
done_blocks=Count(
    'modules__blocks__moduleblockdone',
    filter=Q(
        modules__blocks__moduleblockdone__user=user,
        modules__blocks__can_be_done=True
    ),
    distinct=True
),
```

В `else` ветке — только `total_blocks` поправь.

### Место 5 — `ModuleViewSet.get_queryset()` — `modules_qs` (около строки 373)

То же что в месте 3.

### Место 6 — `LessonViewSet.toggle_block` (около строки 459)

Было:
```python
lesson_stats = ModuleBlock.objects.filter(
    id=module_block_id
).annotate(
    total_blocks=Count('module__lesson__modules__blocks'),
    done_blocks=Count(
        'module__lesson__modules__blocks__moduleblockdone',
        filter=Q(module__lesson__modules__blocks__moduleblockdone__user=user)
    )
).values('module__lesson', 'total_blocks', 'done_blocks').first()
```

Стало:
```python
lesson_stats = ModuleBlock.objects.filter(
    id=module_block_id
).annotate(
    total_blocks=Count(
        'module__lesson__modules__blocks',
        filter=Q(module__lesson__modules__blocks__can_be_done=True)
    ),
    done_blocks=Count(
        'module__lesson__modules__blocks__moduleblockdone',
        filter=Q(
            module__lesson__modules__blocks__moduleblockdone__user=user,
            module__lesson__modules__blocks__can_be_done=True
        )
    )
).values('module__lesson', 'total_blocks', 'done_blocks').first()
```

Также **убери `print(total_blocks)` и `print(done_blocks)`** — это дебаг строки которые забыли.

### Важно

Нигде **не нужны миграции**, поле `can_be_done` уже есть в модели. Если оно в БД из-за старого дампа отсутствует — это проблема миграций, но в моделях оно есть.

Проверка после правки:
```bash
grep -n "Count('modules__blocks'" lesson/views.py
grep -n "Count('blocks'" lesson/views.py
```

В выводе **все** `Count` по блокам должны содержать `filter=Q(...can_be_done=True...)` или быть связаны с `moduleblockdone` (что уже требует `can_be_done=True` через доп. фильтр).

---

## Задача 2 — Thumbnail для видео (серверное решение)

Идея: при загрузке видео админом (или при `save()` существующего Video) — автоматически генерируется первый кадр и сохраняется в поле `thumbnail`. Фронт его берёт сразу, не извлекает на клиенте.

### 2.1 — Добавь поле в модель Video

Файл: `lesson/models.py`, класс `Video`.

Добавь поле:
```python
thumbnail = models.ImageField(upload_to='lessons/module/video/thumbnails/', null=True, blank=True)
```

### 2.2 — Сигнал для автогенерации при save

Создай новый файл: `lesson/signals.py`:

```python
import os
import tempfile
import subprocess
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files import File

from .models import Video


@receiver(post_save, sender=Video)
def generate_thumbnail(sender, instance, created, **kwargs):
    """Генерирует первый кадр видео через ffmpeg при первом сохранении (или если thumbnail пуст)."""
    if instance.thumbnail:
        return  # уже есть, не пересоздаём
    if not instance.file:
        return  # нет файла видео — нечего делать

    try:
        video_path = instance.file.path
    except (ValueError, NotImplementedError):
        return  # файл ещё не сохранён (например при FileField без пути)

    if not os.path.exists(video_path):
        return

    # генерируем в tempfile, потом прикрепляем к модели
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [
                'ffmpeg',
                '-y',  # overwrite
                '-i', video_path,
                '-ss', '00:00:00.5',
                '-vframes', '1',
                '-q:v', '3',
                tmp_path,
            ],
            capture_output=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f'[thumbnail] ffmpeg failed for video {instance.id}: {result.stderr.decode()[:200]}')
            return

        with open(tmp_path, 'rb') as f:
            filename = f'video_{instance.id}_thumb.jpg'
            # save=False чтобы избежать бесконечной рекурсии с post_save
            instance.thumbnail.save(filename, File(f), save=False)
            Video.objects.filter(pk=instance.pk).update(thumbnail=instance.thumbnail.name)
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f'[thumbnail] error for video {instance.id}: {e}')
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
```

### 2.3 — Подключи сигнал

Файл: `lesson/apps.py`. Найди класс `LessonConfig`, добавь `ready()`:

```python
from django.apps import AppConfig


class LessonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lesson'

    def ready(self):
        from . import signals  # noqa: F401
```

### 2.4 — Установка ffmpeg в контейнер

Файл: `Dockerfile` (в корне `ucanspeack_api-master/`). В команду `apt-get install` добавь `ffmpeg`:

Было:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
```

Стало:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

### 2.5 — Сериализатор

Файл: `lesson/serializers.py`. Найди `VideoSerializer`. Добавь `thumbnail` в `fields` (или `Meta.fields` если это ModelSerializer).

Если там `fields = '__all__'` — ничего не надо. Если явный список — добавь туда `'thumbnail'`.

### 2.6 — Management command для генерации thumbnail для уже существующих видео

Создай файл: `lesson/management/commands/generate_video_thumbnails.py` (создай папки `management/commands/` если их нет, в каждой добавь пустой `__init__.py`).

```python
from django.core.management.base import BaseCommand
from lesson.models import Video
from lesson.signals import generate_thumbnail


class Command(BaseCommand):
    help = 'Генерирует thumbnail для всех видео где его ещё нет'

    def handle(self, *args, **options):
        videos_without_thumb = Video.objects.filter(thumbnail__isnull=True) | Video.objects.filter(thumbnail='')
        total = videos_without_thumb.count()
        self.stdout.write(f'Видео без thumbnail: {total}')

        for i, video in enumerate(videos_without_thumb, 1):
            self.stdout.write(f'[{i}/{total}] Обработка video id={video.id}...')
            generate_thumbnail(sender=Video, instance=video, created=False)

        self.stdout.write(self.style.SUCCESS(f'Готово. Обработано: {total}'))
```

Потом Александр запустит вручную:
```bash
docker compose exec backend python manage.py generate_video_thumbnails
```

Для всех 300+ видео это займёт ~30-60 минут. Не страшно, фоновая задача.

---

## Задача 3 — Redis cache для тяжёлых view

Redis уже в стеке (есть в requirements). Нужно: настроить как cache backend + подключить `@cache_page` на `CourseViewSet.list()` и `LevelViewSet.list()` с инвалидацией при изменении прогресса.

### 3.1 — Redis в settings

Файл: `ucanspeack_api/settings.py`. В конец добавь:

```python
# ---- Redis Cache ----
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'TIMEOUT': 300,  # 5 минут по умолчанию
        'KEY_PREFIX': 'ucanspeak',
    }
}
```

### 3.2 — Redis в docker-compose

Файл: `docker-compose.yml` (в корне проекта, уровнем выше `ucanspeack_api-master`). 

Добавь новый сервис и подключи backend к нему:

```yaml
services:
  # ... существующие сервисы (backend, frontend, nginx) оставь как есть ...

  redis:
    image: redis:7-alpine
    container_name: ucanspeak_redis
    restart: unless-stopped
    command: redis-server --save 60 1 --loglevel warning
    volumes:
      - ucanspeak_redis_data:/data
    networks:
      - ucanspeak_net
    expose:
      - "6379"

volumes:
  ucanspeak_redis_data:
```

В сервисе `backend` в блоке `env_file` или через `environment` добавь:
```yaml
    environment:
      REDIS_HOST: redis
      REDIS_PORT: "6379"
      REDIS_DB: "0"
    depends_on:
      - redis
```

### 3.3 — Кеширование на уровне queryset, не view

`@cache_page` не подходит — у нас юзер-специфичный контент (прогресс). Вместо этого — кеш **сырых данных из БД** в методе ViewSet, с инвалидацией при `toggle_block`.

В `lesson/views.py` **в начале** импорты:
```python
from django.core.cache import cache
```

В `LessonViewSet.toggle_block` в самом конце (перед `return Response(...)`) добавь инвалидацию:

```python
# Инвалидация кеша прогресса для этого юзера
cache.delete_many([
    f'user_{user.id}_courses',
    f'user_{user.id}_levels',
])
```

В `CourseViewSet.get_queryset()` (первая строка после проверки аутентификации):
```python
if user.is_authenticated:
    cache_key = f'user_{user.id}_courses'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # ... существующий код получения courses ...

    cache.set(cache_key, courses, timeout=300)
    return courses
```

**Важно:** кешировать можно queryset только если он уже вычислен. Если это ленивый QuerySet — кеш не сработает как нужно. В нашем случае возвращаемое значение всё равно сериализуется DRF'ом в момент использования — поэтому перед кешированием преобразуй в список: `courses = list(courses)`. А в `CourseViewSet.get_queryset()` замени `return courses` на:

```python
# материализуем для кеширования
courses_list = list(courses)
cache.set(cache_key, courses_list, timeout=300)
return courses_list
```

**Аналогично для `LevelViewSet`**:
```python
if user.is_authenticated:
    cache_key = f'user_{user.id}_levels'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    # ... существующий код ...
    levels_list = list(levels)
    cache.set(cache_key, levels_list, timeout=300)
    return levels_list
```

**Note:** Drf не умеет из коробки работать с кешированным списком для ViewSet с lookup. Это только для `list()` action. Для `retrieve()` кеш не используется (редко вызывается, детальный запрос).

**Если Александру это покажется сложным** — можно упростить: просто кешировать **сериализованный ответ** через middleware. Но это требует `DummyCache` для админ-части. Пока сделаем queryset-кеш как выше.

---

## Задача 4 — Gunicorn воркеры

Файл: `ucanspeack_api-master/Dockerfile`. Найди CMD:

Было:
```dockerfile
CMD ["gunicorn", "ucanspeack_api.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

Стало:
```dockerfile
CMD ["gunicorn", "ucanspeack_api.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "9", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "100", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

Что добавилось:
- `--workers 9` — по формуле `(2 * CPU) + 1` для 4 ядер (у сервера fornex 4 CPU)
- `--max-requests 1000 --max-requests-jitter 100` — после 1000 (±100) запросов воркер рестартится (защита от утечек памяти)
- `--keep-alive 5` — keep-alive соединения 5 секунд

---

## Задача 5 — Gzip в nginx

Файл: `nginx/conf.d/ucanspeak.conf` (в корне проекта).

В **самый верх** server-блока (после `listen 443 ssl;` и `server_name`) добавь:

```nginx
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 5;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/x-javascript
        application/json
        application/xml
        application/rss+xml
        application/atom+xml
        image/svg+xml
        font/woff
        font/woff2;
```

Это сжимает все ответы кроме бинарных (видео, картинки). JSON от API сжимается в ~5-10 раз, статика HTML/CSS/JS — в ~3-5 раз.

---

## Задача 6 — Создать файл с инструкцией для Александра

Создай файл в корне проекта: `DEPLOY_1_8_BACKEND.md`:

```markdown
# Деплой S1.8 Backend — что применять на сервере №2

## 1. Закоммитить и запушить локально
git add -A
git commit -m "S1.8 backend: progress fix, thumbnails, redis cache, gzip, workers"
git push origin main

## 2. На сервере №2
ssh root@89.127.197.8
cd /root/ucanspeak
git pull

## 3. Создать миграцию для Video.thumbnail
# Локально сначала (чтобы попала в git):
docker compose exec backend python manage.py makemigrations lesson

# Скопировать новый файл миграции на хост:
docker compose cp backend:/app/lesson/migrations /root/ucanspeak/ucanspeack_api-master/lesson/
git add ucanspeack_api-master/lesson/migrations/
git commit -m "migration: video thumbnail"
git push

## 4. Пересобрать и перезапустить
docker compose build backend
docker compose up -d backend redis
docker compose exec backend python manage.py migrate

## 5. Перезагрузить nginx
docker compose restart nginx

## 6. Сгенерировать thumbnails для существующих видео (фоновая задача)
screen -S gen_thumbs
docker compose exec backend python manage.py generate_video_thumbnails
# Ctrl+A D чтоб выйти из screen

## 7. Проверка
curl -I https://new.ucanspeak.ru
# смотреть на Content-Encoding: gzip

docker compose logs backend --tail 30
# видим "Listening at: http://0.0.0.0:8000 (1)" и 9 воркеров
```

---

## Финальная сводка

Выведи:
1. Список изменённых файлов:
   - `lesson/views.py` (7 фиксов Count)
   - `lesson/models.py` (поле thumbnail)
   - `lesson/signals.py` (новый)
   - `lesson/apps.py` (ready method)
   - `lesson/serializers.py` (thumbnail в VideoSerializer)
   - `lesson/management/commands/generate_video_thumbnails.py` (новый)
   - `ucanspeack_api/settings.py` (Redis CACHES)
   - `Dockerfile` (ffmpeg, воркеры)
   - `docker-compose.yml` (redis сервис)
   - `nginx/conf.d/ucanspeak.conf` (gzip)
   - `DEPLOY_1_8_BACKEND.md` (новый)

2. Предупреждение Александру:
   - Миграция Video.thumbnail должна быть сгенерирована через `makemigrations lesson` локально или в контейнере, потом залить в git
   - Генерация thumbnails для существующих видео — через management command, долго (~30-60 мин для 300+ видео)
   - Redis как новый контейнер — при первом запуске будет пустой, прогрев займёт первые несколько запросов

3. Чего мы НЕ сделали в этой сессии (пойдёт в следующих):
   - Фронт: цвет сердечка в LikeBtn.vue
   - Фронт: вёрстка DictionaryItem
   - Фронт: «уровни» вместо «уроков» на тренажёре
   - Фронт: язык на поиске по language detect
   - Фронт: страница Прогресса переделана
   - Фронт: страница Профиля
   - Фронт: использование thumbnail в VideoWithPreview вместо canvas-генерации

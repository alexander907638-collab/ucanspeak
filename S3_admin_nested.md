# Сессия 3 — Админка: nested inlines + drag-and-drop, фикс багов, превью видео

Контекст: S1 + S1.5 + S2 уже выполнены. Теперь доводим до ума Django admin.

Все пути — от родительской папки:
- `ucanspeack_api-master/` — Django бэк
- `ucanspeak_front-master/` — фронт (в этой сессии не трогаем)

Цели:
- Поставить `django-nested-admin` — он одновременно даёт nested inlines (вложенные несколько уровней) И drag-and-drop через `sortable_field_name`. Это закрывает обе боли админа одним пакетом, без `django-admin-sortable2`.
- Спинить версии в `requirements.txt`
- Перевести админки на nested-admin: открыв страницу урока админ видит модули → блоки → видео+фразы и элементы — всё в одном экране, всё сортируемо мышкой
- Починить сломанные админки: `VideoAdmin.list_display` падает с FieldError, дубль имени `LessonItemFavoriteItemAdmin` на Tariff
- Превью первого кадра видео + счётчики дочерних объектов
- Валидация таймкодов фраз (формат `HH.MM.SS`, проверка start < end)

Что НЕ делаем в этой сессии:
- НЕ трогаем `Module.save()` — там парсится `index` (название модуля типа "1", "A1") в `sorting`. Логику оставляем как есть, drag-and-drop работает поверх через `sortable_field_name="sorting"`. Если `sorting` для модуля = NULL (когда index нечисловой) — этот модуль будет отсортирован неопределённо, drag будет работать только для модулей с числовым sorting. Это намеренный компромисс.
- НЕ удаляем мёртвые `inlines = [...]` строки внутри inline-классов, потому что после перехода на nested-admin они оживают (это и есть nested inlines).

Выполни 5 задач последовательно. После каждой — короткий отчёт. В конце — финальная сводка с инструкциями по миграциям и установке зависимостей.

---

## Задача 1 — спинить requirements.txt + добавить django-nested-admin

Файл: `ucanspeack_api-master/requirements.txt`.

Сейчас все зависимости без версий — это рулетка при `pip install` на новой машине.

**Сделай НЕ так:** не выдумывай версии сам. Открой текущее окружение проекта (где уже работает приложение) и выполни:
```
pip freeze
```

Из вывода `pip freeze` возьми реальные версии всех пакетов которые сейчас перечислены в requirements.txt. Перепиши `requirements.txt`, заменив каждую строку без версии на строку с реальной версией из `pip freeze`.

Пример: если в `requirements.txt` строка `djangorestframework`, а `pip freeze` показывает `djangorestframework==3.16.1` — пишешь `djangorestframework==3.16.1`.

**Если** ты НЕ можешь запустить `pip freeze` (не активировано venv, нет доступа к окружению):
- Не выдумывай версии. Вместо этого выведи в финальный отчёт сообщение для Александра: «Не могу спинить версии — нужен `pip freeze` из активного окружения. Александр должен сделать это сам и переписать requirements.txt».
- Только добавь новую строку в конце файла:
  ```
  django-nested-admin==4.1.6
  ```

**Если** `pip freeze` доступен:
- Спинь все строки
- Добавь в конец `django-nested-admin==4.1.6`

Не выполняй сам `pip install` — Александр сделает после ревью.

---

## Задача 2 — подключить django-nested-admin

### 2a. settings

Файл: `ucanspeack_api-master/ucanspeack_api/settings.py`.

В `INSTALLED_APPS` добавь `'nested_admin',`. Положение: после остальных third-party (`'corsheaders'`, `'colorfield'`, `'django_cleanup'`, `'django_ckeditor_5'`), перед локальными приложениями (`'user.apps.UserConfig'`).

### 2b. URL

Файл: `ucanspeack_api-master/ucanspeack_api/urls.py`.

Добавь в `urlpatterns` (рядом с другими `path`):
```python
path('_nested_admin/', include('nested_admin.urls')),
```
(этот путь нужен только если используется django-grappelli, но безопасно добавить заранее — не мешает)

### 2c. Поля order для drag-and-drop

`django-nested-admin` использует `sortable_field_name = "..."` — указывает поле для сортировки. Поле должно существовать на модели и быть числовым.

Проверь модели:

**`ucanspeack_api-master/lesson/models.py`:**

Поля порядка которые ЕСТЬ:
- `Level.order_num` — есть
- `Lesson.order_num` — есть
- `Module.sorting` — есть (но иногда NULL)
- `ModuleBlock.sorting` — есть
- `LessonItem.order_num` — есть
- `DictionaryGroup.order` — есть
- `OrthographyItem.order` — есть

Поля которых НЕТ — добавь:
- `Phrase` — добавь поле `order = models.IntegerField(default=0, verbose_name="Порядок")`. **Это решает баг #1 пользователя «фразы перепутались».** В `Meta` замени `ordering = ['id']` на `ordering = ['order', 'id']`.
- `Watermark` — добавь `order = models.IntegerField(default=0, verbose_name="Порядок")`. Добавь `class Meta: ordering = ['order']` (сейчас Meta нет).
- `Video` — добавь `order = models.IntegerField(default=0, verbose_name="Порядок")`. Добавь `class Meta: ordering = ['order']`.
- `DictionaryItem` — добавь `order = models.IntegerField(default=0, verbose_name="Порядок")`. В `Meta` добавь `ordering = ['order', 'id']` (сейчас в Meta только indexes).

**`ucanspeack_api-master/train/models.py`:**

- `Course` — добавь `order = models.IntegerField(default=0)` + `Meta: ordering = ['order']`.
- `Topic.order` — есть, но `null=True, blank=True`. Замени на `order = models.IntegerField(default=0)`.
- `AudioFile.order` — это `CharField`. **Не меняй тип** (могут быть нечисловые значения у клиента в БД), вместо этого добавь рядом `order_num = models.IntegerField(default=0, verbose_name="Порядок ПП")`. В `Meta.ordering` замени `['order']` на `['order_num']`.
- `Phrase.order` — есть `IntegerField(blank=True, null=True)`. Замени на `order = models.IntegerField(default=0)`.

---

## Задача 3 — переписать lesson/admin.py на nested-admin

Файл: `ucanspeack_api-master/lesson/admin.py`.

Это большой файл. Перепиши его целиком так:

```python
import nested_admin
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from lesson.models import (
    Course, Level, Lesson, Module, ModuleBlock, Video, Phrase, Watermark,
    LessonItem, DictionaryGroup, DictionaryItem, OrthographyItem,
    ModuleBlockDone, LessonDone, DictionaryItemFavorite, LessonItemFavoriteItem,
    Tariff, TariffItem,
)


# ---- Inlines (от самого глубокого к верхнему) ----

class PhraseInline(nested_admin.NestedTabularInline):
    model = Phrase
    extra = 0
    sortable_field_name = "order"
    fields = ("order", "start_time", "end_time", "text_en", "text_ru", "file")
    verbose_name = "Фраза"
    verbose_name_plural = "Фразы"


class WatermarkInline(nested_admin.NestedTabularInline):
    model = Watermark
    extra = 0
    sortable_field_name = "order"
    fields = ("order", "start_time", "end_time", "text")
    verbose_name = "Watermark"
    verbose_name_plural = "Watermarks"


class VideoInline(nested_admin.NestedStackedInline):
    model = Video
    extra = 0
    sortable_field_name = "order"
    fields = ("order", "video_src", "video_number", "file")
    inlines = [PhraseInline, WatermarkInline]
    verbose_name = "Видео"
    verbose_name_plural = "Видео"


class LessonItemInline(nested_admin.NestedTabularInline):
    model = LessonItem
    extra = 0
    sortable_field_name = "order_num"
    fields = ("order_num", "text_ru", "text_en", "file")
    verbose_name = "Элемент урока"
    verbose_name_plural = "Элементы урока"


class ModuleBlockInline(nested_admin.NestedStackedInline):
    model = ModuleBlock
    extra = 0
    sortable_field_name = "sorting"
    fields = ("sorting", "caption", "type3_content", "can_be_done")
    inlines = [VideoInline, LessonItemInline]
    verbose_name = "Блок модуля"
    verbose_name_plural = "Блоки модуля"


class ModuleInline(nested_admin.NestedStackedInline):
    model = Module
    extra = 0
    sortable_field_name = "sorting"
    fields = ("index", "title", "sorting")
    inlines = [ModuleBlockInline]
    verbose_name = "Модуль"
    verbose_name_plural = "Модули"


class DictionaryItemInline(nested_admin.NestedTabularInline):
    model = DictionaryItem
    extra = 0
    sortable_field_name = "order"
    fields = ("order", "text_ru", "text_en", "file")
    verbose_name = "Слово"
    verbose_name_plural = "Слова"


class DictionaryGroupInline(nested_admin.NestedStackedInline):
    model = DictionaryGroup
    extra = 0
    sortable_field_name = "order"
    fields = ("order", "title", "module")
    inlines = [DictionaryItemInline]
    verbose_name = "Группа словаря"
    verbose_name_plural = "Группы словаря"


class OrthographyItemInline(nested_admin.NestedTabularInline):
    model = OrthographyItem
    extra = 0
    sortable_field_name = "order"
    fields = ("order", "ru_text", "en_text")
    verbose_name = "Задание орфографии"
    verbose_name_plural = "Задания орфографии"


class LessonInline(nested_admin.NestedStackedInline):
    model = Lesson
    extra = 0
    sortable_field_name = "order_num"
    fields = ("order_num", "title", "slug", "url", "file", "is_common", "is_free")
    inlines = [ModuleInline, DictionaryGroupInline, OrthographyItemInline]
    verbose_name = "Урок"
    verbose_name_plural = "Уроки"


class LevelInline(nested_admin.NestedStackedInline):
    model = Level
    extra = 0
    sortable_field_name = "order_num"
    fields = ("order_num", "title", "slug", "description", "icon")
    inlines = [LessonInline]
    verbose_name = "Уровень"
    verbose_name_plural = "Уровни"


class TariffItemInline(admin.TabularInline):
    model = TariffItem
    extra = 0


# ---- ModelAdmin ----

@admin.register(Course)
class CourseAdmin(nested_admin.NestedModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title",)
    inlines = [LevelInline]


@admin.register(Level)
class LevelAdmin(nested_admin.NestedModelAdmin):
    list_display = ("order_num", "title", "course", "slug")
    search_fields = ("title", "course__title")
    list_filter = ("course",)
    ordering = ["order_num"]
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(nested_admin.NestedModelAdmin):
    list_display = ("order_num", "title", "level", "slug", "modules_count")
    search_fields = ("title", "level__title")
    list_filter = ("level",)
    ordering = ["order_num"]
    inlines = [ModuleInline, DictionaryGroupInline, OrthographyItemInline]

    @admin.display(description='Модулей')
    def modules_count(self, obj):
        return obj.modules.count()


@admin.register(Module)
class ModuleAdmin(nested_admin.NestedModelAdmin):
    list_display = ("title", "lesson_with_level", "index", "sorting")
    search_fields = ("title", "lesson__title", "lesson__level__title")
    list_filter = ("lesson", "lesson__level")
    ordering = ["sorting"]
    inlines = [ModuleBlockInline]

    @admin.display(description='Урок (Уровень)', ordering='lesson__title')
    def lesson_with_level(self, obj):
        if not obj.lesson:
            return "-"
        lesson_url = reverse('admin:lesson_lesson_change', args=[obj.lesson.id])
        lesson_html = format_html('<a href="{}">{}</a>', lesson_url, obj.lesson.title)

        if obj.lesson.level:
            level_url = reverse('admin:lesson_level_change', args=[obj.lesson.level.id])
            level_html = format_html('<a href="{}">{}</a>', level_url, obj.lesson.level.title)
        else:
            level_html = "Нет уровня"

        return format_html('{}<br><small>Уровень: {}</small>', lesson_html, level_html)


@admin.register(ModuleBlock)
class ModuleBlockAdmin(nested_admin.NestedModelAdmin):
    list_display = ("id", "module", "sorting", "caption_preview", "lesson_info")
    list_filter = ("module__lesson", "module")
    autocomplete_fields = ["module"]
    ordering = ["sorting"]
    inlines = [VideoInline, LessonItemInline]
    search_fields = (
        "caption",
        "module__title",
        "module__lesson__title",
        "module__lesson__level__title",
        "module__lesson__level__course__title",
    )

    @admin.display(description='Превью текста')
    def caption_preview(self, obj):
        if obj.caption:
            text = str(obj.caption)
            return text[:100] + "..." if len(text) > 100 else text
        return "-"

    @admin.display(description='Урок → Модуль')
    def lesson_info(self, obj):
        if obj.module and obj.module.lesson:
            return f"{obj.module.lesson.title} → {obj.module.title}"
        return "-"


@admin.register(Video)
class VideoAdmin(nested_admin.NestedModelAdmin):
    list_display = ("id", "video_number", "lesson_title", "phrases_count", "video_preview")
    search_fields = ("video_number",)
    ordering = ["order"]
    inlines = [PhraseInline, WatermarkInline]
    readonly_fields = ("site_link",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _phrases_count=Count('phrases', distinct=True),
            _watermarks_count=Count('watermarks', distinct=True),
        )

    @admin.display(description='Урок', ordering='block__module__lesson__title')
    def lesson_title(self, obj):
        if obj.block and obj.block.module and obj.block.module.lesson:
            return obj.block.module.lesson.title
        return "-"

    @admin.display(description='Фразы / WM')
    def phrases_count(self, obj):
        p = getattr(obj, '_phrases_count', '?')
        w = getattr(obj, '_watermarks_count', '?')
        return f"{p} / {w}"

    @admin.display(description='Превью')
    def video_preview(self, obj):
        if obj.file:
            return format_html(
                '<video src="{}" width="120" height="80" preload="metadata" '
                'style="object-fit:cover;border-radius:4px;" muted></video>',
                obj.file.url
            )
        return "-"

    @admin.display(description='Ссылка на сайт')
    def site_link(self, obj):
        if obj.block and obj.block.module and obj.block.module.lesson:
            lesson = obj.block.module.lesson
            if lesson.level and lesson.level.course:
                url = (
                    f"/courses/{lesson.level.course.slug}/{lesson.level.slug}/"
                    f"{lesson.slug}?m_id={obj.block.module.id}"
                )
                return format_html(
                    '<a href="{}" target="_blank">Открыть урок на сайте</a>', url
                )
        return "-"


@admin.register(Phrase)
class PhraseAdmin(nested_admin.NestedModelAdmin):
    list_display = ("text_en", "text_ru", "video", "order")
    search_fields = ("text_en", "text_ru")
    list_filter = ("video",)
    ordering = ["video", "order"]


@admin.register(DictionaryGroup)
class DictionaryGroupAdmin(nested_admin.NestedModelAdmin):
    list_display = ("order", "title", "lesson", "module_info")
    search_fields = ("title", "lesson__title")
    list_filter = ("lesson",)
    ordering = ["-order", "id"]
    autocomplete_fields = ['module']
    inlines = [DictionaryItemInline]

    @admin.display(description='Модуль/Блок')
    def module_info(self, obj):
        if obj.module:
            return f"{obj.module.lesson.title} → {obj.module.title}"
        return "-"


@admin.register(ModuleBlockDone)
class ModuleBlockDoneAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(LessonDone)
class LessonDoneAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(DictionaryItemFavorite)
class DictionaryItemFavoriteAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(LessonItemFavoriteItem)
class LessonItemFavoriteItemAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ("order", 'price', 'price_text')
    inlines = [TariffItemInline]
```

Что было исправлено по сравнению с оригиналом:
- Все админки и inline'ы используются классы из `nested_admin` (`NestedModelAdmin`, `NestedStackedInline`, `NestedTabularInline`)
- Везде указано `sortable_field_name` — drag-and-drop работает на каждом inline
- Открывая урок (`/admin/lesson/lesson/<id>/change/`) админ видит **вложенно**: модули → блоки → видео → фразы (4 уровня)
- `VideoAdmin.list_display` — поле `block__module__lesson__title` заменено на метод `lesson_title` (раньше падало с FieldError)
- Добавлено превью первого кадра видео (через тег `<video preload="metadata">`)
- Добавлен счётчик фраз/watermark в list_display
- Дубль `LessonItemFavoriteItemAdmin` на `Tariff` исправлен: тарифная админка теперь `TariffAdmin`
- Добавлены `ordering` где их не было

---

## Задача 4 — train/admin.py на nested-admin

Файл: `ucanspeack_api-master/train/admin.py`.

Перепиши целиком:

```python
import nested_admin
from django.contrib import admin

from .models import (
    Course, Level, Topic, AudioFile, Phrase,
    PhraseFavorite, TopicDone, LevelDone,
)


class AudioFileInline(nested_admin.NestedTabularInline):
    model = AudioFile
    extra = 0
    sortable_field_name = "order_num"
    fields = ("order_num", "name", "slug", "mp3", "file", "description")


class PhraseInline(nested_admin.NestedTabularInline):
    model = Phrase
    extra = 0
    sortable_field_name = "order"
    fields = ("order", "text_ru", "text_en", "sound", "file")


class TopicInline(nested_admin.NestedStackedInline):
    model = Topic
    extra = 0
    sortable_field_name = "order"
    fields = ("order", "name", "slug", "description", "url", "is_common")
    inlines = [AudioFileInline, PhraseInline]


class LevelInline(nested_admin.NestedStackedInline):
    model = Level
    extra = 0
    sortable_field_name = "order_num"
    fields = ("order_num", "name", "slug", "description", "url", "icon")
    inlines = [TopicInline]


@admin.register(Course)
class CourseAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "slug", "order")
    search_fields = ("name",)
    ordering = ["order"]
    inlines = [LevelInline]


@admin.register(Level)
class LevelAdmin(nested_admin.NestedModelAdmin):
    list_display = ("order_num", "name", "course", "order")
    search_fields = ("name", "course__name")
    list_filter = ("course",)
    ordering = ["order_num"]
    inlines = [TopicInline]


@admin.register(Topic)
class TopicAdmin(nested_admin.NestedModelAdmin):
    list_display = ("name", "level", "order")
    search_fields = ("name", "level__name")
    list_filter = ("level",)
    ordering = ["order"]
    inlines = [AudioFileInline, PhraseInline]


@admin.register(AudioFile)
class AudioFileAdmin(admin.ModelAdmin):
    list_display = ("name", "topic", "order_num")
    search_fields = ("name", "topic__name")
    list_filter = ("topic",)
    ordering = ["order_num"]


@admin.register(Phrase)
class PhraseAdmin(admin.ModelAdmin):
    list_display = ("text_en", "text_ru", "topic", "order")
    search_fields = ("text_en", "text_ru")
    list_filter = ("topic",)
    ordering = ["order"]


admin.site.register(PhraseFavorite)
admin.site.register(TopicDone)
admin.site.register(LevelDone)
```

---

## Задача 5 — валидация таймкодов фраз

Файл: `ucanspeack_api-master/lesson/models.py`.

Сейчас `start_time` и `end_time` — `CharField(max_length=20)` без валидации. Если оператор введёт `00:01:23` (двоеточия) — фронтовый плеер сломается тихо (фронт парсит через `split('.')`).

В начало файла, после импортов, добавь:

```python
import re
from django.core.exceptions import ValidationError


def validate_timecode(value):
    """
    Допустимые форматы: HH.MM.SS, H.M.S, опционально с миллисекундами.
    Пример: 00.01.23 или 0.1.23.500
    """
    if value is None or value == "":
        return
    pattern = re.compile(r'^\d{1,2}\.\d{1,2}\.\d{1,2}(\.\d+)?$')
    if not pattern.match(value):
        raise ValidationError(
            f"Таймкод '{value}' должен быть в формате HH.MM.SS "
            f"(с точками, не двоеточиями). Пример: 00.01.23"
        )
```

В моделях `Phrase` и `Watermark` (lesson/models.py) измени поля:
```python
start_time = models.CharField(max_length=20, null=True, blank=True, validators=[validate_timecode])
end_time = models.CharField(max_length=20, null=True, blank=True, validators=[validate_timecode])
```

В модель `Phrase` (lesson, та что про видео-фразы) добавь метод `clean()`:
```python
def clean(self):
    super().clean()
    if self.start_time and self.end_time:
        try:
            def parse(t):
                parts = t.split('.')[:3]
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            if parse(self.start_time) >= parse(self.end_time):
                raise ValidationError({
                    'end_time': 'Время конца должно быть больше времени начала'
                })
        except (ValueError, IndexError):
            pass  # validate_timecode уже отловит формат
```

`clean()` будет вызываться при сохранении из Django admin (через `ModelForm.full_clean()`).

---

## Финальная сводка

Выведи:
1. Список всех изменённых файлов
2. **Команды для Александра — выполнить вручную в виртуальном окружении:**
   ```
   cd ucanspeack_api-master
   pip install -r requirements.txt
   python manage.py makemigrations lesson train
   python manage.py migrate
   ```
   В миграции добавляется:
   - `lesson.Phrase.order` (default=0)
   - `lesson.Watermark.order` (default=0)
   - `lesson.Video.order` (default=0)
   - `lesson.DictionaryItem.order` (default=0)
   - `train.Course.order` (default=0)
   - `train.Topic.order` — изменение типа (теперь без NULL, default=0)
   - `train.AudioFile.order_num` (новое поле, default=0)
   - `train.Phrase.order` — изменение типа (без NULL, default=0)
   - валидаторы добавляются на `lesson.Phrase.start_time/end_time` и `lesson.Watermark.start_time/end_time` (это попадёт в миграцию как `AlterField`)
3. **Что произойдёт после миграции:**
   - Все существующие фразы получат `order=0`. Сортировка станет по `(order, id)` — фактически по id. Это не ухудшение (раньше тоже было по id). После миграции админ откроет нужное видео и расставит порядок мышкой через drag-and-drop.
   - Старые таймкоды с двоеточиями (если такие есть) НЕ упадут на чтении — валидатор срабатывает только при сохранении новой/изменении существующей. Чтобы их найти и поправить — отдельная команда (можно сделать в shell): `Phrase.objects.filter(start_time__contains=':').values('id', 'start_time')`.
4. **Чеклист ручной проверки:**
   - Открыть `/admin/lesson/lesson/<id>/change/` — должны появиться вложенные inline'ы 4 уровня: модули → блоки → видео → фразы. У каждой строки слева drag-handle.
   - Перетащить фразу в видео — порядок меняется визуально, после Save сохраняется.
   - Открыть `/admin/lesson/video/` — список не падает с FieldError (был баг #47), показывает превью видео и счётчик фраз.
   - Открыть `/admin/lesson/tariff/` — теперь админка тарифов работает (был баг #46 с дублем имени класса).
   - Ввести фразу с временем `00:01:23` (двоеточия) → ошибка валидации при сохранении.
   - Ввести фразу с `start_time=00.05.00` и `end_time=00.03.00` → ошибка «Время конца должно быть больше начала».
   - Тренажёр: `/admin/train/topic/<id>/change/` — фразы и аудио перетаскиваются.
   - `/admin/train/course/<id>/change/` — видна вся структура: уровень → топик → аудио+фразы.
5. Что НЕ сделано в этой сессии (для будущих):
   - Кнопки «редактировать» из урока на фронте, рассчитанные на тренажёр — Сессия 4
   - Onsite-editor видеофраз (модалка прямо на странице урока) — Сессия 5
   - Если у клиента в БД есть фразы/таймкоды с двоеточиями — отдельная команда миграции данных, обсудим отдельно

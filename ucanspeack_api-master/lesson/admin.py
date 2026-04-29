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
    fields = ("order", "video_number", "file")
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

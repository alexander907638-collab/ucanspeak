import nested_admin
from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, format_html_join

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


class DictionaryItemInline(admin.TabularInline):
    model = DictionaryItem
    extra = 0
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
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "levels_count")
    search_fields = ("title",)
    readonly_fields = ("levels_links",)

    fieldsets = (
        (None, {
            "fields": ("title", "slug"),
        }),
        ("Уровни курса", {
            "fields": ("levels_links",),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("levels")

    @admin.display(description='Уровней')
    def levels_count(self, obj):
        return obj.levels.count()

    @admin.display(description='Уровни')
    def levels_links(self, obj):
        if not obj.pk:
            return "-"
        levels = obj.levels.all().order_by("order_num")
        if not levels:
            return format_html(
                '<a href="{}?course={}" class="addlink">Добавить уровень</a>',
                reverse('admin:lesson_level_add'), obj.pk,
            )
        rows = []
        for l in levels:
            url = reverse('admin:lesson_level_change', args=[l.id])
            rows.append(format_html(
                '<li><a href="{}">{}. {}</a></li>',
                url, l.order_num or '?', l.title or '(без названия)',
            ))
        add_url = reverse('admin:lesson_level_add')
        rows.append(format_html(
            '<li style="margin-top:6px"><a href="{}?course={}" class="addlink">'
            'Добавить уровень</a></li>',
            add_url, obj.pk,
        ))
        return format_html('<ul style="padding-left:18px;margin:0">{}</ul>',
                           format_html_join('', '{}', ((r,) for r in rows)))


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("order_num", "title", "course", "slug", "lessons_count")
    search_fields = ("title", "course__title")
    list_filter = ("course",)
    ordering = ["order_num"]
    autocomplete_fields = ["course"]
    readonly_fields = ("lessons_links",)

    fieldsets = (
        (None, {
            "fields": ("order_num", "course", "title", "slug", "description", "icon"),
        }),
        ("Уроки уровня", {
            "fields": ("lessons_links",),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .select_related("course") \
            .prefetch_related("lessons")

    @admin.display(description='Уроков')
    def lessons_count(self, obj):
        return obj.lessons.count()

    @admin.display(description='Уроки')
    def lessons_links(self, obj):
        if not obj.pk:
            return "-"
        lessons = obj.lessons.all().order_by("order_num")
        if not lessons:
            return format_html(
                '<a href="{}?level={}" class="addlink">Добавить урок</a>',
                reverse('admin:lesson_lesson_add'), obj.pk,
            )
        rows = []
        for ls in lessons:
            url = reverse('admin:lesson_lesson_change', args=[ls.id])
            rows.append(format_html(
                '<li><a href="{}">{}. {}</a></li>',
                url, ls.order_num or '?', ls.title or '(без названия)',
            ))
        add_url = reverse('admin:lesson_lesson_add')
        rows.append(format_html(
            '<li style="margin-top:6px"><a href="{}?level={}" class="addlink">'
            'Добавить урок</a></li>',
            add_url, obj.pk,
        ))
        return format_html('<ul style="padding-left:18px;margin:0">{}</ul>',
                           format_html_join('', '{}', ((r,) for r in rows)))


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Облегчённая админка урока: без вложенных инлайнов модулей/словаря/орфографии.
    Связанные сущности доступны через ссылки в readonly-полях ниже и через
    свои собственные admin-разделы (Module, ModuleBlock, DictionaryGroup и т.д.).
    """
    list_display = ("order_num", "title", "level", "slug", "modules_count")
    search_fields = ("title", "level__title")
    list_filter = ("level",)
    ordering = ["order_num"]
    autocomplete_fields = ["level"]

    readonly_fields = (
        "url",
        "modules_links",
        "dictionary_groups_links",
        "orthography_items_links",
    )

    fieldsets = (
        (None, {
            "fields": (
                "order_num", "title", "slug", "level",
                "url", "file", "is_common", "is_free",
            ),
        }),
        ("Связанные сущности", {
            "fields": (
                "modules_links",
                "dictionary_groups_links",
                "orthography_items_links",
            ),
            "description": (
                "Ссылки на связанные модули, группы словаря и задания орфографии. "
                "Для редактирования откройте конкретную сущность по ссылке — "
                "она откроется на своей странице."
            ),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related("level", "level__course")
        qs = qs.prefetch_related("modules", "dictionary_groups", "orthography_items")
        return qs

    @admin.display(description='Модулей')
    def modules_count(self, obj):
        return obj.modules.count()

    @admin.display(description='Модули')
    def modules_links(self, obj):
        if not obj.pk:
            return "-"
        modules = obj.modules.all().order_by("sorting")
        if not modules:
            return format_html(
                '<a href="{}?lesson__id__exact={}" class="addlink">'
                'Добавить модуль</a>',
                reverse('admin:lesson_module_changelist'), obj.pk,
            )
        rows = []
        for m in modules:
            url = reverse('admin:lesson_module_change', args=[m.id])
            rows.append(format_html(
                '<li><a href="{}">{}. {}</a></li>',
                url, m.sorting or m.index or '?', m.title or '(без названия)',
            ))
        add_url = reverse('admin:lesson_module_add')
        rows.append(format_html(
            '<li style="margin-top:6px"><a href="{}?lesson={}" class="addlink">'
            'Добавить модуль</a></li>',
            add_url, obj.pk,
        ))
        return format_html('<ul style="padding-left:18px;margin:0">{}</ul>',
                           format_html_join('', '{}', ((r,) for r in rows)))

    @admin.display(description='Группы словаря')
    def dictionary_groups_links(self, obj):
        if not obj.pk:
            return "-"
        groups = obj.dictionary_groups.all().order_by("order")
        if not groups:
            return format_html(
                '<a href="{}?lesson__id__exact={}" class="addlink">'
                'Добавить группу словаря</a>',
                reverse('admin:lesson_dictionarygroup_changelist'), obj.pk,
            )
        rows = []
        for g in groups:
            url = reverse('admin:lesson_dictionarygroup_change', args=[g.id])
            rows.append(format_html(
                '<li><a href="{}">{}. {}</a></li>',
                url, g.order or '?', g.title or '(без названия)',
            ))
        add_url = reverse('admin:lesson_dictionarygroup_add')
        rows.append(format_html(
            '<li style="margin-top:6px"><a href="{}?lesson={}" class="addlink">'
            'Добавить группу словаря</a></li>',
            add_url, obj.pk,
        ))
        return format_html('<ul style="padding-left:18px;margin:0">{}</ul>',
                           format_html_join('', '{}', ((r,) for r in rows)))

    @admin.display(description='Задания орфографии')
    def orthography_items_links(self, obj):
        if not obj.pk:
            return "-"
        items = obj.orthography_items.all().order_by("order")
        if not items:
            return "Нет заданий"
        rows = []
        for it in items:
            rows.append(format_html(
                '<li>{}. {} → {}</li>',
                it.order or '?',
                (it.ru_text or '')[:50],
                (it.en_text or '')[:50],
            ))
        return format_html(
            '<ul style="padding-left:18px;margin:0">{}</ul>'
            '<p style="margin-top:6px;color:#666;font-size:12px">'
            'Задания орфографии редактируются через интерфейс на сайте.</p>',
            format_html_join('', '{}', ((r,) for r in rows)),
        )


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson_with_level", "index", "sorting", "blocks_count")
    search_fields = ("title", "lesson__title", "lesson__level__title")
    list_filter = ("lesson__level",)
    ordering = ["sorting"]
    autocomplete_fields = ["lesson"]
    readonly_fields = ("blocks_links",)

    fieldsets = (
        (None, {
            "fields": ("lesson", "index", "title", "sorting"),
        }),
        ("Блоки модуля", {
            "fields": ("blocks_links",),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .select_related("lesson", "lesson__level") \
            .prefetch_related("blocks")

    @admin.display(description='Блоков')
    def blocks_count(self, obj):
        return obj.blocks.count()

    @admin.display(description='Блоки модуля')
    def blocks_links(self, obj):
        if not obj.pk:
            return "-"
        blocks = obj.blocks.all().order_by("sorting")
        if not blocks:
            return format_html(
                '<a href="{}?module={}" class="addlink">Добавить блок</a>',
                reverse('admin:lesson_moduleblock_add'), obj.pk,
            )
        rows = []
        for b in blocks:
            url = reverse('admin:lesson_moduleblock_change', args=[b.id])
            caption = (str(b.caption) if b.caption else '(без названия)')[:80]
            rows.append(format_html(
                '<li><a href="{}">{}. {}</a></li>',
                url, b.sorting or '?', caption,
            ))
        add_url = reverse('admin:lesson_moduleblock_add')
        rows.append(format_html(
            '<li style="margin-top:6px"><a href="{}?module={}" class="addlink">'
            'Добавить блок</a></li>',
            add_url, obj.pk,
        ))
        return format_html('<ul style="padding-left:18px;margin:0">{}</ul>',
                           format_html_join('', '{}', ((r,) for r in rows)))

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
class DictionaryGroupAdmin(admin.ModelAdmin):
    """С инлайном слов внутри группы — это нормальная глубина."""
    list_display = ("order", "title", "lesson", "module_info", "items_count")
    search_fields = ("title", "lesson__title")
    list_filter = ("lesson__level",)
    ordering = ["-order", "id"]
    autocomplete_fields = ['module', 'lesson']
    inlines = [DictionaryItemInline]

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .select_related("lesson", "lesson__level", "module") \
            .prefetch_related("items")

    @admin.display(description='Слов')
    def items_count(self, obj):
        return obj.items.count()

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

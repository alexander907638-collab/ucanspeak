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

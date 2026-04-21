import re

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django_ckeditor_5.fields import CKEditor5Field

from django.contrib.postgres.indexes import GinIndex


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

class Course(models.Model):
    """Курс"""
    title = models.CharField(max_length=255, verbose_name="Название курса")
    slug = models.SlugField(verbose_name="Slug курса",max_length=255)
    cover = models.FileField(upload_to='lessons/course_covers/', null=True, blank=True)
    bg_color = models.CharField(max_length=20, null=True, blank=True)
    progress_bg_color = models.CharField(max_length=20, null=True, blank=True)
    progress_color = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.title


class Level(models.Model):
    """Уровень курса (Beginner, Intermediate, Advanced...)"""
    order_num = models.IntegerField('Номер ПП',default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="levels", verbose_name="Курс")
    title = models.CharField(max_length=255, verbose_name="Название уровня")
    slug = models.SlugField(verbose_name="Slug уровня",max_length=255)
    description = models.TextField(null=True, blank=True, verbose_name="Описание уровня")
    url = models.URLField(max_length=500, verbose_name="URL уровня", null=True, blank=True)
    icon = models.FileField(upload_to='lessons/level_icons/', null=True, blank=True)
    def __str__(self):
        return f"{self.course.title} → {self.title}"

    class Meta:
        ordering = ['order_num']


class Lesson(models.Model):
    """Урок внутри уровня"""
    order_num = models.IntegerField('Номер ПП', default=0)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="lessons", verbose_name="Уровень")
    title = models.CharField(max_length=255, verbose_name="Название урока")
    short_description = models.CharField(max_length=255, verbose_name="Описание урока", null=True, blank=True)
    slug = models.SlugField(verbose_name="Slug урока",max_length=255)
    url = models.URLField(max_length=500, verbose_name="URL урока", null=True, blank=True, editable=False)
    mp3 = models.URLField(null=True, blank=True, verbose_name="Аудио MP3 урока", editable=False)
    file = models.FileField(upload_to='lessons/mp3/', null=True, blank=True)
    table = models.TextField(null=True, blank=True)
    table_file = models.ImageField(upload_to='lesson/table',null=True, blank=True)
    orthography_description = models.TextField(verbose_name="Описание блока орфографии", null=True, blank=True)
    is_common = models.BooleanField('Обобщающий', default=False)
    is_free = models.BooleanField('Бесплатный', default=False)
    def __str__(self):
        return f"{self.level.title} → {self.title}"

    class Meta:
        ordering = ['order_num']
        indexes = [
            GinIndex(
                name="lesson_title_trgm",
                fields=["title"],
                opclasses=["gin_trgm_ops"],
            ),
        ]



class Module(models.Model):
    """Модуль внутри урока"""

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="modules", verbose_name="Урок")
    title = models.CharField(max_length=255, verbose_name="Название модуля")
    index = models.CharField(max_length=20, null=True, blank=True, verbose_name="Индекс модуля")
    url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL модуля")
    sorting = models.IntegerField(null=True, blank=True, verbose_name="Порядок отображения модуля")

    def __str__(self):
        return f"{self.lesson.title} → {self.title}"
    def save(self, *args, **kwargs):
        if self.index:
            try:
                # если index = "10" → sorting = 10
                self.sorting = int(self.index)
            except ValueError:
                # если index = "A1", "1.2", "01a" → None
                self.sorting = None
        else:
            self.sorting = None

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['sorting']
        indexes = [
            GinIndex(
                name="module_title_trgm",
                fields=["title"],
                opclasses=["gin_trgm_ops"],
            ),
        ]

class ModuleBlock(models.Model):
    """Блок контента внутри модуля"""
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="blocks", verbose_name="Модуль")
    sorting = models.IntegerField(null=True, blank=True, verbose_name="Сортировка блока")
    caption = CKEditor5Field(null=True, blank=True, verbose_name="Текст/описание блока",config_name='extends')
    type3_content = CKEditor5Field(blank=True, verbose_name="HTML контент блока (type3)",config_name='extends')
    #type3_content = models.JSONField(default=list, blank=True, verbose_name="HTML контент блока (type3)")
    can_be_done = models.BooleanField('Выполняемый', default=True,null=False)

    def __str__(self):
        return f"Блок {self.sorting} модуля {self.module.title}"

    class Meta:
        ordering = ['sorting']


class LessonItem(models.Model):
    """Фразы или элементы внутри блока"""
    order_num = models.IntegerField(default=0, null=True, blank=True)
    block = models.ForeignKey(ModuleBlock, on_delete=models.CASCADE,null=True, blank=True, related_name="items", verbose_name="Блок")
    text_ru = models.TextField(null=True, blank=True, verbose_name="Текст на русском")
    text_en = models.TextField(null=True, blank=True, verbose_name="Текст на английском")
    sound = models.URLField(null=True, blank=True, verbose_name="Ссылка на аудио")
    file = models.FileField(upload_to='lessons/module/mp3/', null=True, blank=True)
    def __str__(self):
        return self.text_en or self.text_ru or "Элемент урока"

    class Meta:
        ordering = ['order_num']
        indexes = [
            GinIndex(
                name="lessonitem_text_ru_trgm",
                fields=["text_ru"],
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                name="lessonitem_text_en_trgm",
                fields=["text_en"],
                opclasses=["gin_trgm_ops"],
            ),
        ]

class Video(models.Model):
    """Видео внутри блока"""
    block = models.ForeignKey(ModuleBlock, on_delete=models.CASCADE,null=True, blank=True, related_name="videos", verbose_name="Блок")
    video_src = models.URLField(verbose_name="Ссылка на видео",null=True, blank=True, editable=False)
    file = models.FileField(upload_to='lessons/module/video/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='lessons/module/video/thumbnails/', null=True, blank=True)
    video_number = models.CharField(max_length=10, blank=True, null=True)
    order = models.IntegerField(default=0, verbose_name="Порядок")
    def __str__(self):
        return self.video_number

    class Meta:
        ordering = ['order']


class Phrase(models.Model):
    """Фразы из видео"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="phrases", verbose_name="Видео")
    start_time = models.CharField(max_length=20, null=True, blank=True, verbose_name="Время начала", validators=[validate_timecode])
    end_time = models.CharField(max_length=20, null=True, blank=True, verbose_name="Время конца", validators=[validate_timecode])
    text_en = models.TextField(null=True, blank=True, verbose_name="Текст на английском")
    text_ru = models.TextField(null=True, blank=True, verbose_name="Текст на русском")
    sound = models.URLField(null=True, blank=True, verbose_name="Ссылка на аудио", editable=False)
    file = models.FileField(upload_to='lessons/module/video/phrase', null=True, blank=True)
    order = models.IntegerField(default=0, verbose_name="Порядок")

    def __str__(self):
        return self.text_en or self.text_ru or "Фраза видео"

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

    class Meta:
        ordering = ['order', 'id']
        indexes = [
            GinIndex(
                name="lesson_phrase_text_ru_trgm",
                fields=["text_ru"],
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                name="lesson_phrase_text_en_trgm",
                fields=["text_en"],
                opclasses=["gin_trgm_ops"],
            ),
        ]

class Watermark(models.Model):
    """Фразы из видео"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="watermarks", verbose_name="Видео")
    start_time = models.CharField(max_length=20, null=True, blank=True, verbose_name="Время начала", validators=[validate_timecode])
    end_time = models.CharField(max_length=20, null=True, blank=True, verbose_name="Время конца", validators=[validate_timecode])
    text = models.TextField(null=True, blank=True, verbose_name="Текст ")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['order']

class DictionaryGroup(models.Model):
    """Группа слов в словаре урока"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="dictionary_groups", verbose_name="Урок")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="module_dictionary_groups",
                                     verbose_name="Блок модуля", blank=True, null=True)
    title = models.CharField(max_length=255, verbose_name="Название группы")
    order = models.IntegerField(default=0, null=True)
    def __str__(self):
        return self.title
    class Meta:
        ordering = ['-order', 'id']

class DictionaryItem(models.Model):
    """Элемент словаря"""
    group = models.ForeignKey(DictionaryGroup, on_delete=models.CASCADE, related_name="items", verbose_name="Группа слов")
    text_ru = models.TextField(null=True, blank=True, verbose_name="Текст на русском")
    text_en = models.TextField(null=True, blank=True, verbose_name="Текст на английском")
    sound = models.CharField(max_length=255, null=True, blank=True, verbose_name="Ссылка на аудио")
    file = models.FileField(upload_to='lessons/dictionary/mp3', null=True, blank=True)
    order = models.IntegerField(default=0, verbose_name="Порядок")

    def __str__(self):
        return self.text_en or self.text_ru or "Элемент словаря"

    class Meta:
        ordering = ['order', 'id']
        indexes = [
            GinIndex(
                name="dict_text_ru_trgm",
                fields=["text_ru"],
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                name="dict_text_en_trgm",
                fields=["text_en"],
                opclasses=["gin_trgm_ops"],
            ),
        ]

class ModuleBlockDone(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
    module_block = models.ForeignKey('ModuleBlock',on_delete=models.CASCADE,blank=True,null=True)

class LessonDone(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
    lesson = models.ForeignKey('Lesson',on_delete=models.CASCADE,blank=True,null=True)

class DictionaryItemFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
    dictionary_item = models.ForeignKey(DictionaryItem,on_delete=models.CASCADE,blank=True,null=True)


class LessonItemFavoriteItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,blank=True,null=True)
    lesson_item = models.ForeignKey(LessonItem,on_delete=models.CASCADE,blank=True,null=True, related_name="lesson_item_favorites")


class OrthographyItem(models.Model):
    order = models.IntegerField(default=0, null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=True, null=True,
                                    related_name="orthography_items")
    ru_text = models.TextField('Русский текст', null=True, blank=False)
    en_text = models.TextField('Англ. текст', null=True, blank=False)

    def __str__(self):
        return self.ru_text

    class Meta:
        ordering = ['-order']
        indexes = [
            GinIndex(
                name="ortho_ru_trgm",
                fields=["ru_text"],
                opclasses=["gin_trgm_ops"],
            ),
            GinIndex(
                name="ortho_en_trgm",
                fields=["en_text"],
                opclasses=["gin_trgm_ops"],
            ),
        ]

class OrthographyItemDone(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    orthography_item = models.ForeignKey(OrthographyItem, on_delete=models.CASCADE, blank=True, null=True)


class Tariff(models.Model):
    order = models.IntegerField(default=0, null=True)
    is_for_school = models.BooleanField(default=False, null=False)
    is_decorated = models.BooleanField(default=False, null=False)
    badge_text = models.CharField(max_length=30, null=True, blank=True)
    price = models.IntegerField(default=0, null=True, blank=True)
    price_text = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return  f'{self.price} руб'

    class Meta:
        ordering = ['order']

class TariffItem(models.Model):
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, blank=True, null=True, related_name="tariff_items")
    text = models.TextField(null=False, blank=True)
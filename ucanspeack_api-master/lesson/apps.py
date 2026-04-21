from django.apps import AppConfig


class LessonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lesson'

    def ready(self):
        from . import signals  # noqa: F401

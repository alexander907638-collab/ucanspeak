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

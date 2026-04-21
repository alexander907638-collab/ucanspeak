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

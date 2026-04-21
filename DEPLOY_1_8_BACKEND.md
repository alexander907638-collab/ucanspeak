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

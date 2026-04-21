# Ucanspeak — запуск

## Структура
- `ucanspeack_api-master/` — Django backend
- `ucanspeak_front-master/` — Nuxt frontend
- `docker-compose.yml` — оркестрация
- `nginx/` — конфиги

## Первый запуск
1. Скопировать и заполнить env-файлы:
   cp ucanspeack_api-master/.env.example ucanspeack_api-master/.env
   cp ucanspeak_front-master/.env.example ucanspeak_front-master/.env
2. Убедиться что Postgres работает на хосте и пропускает подключения с docker-сети (см. DEPLOY.md шаг 4).
3. Создать папки для медиа и static на хосте:
   sudo mkdir -p /var/ucanspeak/media /var/ucanspeak/static
   sudo chown -R $USER:$USER /var/ucanspeak
4. Собрать и запустить:
   docker compose build
   docker compose up -d
5. Применить миграции и собрать статику:
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py collectstatic --noinput
6. Проверить:
   curl https://new.ucanspeak.ru/api/lesson/courses/

## Повседневные команды
- Логи: `docker compose logs -f backend`
- Перезапуск после правки кода: `git pull && docker compose up -d --build`
- Django shell: `docker compose exec backend python manage.py shell`
- Бэкап БД: см. DEPLOY.md

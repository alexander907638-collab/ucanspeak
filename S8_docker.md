# Сессия 8 — Docker для платформы: backend + frontend + nginx

Контекст: S1–S7 локально выполнены. Теперь заворачиваем платформу в Docker для деплоя.

Все пути — от родительской папки:
- `ucanspeack_api-master/` — Django бэк
- `ucanspeak_front-master/` — Nuxt фронт

Архитектура:
- **Postgres на хосте** (не в Docker). Контейнеры коннектятся к нему через `host.docker.internal` (через `extra_hosts`).
- **3 контейнера:** `backend` (Django + gunicorn), `frontend` (Nuxt build + node runtime), `nginx`
- **Медиа:** bind-mount с хоста `/var/ucanspeak/media` в контейнер `backend` (именно туда rclone скачает 49 ГБ из YC)
- **Внешняя сеть:** `ucanspeak_net` — заранее сделана, потом в неё вступит контейнер звонилки отдельным compose
- **Nginx:** внутри compose, слушает 80 и 443. В конфиг заранее добавлен закомментированный блок для проксирования на звонилку (раскомментируешь когда будешь её поднимать)

Выполни 5 задач последовательно.

---

## Задача 1 — Dockerfile для backend

Создай файл: `ucanspeack_api-master/Dockerfile`

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# системные зависимости: psycopg, weasyprint-less (у вас только psycopg-binary — хватит build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY . .

RUN mkdir -p /app/media /app/static

EXPOSE 8000

CMD ["gunicorn", "ucanspeack_api.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

Также создай `ucanspeack_api-master/.dockerignore`:
```
__pycache__
*.pyc
*.pyo
.git
.gitignore
.env
.venv
venv/
media/
static/
db.sqlite3
.DS_Store
*.log
```

**Важно:** `.env` исключён из образа — переменные окружения пробрасываются через `env_file` в docker-compose.

---

## Задача 2 — Dockerfile для frontend

Создай файл: `ucanspeak_front-master/Dockerfile`

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app

# Nuxt 4 build output в .output
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

ENV HOST=0.0.0.0 \
    PORT=3000 \
    NODE_ENV=production

CMD ["node", ".output/server/index.mjs"]
```

Также создай `ucanspeak_front-master/.dockerignore`:
```
node_modules
.nuxt
.output
.git
.gitignore
.env
dist
*.log
.DS_Store
```

---

## Задача 3 — docker-compose.yml в корне проекта

В **родительской папке** (там где лежат `ucanspeack_api-master/` и `ucanspeak_front-master/`) создай файл `docker-compose.yml`:

```yaml
services:
  backend:
    build:
      context: ./ucanspeack_api-master
      dockerfile: Dockerfile
    container_name: ucanspeak_backend
    restart: unless-stopped
    env_file:
      - ./ucanspeack_api-master/.env
    volumes:
      - /var/ucanspeak/media:/app/media
      - /var/ucanspeak/static:/app/static
    extra_hosts:
      - "host.docker.internal:host-gateway"
    networks:
      - ucanspeak_net
    expose:
      - "8000"

  frontend:
    build:
      context: ./ucanspeak_front-master
      dockerfile: Dockerfile
    container_name: ucanspeak_frontend
    restart: unless-stopped
    env_file:
      - ./ucanspeak_front-master/.env
    networks:
      - ucanspeak_net
    expose:
      - "3000"

  nginx:
    image: nginx:1.27-alpine
    container_name: ucanspeak_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - /var/ucanspeak/media:/var/ucanspeak/media:ro
      - /var/ucanspeak/static:/var/ucanspeak/static:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - backend
      - frontend
    networks:
      - ucanspeak_net

networks:
  ucanspeak_net:
    name: ucanspeak_net
    driver: bridge
```

Ключевые моменты:
- `extra_hosts: host.docker.internal:host-gateway` — у backend появляется DNS-имя для доступа к Postgres на хосте (`DB_HOST=host.docker.internal` в `.env`)
- media и static — общие bind-mount'ы между backend (запись) и nginx (чтение)
- nginx читает SSL-сертификаты из `/etc/letsencrypt` — это стандартное место certbot
- сеть `ucanspeak_net` — именованная, в неё потом вступит compose со звонилкой

---

## Задача 4 — nginx конфиг

Создай файл в **родительской папке**: `nginx/conf.d/ucanspeak.conf`

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

# redirect HTTP → HTTPS
server {
    listen 80;
    server_name new.ucanspeak.ru;

    # для certbot renewal
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    http2 on;
    server_name new.ucanspeak.ru;

    ssl_certificate /etc/letsencrypt/live/new.ucanspeak.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/new.ucanspeak.ru/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    client_max_body_size 500m;

    # статика Django (админка, CKEditor)
    location /static/ {
        alias /var/ucanspeak/static/;
        expires 7d;
        access_log off;
    }

    # медиа (видео, аудио, картинки)
    location /media/ {
        alias /var/ucanspeak/media/;
        expires 30d;
        access_log off;
    }

    # API бэкенда
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # Djoser
    location /auth/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django admin
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # CKEditor upload
    location /ckeditor5/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # ---- ЗАГОТОВКА для звонилки (раскомментируешь когда поднимешь её) ----
    # location /calls/ {
    #     proxy_pass http://calls_service:PORT/;
    #     proxy_http_version 1.1;
    #     proxy_set_header Upgrade $http_upgrade;
    #     proxy_set_header Connection "upgrade";
    #     proxy_set_header Host $host;
    #     proxy_set_header X-Real-IP $remote_addr;
    #     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    #     proxy_set_header X-Forwarded-Proto $scheme;
    # }
    # -------------------------------------------------------------------

    # всё остальное — фронт (Nuxt SSR/SPA)
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Задача 5 — .env.example и вспомогательные скрипты

### 5a. backend .env.example

Создай `ucanspeack_api-master/.env.example`:
```env
# Django
DEBUG=False
SECRET_KEY=<сгенерируй: python -c "import secrets; print(secrets.token_urlsafe(50))">
ALLOWED_HOSTS=new.ucanspeak.ru,localhost
CORS_ORIGIN_ALLOW_ALL=False
CORS_ALLOWED_ORIGINS=https://new.ucanspeak.ru

# Database
DB_NAME=ucanspeak
DB_USER=ucanspeak_user
DB_PASSWORD=<новый пароль, не тот что был на сервере №1>
DB_HOST=host.docker.internal
DB_PORT=5432
```

### 5b. frontend .env.example

Создай `ucanspeak_front-master/.env.example`:
```env
NUXT_PUBLIC_API_URL=https://new.ucanspeak.ru
```

### 5c. Правка settings.py

Файл: `ucanspeack_api-master/ucanspeack_api/settings.py`.

Сейчас `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, CORS, `DB_HOST` захардкожены. Нужно вытащить в env.

Замени соответствующие строки на:
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-only-change-me')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('1', 'true', 'yes', 'on')
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ORIGIN_ALLOW_ALL', 'False').lower() in ('1', 'true', 'yes', 'on')
CORS_ALLOWED_ORIGINS = [o.strip() for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]
```

И в блоке DATABASES поменяй захардкоженные `HOST`/`PORT`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'ATOMIC_REQUESTS': True
    }
}
```

Также: за доверием HTTPS-прокси добавь в конец `settings.py`:
```python
# доверяем заголовку X-Forwarded-Proto от nginx (для detected scheme https)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CSRF доверенные домены при работе за прокси
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', 'https://new.ucanspeak.ru').split(',') if o.strip()]
```

### 5d. .gitignore в корне

Создай в **родительской папке** файл `.gitignore`:
```
# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
.venv/
venv/

# Node
node_modules/
.nuxt/
.output/

# env
.env
*.env
!.env.example

# Django
db.sqlite3
staticfiles/

# Медиа — не лезет в git (60 ГБ)
media/
ucanspeack_api-master/media/

# IDE
.idea/
.vscode/
.DS_Store
*.log
```

### 5e. Команды запуска (справочно, положи в README.md в корне)

Создай в родительской папке `README.md`:
```markdown
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
```

---

## Финальная сводка

Выведи:
1. Список созданных и изменённых файлов
2. Проверка что в `settings.py` больше не осталось хардкодов `DEBUG=True`, `SECRET_KEY='django-insecure-...'`, `ALLOWED_HOSTS=['*']`, `CORS_ORIGIN_ALLOW_ALL=True`, `HOST='127.0.0.1'`. Если что-то осталось — поправь.
3. **Что делать Александру дальше** — следовать инструкции в `DEPLOY.md` (отдельный файл, я его выдаю сразу после этой сессии)

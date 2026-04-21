# DEPLOY.md — Пошаговый деплой Ucanspeak на сервер №2

## Твои данные (замени перед выполнением)

- **Сервер №2:** `89.127.197.8`
- **Домен:** `new.ucanspeak.ru` (уже направлен на сервер №2 в DNS)
- **YC бакет:** `ucanspeak-backup` (rclone профиль `ycloud:` уже настроен на сервере)
- **Плейсхолдеры:** `<GITHUB_USER>`, `<NEW_DB_PASSWORD>`, `<NEW_DJANGO_SECRET>` — ты заменишь

---

## Часть 1 — Локально: пушим проект в GitHub

### 1.1 Создай новый приватный репо на GitHub

Зайди на https://github.com/new:
- Repository name: `ucanspeak`
- Private
- **НЕ** добавляй README, .gitignore, license (мы сами положим)

Получишь URL: `https://github.com/<GITHUB_USER>/ucanspeak.git`

### 1.2 Локально — один репо на всю родительскую папку

На твоём Windows в PowerShell:

```powershell
cd C:\Users\Legioner\projects\studio\projects\ucanspeak

# инициализация git
git init
git branch -M main

# проверь .gitignore на месте (S8 создал его в этой папке)
type .gitignore

# проверь что .env НЕ попадут в коммит
git status
# в списке НЕ должно быть: ucanspeack_api-master/.env, ucanspeak_front-master/.env
# должны быть: .env.example файлы, Dockerfile-ы, docker-compose.yml, nginx/, README.md, и весь код

# добавить всё
git add .
git commit -m "Initial: platform code with Docker setup, migration-ready"

# подключить GitHub
git remote add origin https://github.com/<GITHUB_USER>/ucanspeak.git
git push -u origin main
```

Если `git push` попросит аутентификацию — нужен Personal Access Token (не пароль от аккаунта):
- GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate new token (classic)
- Scopes: `repo` (все галочки внутри)
- Копируешь токен, вставляешь вместо пароля когда git попросит

Если вылетел с ошибкой типа `files over 100MB` — в репозитории попал большой файл (скорее всего медиа или venv). Проверь:
```powershell
git rm --cached -r ucanspeack_api-master/media
git rm --cached -r ucanspeack_api-master/venv
git rm --cached -r ucanspeak_front-master/node_modules
git commit -m "Remove large dirs from tracking"
git push
```

---

## Часть 2 — На сервере №2: клонируем и подготавливаем

Подключайся по ssh: `ssh root@89.127.197.8`

### 2.1 Проверь что всё установлено

```bash
docker --version      # должен быть 20+
docker compose version  # должен быть v2+ (БЕЗ дефиса в команде)
psql --version
nginx -v
rclone version
git --version
```

Если `docker compose` не работает (Ubuntu 24) — установи плагин:
```bash
sudo apt install -y docker-compose-plugin
```

### 2.2 Создай папки для медиа и static на хосте

```bash
sudo mkdir -p /var/ucanspeak/media
sudo mkdir -p /var/ucanspeak/static
sudo chown -R $USER:$USER /var/ucanspeak
ls -la /var/ucanspeak/
```

### 2.3 Клонируй репозиторий

```bash
cd /root
git clone https://github.com/<GITHUB_USER>/ucanspeak.git
cd ucanspeak
ls
```

Должен увидеть: `ucanspeack_api-master/`, `ucanspeak_front-master/`, `docker-compose.yml`, `nginx/`, `README.md`.

Если репо приватный — `git clone` попросит креды. Используй GitHub username + Personal Access Token (тот же что при push).

---

## Часть 3 — Postgres на хосте

### 3.1 Настроить Postgres принимать подключения из Docker

По умолчанию Postgres слушает только `127.0.0.1`. Docker-контейнеры приходят с адреса docker-сети (172.17.x.x или типа того). Надо открыть Postgres для этой сети.

Сначала найди актуальный путь к конфигам:
```bash
sudo -u postgres psql -c "SHOW config_file;"
sudo -u postgres psql -c "SHOW hba_file;"
```

Обычно это `/etc/postgresql/16/main/postgresql.conf` и `.../pg_hba.conf`.

**Правка `postgresql.conf`** — разрешаем слушать на всех интерфейсах:
```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```
Найди строку `listen_addresses` (может быть закомментирована) и поставь:
```
listen_addresses = '*'
```

**Правка `pg_hba.conf`** — разрешаем подключения из docker-сети:
```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```
В конец файла добавь:
```
# Docker bridge network
host    all    all    172.17.0.0/16    md5
host    all    all    172.18.0.0/16    md5
host    all    all    172.19.0.0/16    md5
host    all    all    172.20.0.0/16    md5
```
(несколько диапазонов потому что Docker создаёт разные сети и заранее не знаем какой достанется `ucanspeak_net`)

Перезагрузи Postgres:
```bash
sudo systemctl restart postgresql
sudo systemctl status postgresql  # убедись что Active: running
```

### 3.2 Создай БД и пользователя

```bash
sudo -u postgres psql
```

В psql:
```sql
CREATE DATABASE ucanspeak;
CREATE USER ucanspeak_user WITH PASSWORD '<NEW_DB_PASSWORD>';
GRANT ALL PRIVILEGES ON DATABASE ucanspeak TO ucanspeak_user;
ALTER DATABASE ucanspeak OWNER TO ucanspeak_user;

-- для Postgres 15+ обязательно:
\c ucanspeak
GRANT ALL ON SCHEMA public TO ucanspeak_user;

\q
```

**⚠️ `<NEW_DB_PASSWORD>`** — придумай НОВЫЙ, не тот что был на сервере №1 (`l2ASD3sdf&*!!` со спецсимволами). Возьми что-то **без `&`, `*`, `!`, `$`** — просто буквы+цифры+может дефис/подчёркивание. Например: `Xk9pM2nQ7wL4vT8r`. Запиши в блокнот.

### 3.3 Проверь что подключение работает с хоста

```bash
PGPASSWORD='<NEW_DB_PASSWORD>' psql -h 127.0.0.1 -U ucanspeak_user -d ucanspeak -c "SELECT 1;"
```

Должно вывести `?column?` и `1`. Если ошибка — разбирайся с pg_hba.conf.

---

## Часть 4 — Восстанавливаем БД из YC

### 4.1 Скачай дамп с YC

```bash
mkdir -p /root/restore
cd /root/restore
rclone copy ycloud:ucanspeak-backup/db/ . -P
ls -lh
```

Должен появиться файл `ucanspeak_20260421_1050.dump` (59 МБ).

### 4.2 Восстанови дамп в новую БД

```bash
PGPASSWORD='<NEW_DB_PASSWORD>' pg_restore \
  -h 127.0.0.1 \
  -U ucanspeak_user \
  -d ucanspeak \
  --no-owner \
  --no-privileges \
  /root/restore/ucanspeak_20260421_1050.dump
```

Флаги важные:
- `--no-owner` — не пытаемся выставить старого владельца `u_can_user` (его нет на новом сервере)
- `--no-privileges` — аналогично для GRANT'ов

Возможные предупреждения:
- `WARNING: errors ignored on restore: N` — если N небольшое (до 10), это обычно про отсутствующие расширения или роли. Проверь:
  ```bash
  PGPASSWORD='<NEW_DB_PASSWORD>' psql -h 127.0.0.1 -U ucanspeak_user -d ucanspeak -c "\dt"
  ```
  Если таблицы на месте (`auth_user`, `lesson_lesson`, `train_topic` и т.д.) — всё ок, идём дальше.

### 4.3 Быстрая проверка данных

```bash
PGPASSWORD='<NEW_DB_PASSWORD>' psql -h 127.0.0.1 -U ucanspeak_user -d ucanspeak
```

В psql:
```sql
SELECT count(*) FROM user_user;
SELECT count(*) FROM lesson_lesson;
SELECT count(*) FROM train_topic;
\q
```

Если цифры ненулевые и разумные (десятки/сотни) — дамп жив.

---

## Часть 5 — Env-файлы

### 5.1 Backend .env

```bash
cd /root/ucanspeak/ucanspeack_api-master
cp .env.example .env
nano .env
```

Заполни:
```env
DEBUG=False
SECRET_KEY=<NEW_DJANGO_SECRET>
ALLOWED_HOSTS=new.ucanspeak.ru,localhost,127.0.0.1
CORS_ORIGIN_ALLOW_ALL=False
CORS_ALLOWED_ORIGINS=https://new.ucanspeak.ru
CSRF_TRUSTED_ORIGINS=https://new.ucanspeak.ru

DB_NAME=ucanspeak
DB_USER=ucanspeak_user
DB_PASSWORD=<NEW_DB_PASSWORD>
DB_HOST=host.docker.internal
DB_PORT=5432
```

**Сгенерировать `<NEW_DJANGO_SECRET>`:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

Скопируй результат в `SECRET_KEY=`.

Сохрани (`Ctrl+O`, `Enter`, `Ctrl+X`).

### 5.2 Frontend .env

```bash
cd /root/ucanspeak/ucanspeak_front-master
cp .env.example .env
nano .env
```

```env
NUXT_PUBLIC_API_URL=https://new.ucanspeak.ru
```

Сохрани.

---

## Часть 6 — SSL-сертификат через certbot

Сертификат нужен ДО старта nginx — иначе контейнер не запустится (конфиг ссылается на файлы которых нет).

### 6.1 Установить certbot

```bash
sudo apt install -y certbot
```

### 6.2 Получить сертификат в standalone-режиме

**⚠️ На сервере №2 НЕ должно быть ничего на 80 порту** в момент получения. Проверь:
```bash
sudo ss -tlnp | grep :80
```
Если что-то есть (системный nginx например) — останови: `sudo systemctl stop nginx`.

Получаем:
```bash
sudo certbot certonly --standalone -d new.ucanspeak.ru --agree-tos --register-unsafely-without-email
```

Если хочешь с email — убери `--register-unsafely-without-email` и после домена добавь `-m your@email.com`.

Проверь что сертификат появился:
```bash
sudo ls /etc/letsencrypt/live/new.ucanspeak.ru/
```
Должны быть: `cert.pem`, `chain.pem`, `fullchain.pem`, `privkey.pem`.

---

## Часть 7 — Билд и старт контейнеров

```bash
cd /root/ucanspeak

# сборка образов (первый раз долго — 3-5 минут)
docker compose build

# старт в фоне
docker compose up -d

# посмотреть логи
docker compose ps
docker compose logs -f backend
```

При первом старте смотри лог `backend` — если там есть трейсбеки, давай мне сюда.

Нажми `Ctrl+C` чтобы выйти из `logs -f` (контейнеры продолжат работать).

---

## Часть 8 — Миграции и static

Раз у нас S2 и S3 добавляли поля в БД — миграции обязательно:

```bash
docker compose exec backend python manage.py migrate
```

Должен увидеть что-то типа:
```
Applying user.0XXX_usertoken_last_used_at_and_more... OK
Applying lesson.0XXX_phrase_order_and_more... OK
Applying train.0XXX_course_order_and_more... OK
```

Если ругается на отсутствующие миграции (`No migrations to apply`) — возможно ты делал `makemigrations` локально, но не закоммитил. Проверь локально:
```powershell
cd C:\Users\Legioner\projects\studio\projects\ucanspeak
git status
```
Если увидишь файлы типа `ucanspeack_api-master/user/migrations/0XXX_....py` — закоммить, запуши, на сервере сделай `git pull`, потом снова `docker compose exec backend python manage.py migrate`.

### 8.1 Собрать static

```bash
docker compose exec backend python manage.py collectstatic --noinput
```

Увидишь что-то типа `XXX static files copied to '/app/static'`.

### 8.2 Создать суперюзера (если нужен)

В старой БД уже есть superuser'ы (восстановились из дампа). Если хочешь нового:
```bash
docker compose exec backend python manage.py createsuperuser
```

---

## Часть 9 — Медиа из YC

49 ГБ — долго, но сейчас уже должно быть долито в YC (проверь на сервере №1 что заливка закончилась, запусти `rclone size ycloud:ucanspeak-backup/media/` — цифра должна примерно совпадать с 44 ГБ).

### 9.1 Скачиваем медиа

В screen:
```bash
screen -S media_download
rclone copy ycloud:ucanspeak-backup/media /var/ucanspeak/media -P --transfers=8 --checkers=16 --stats=30s
```

Выход из screen: `Ctrl+A`, `D`.
Возврат: `screen -r media_download`.

Скорость обычно 30-80 МБ/с на скачивание из YC (быстрее чем загрузка). 45 ГБ ≈ 15-30 минут.

Можешь НЕ ждать этого шага для первой проверки платформы — видео не будет, но авторизация, админка, списки уроков, тренажёр — всё остальное будет работать. Проверяй параллельно.

---

## Часть 10 — Проверка что всё работает

### 10.1 Проверка с сервера (локально)

```bash
# backend жив?
curl http://localhost:80 -H "Host: new.ucanspeak.ru" -I
# должен ответить 301 Moved Permanently (редирект на https)

# через https
curl https://new.ucanspeak.ru/api/lesson/courses/ -k
# должен вернуть JSON со списком курсов
```

### 10.2 Проверка с твоего компа

Открой в браузере `https://new.ucanspeak.ru` — должна появиться страница логина.

Замок в адресной строке зелёный — SSL работает.

Логинься superuser'ом (логин/пароль из старой БД остались).

### 10.3 Чек-лист по всем сессиям

- [ ] Главная `/` → редирект на `/courses`
- [ ] Логин обычного юзера → попадает в `/courses`
- [ ] Регистрация нового юзера с ФИО → в админке `/admin/user/user/<id>/` ФИО заполнено (S1.5)
- [ ] В админке `/admin/user/usertoken/` — видны колонки expires_at, ip, user_agent, is_expired (S2)
- [ ] Залогиниться с двух разных браузеров тестовым юзером с `max_logins=1` → получить модалку «Превышен лимит» → кнопка «Выйти отовсюду и войти» → работает (S2)
- [ ] Открыть `/admin/lesson/lesson/<id>/change/` — вложенные inline'ы: модули → блоки → видео → фразы, drag-and-drop работает (S3)
- [ ] `/admin/lesson/video/` — видно превью видео и счётчик фраз (S3 — фикс бага)
- [ ] `/admin/lesson/tariff/` — админка тарифов открывается (S3 — фикс дубля класса)
- [ ] На странице тренажёра для суперюзера — кнопки-карандаши возле курсов, уровней, топиков, аудиофайлов (S4)
- [ ] В уроке с видео: пауза → список фраз → возле каждой карандаш, клик открывает модалку с полями ru/en/start/end (S5)
- [ ] В модалке сохранение фразы работает, обновление порядка через стрелки работает (S5)
- [ ] `/profile/favorite` — нет поля поиска, нет чекбоксов, кнопка «Очистить» работает и действует только на активную вкладку (S6)
- [ ] `/profile/pupils` → кнопка «Выйти» на ученике — реально разлогинивает ученика (S7)

### 10.4 Типичные баги и где смотреть

**500 на любой странице API:**
```bash
docker compose logs -f backend
```
Искать трейсбек. Частые причины:
- Миграции не прошли
- SECRET_KEY не установлен
- CORS не пропускает (в логах `CORS header not set`)

**502 Bad Gateway от nginx:**
- Backend или frontend упали. `docker compose ps` — статус контейнеров.
- `docker compose logs backend` / `logs frontend`

**Фронт не видит API (CORS):**
- В `.env` бэка: `CORS_ALLOWED_ORIGINS=https://new.ucanspeak.ru`
- В `.env` фронта: `NUXT_PUBLIC_API_URL=https://new.ucanspeak.ru` (именно с https, не http)

**Not Found media:**
- Папка `/var/ucanspeak/media` пустая или rclone ещё не закончил
- `ls /var/ucanspeak/media/` — должны быть подпапки `lessons/`, `module/` и т.п.

---

## Часть 11 — Переключение DNS (если ещё не сделано)

Ты сказал что DNS уже настроен на `89.127.197.8`. Проверь:
```bash
dig new.ucanspeak.ru +short
# или
nslookup new.ucanspeak.ru
```

Должен вернуть `89.127.197.8`. Если вернул другой IP — жди распространения DNS (может занять до нескольких часов).

---

## Часть 12 — После созвона / на будущее

### Удалить сервер №1
Ты планировал снести его сегодня же. Сделай это **после того как сервер №2 проработал 1-2 часа без проблем**. До этого — пусть живёт как backup.

### Настроить автоматический renew SSL

```bash
sudo crontab -e
```

Добавь:
```
0 3 * * * certbot renew --pre-hook "docker compose -f /root/ucanspeak/docker-compose.yml stop nginx" --post-hook "docker compose -f /root/ucanspeak/docker-compose.yml start nginx"
```

### Настроить автоматический бэкап БД

Создай `/root/backup_db.sh`:
```bash
#!/bin/bash
BACKUP_DIR=/root/backups
TIMESTAMP=$(date +%Y%m%d_%H%M)
mkdir -p $BACKUP_DIR

PGPASSWORD='<NEW_DB_PASSWORD>' pg_dump \
  -h 127.0.0.1 -U ucanspeak_user -d ucanspeak \
  -Fc -Z 9 \
  -f $BACKUP_DIR/ucanspeak_${TIMESTAMP}.dump

# Залить в YC
rclone copy $BACKUP_DIR/ucanspeak_${TIMESTAMP}.dump ycloud:ucanspeak-backup/db/ 2>&1

# Удалить локальные дампы старше 7 дней
find $BACKUP_DIR -name "ucanspeak_*.dump" -mtime +7 -delete
```

```bash
chmod +x /root/backup_db.sh
sudo crontab -e
```
Добавь:
```
0 4 * * * /root/backup_db.sh >> /var/log/ucanspeak_backup.log 2>&1
```

Каждый день в 4:00 — бэкап локально + заливка в YC + чистка старше 7 дней.

### Звонилка (когда будешь готов)

- Отдельный compose в `/root/ucanspeak/docker-compose.calls.yml`
- Подключается к сети `ucanspeak_net` (внешняя, уже создана)
- В `nginx/conf.d/ucanspeak.conf` раскомментируешь блок `location /calls/` и укажешь правильный `proxy_pass` и порт
- `docker compose -f docker-compose.calls.yml up -d`
- Nginx перезагрузка: `docker compose exec nginx nginx -s reload`

Это отдельная сессия после созвона.

---

## Что делать если что-то пошло не так

1. **Сохрани состояние** — не удаляй контейнеры с данными
2. **Логи всего подряд:**
   ```bash
   docker compose logs > /tmp/all_logs.txt
   sudo journalctl -u postgresql --since "1 hour ago" > /tmp/pg_logs.txt
   ```
3. **Опиши что происходит и что ожидал** — в чат, со скрином если можно.

---

## Шпаргалка команд

```bash
# Обновить код после git push
cd /root/ucanspeak && git pull && docker compose up -d --build

# Перезапустить всё
docker compose restart

# Применить новые миграции
docker compose exec backend python manage.py migrate

# Зайти в shell Django
docker compose exec backend python manage.py shell

# Зайти в bash backend
docker compose exec backend bash

# Посмотреть все логи
docker compose logs -f

# Остановить всё (не удаляя)
docker compose down

# Остановить и удалить всё (НЕ трогает БД на хосте и /var/ucanspeak/)
docker compose down -v
```

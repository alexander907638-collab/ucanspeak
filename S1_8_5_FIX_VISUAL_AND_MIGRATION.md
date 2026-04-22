# S1.8.5 — Фикс визуала профиля/прогресса + миграция Video.thumbnail

## Задача 1 — Бэкенд: поле Video.thumbnail + миграция

**Файл:** `ucanspeack_api-master/lesson/models.py`

В классе `Video` (модель для видео в модуле урока) **проверь наличие поля**:

```python
thumbnail = models.ImageField(
    upload_to='lessons/module/video/thumbnails/',
    null=True,
    blank=True,
    verbose_name='Превью'
)
```

Если поля нет — добавить сразу после поля `file` (или после `video_src` — как удобнее, важно чтобы было рядом с медиа-полями).

**После правки модели:**

```bash
cd ucanspeack_api-master
python manage.py check
python manage.py makemigrations lesson
```

Новая миграция должна появиться в `ucanspeack_api-master/lesson/migrations/` — имя вроде `0040_video_thumbnail.py`. Открой её и **убедись** что там только `migrations.AddField(model_name='video', name='thumbnail', ...)` — без переименований, удалений или других побочек. Если в миграции есть что-то ещё — остановись и сообщи.

**НЕ запускай** `migrate` локально (нет смысла, локальной БД может не быть или она пустая).

---

## Задача 2 — Фронтенд: страница профиля

**Файл:** `ucanspeak_front-master/app/pages/profile/index.vue`

Перепиши ПОЛНОСТЬЮ `<template>` секцию. Логику в `<script setup>` **НЕ трогай**, только исправь битый символ в `formatSessionTime` — там сейчас:

```ts
if (diffHr < 24) return `${diffHr} ${pluralize(diffHr, 'ча��', 'часа', 'часов')} назад`
```

Должно быть:

```ts
if (diffHr < 24) return `${diffHr} ${pluralize(diffHr, 'час', 'часа', 'часов')} назад`
```

**Новый `<template>` целиком:**

```vue
<template>
  <div>
    <!-- 1. CTA-баннер подписки — ВНЕ CardBase, отдельным div с gradient -->
    <div
        v-if="user && !user.is_pupil"
        class="rounded-2xl p-5 text-white mb-4"
        style="background: linear-gradient(135deg, #7575F0 0%, #9F7AEA 100%);"
    >
      <div class="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <p class="text-xs opacity-80 uppercase tracking-wider mb-1">Ваша подписка</p>
          <p class="text-lg font-semibold mb-1">
            {{ user?.is_school ? 'Школа' : 'Ученик' }}
            <span v-if="user?.subscription_expire" class="font-normal opacity-90">
              · до {{ formatDate(user.subscription_expire) }}
            </span>
          </p>
          <p class="text-sm opacity-80" v-if="user?.max_logins">
            Активна · до {{ user.max_logins }} {{ pluralize(user.max_logins, 'устройство', 'устройства', 'устройств') }} одновременно
          </p>
        </div>
        <NuxtLink to="/tariffs">
          <Button label="Продлить" class="!bg-white !text-[#7575F0] !border-white" />
        </NuxtLink>
      </div>
    </div>

    <!-- 2. Вся остальная страница — В ОДНОЙ CardBase padding="md" -->
    <CardBase padding="md">
      <BlockBaseBreadcrumbs :items="[{ label: 'Главная', to: '/' }, { label: 'Профиль' }]" />
      <TypingText28 text="Профиль" class="mb-6" />

      <!-- Секция: Личные данные -->
      <section class="mb-6 pb-6 border-b border-gray-100">
        <h2 class="text-base font-semibold mb-4">Личные данные</h2>

        <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
          <div class="md:col-span-3 flex flex-col items-center gap-2">
            <Avatar
                :image="avatarPreview || user?.avatar"
                :label="avatarPreview || user?.avatar ? null : avatarLabel"
                size="xlarge"
                shape="circle"
                class="w-20 h-20 text-lg"
            />
            <label class="text-xs text-[#7575F0] hover:underline cursor-pointer">
              Загрузить фото
              <input type="file" class="hidden" accept="image/*" @change="onFileSelected">
            </label>
          </div>

          <div class="md:col-span-9 space-y-3">
            <UIInput fluid
                     placeholder="ФИО"
                     label="ФИО"
                     id="full_name"
                     v-model="user_data.full_name"/>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <UIInput fluid
                       placeholder="Email"
                       label="Email"
                       id="email"
                       v-model="user_data.email"/>
              <UIInput fluid
                       placeholder="Телефон"
                       label="Телефон"
                       id="phone"
                       v-model="user_data.phone"/>
            </div>
          </div>
        </div>

        <!-- Школа: логотип и ссылка -->
        <template v-if="user?.is_school">
          <div class="flex items-center gap-10 mt-4 mb-4">
            <img class="w-[137px] h-auto object-contain" :src="schoolLogoPreview || user?.school?.image"/>
            <Button
                label="Выбрать логотип школы"
                icon="pi pi-image"
                size="small"
                @click="fileInput1?.click()"
            />
            <input
                type="file"
                ref="fileInput1"
                accept="image/*"
                @change="onSchoolLogoPreviewSelected"
                class="hidden"
            />
          </div>
          <div class="flex flex-wrap items-center justify-between">
            <p class="text-sm text-gray-600">Ссылка входа: {{ config.public.apiUrl }}/login/{{ user.school.slug }}</p>
            <Button size="small" severity="secondary" @click="copy(`${config.public.apiUrl}/login/${user.school.slug}`)" outlined
                    :label="copied ? 'Скопировано' : 'Скопировать'"/>
          </div>
        </template>

        <div v-if="errors" class="text-red-500 mt-3">{{ errors }}</div>

        <div class="mt-4 flex justify-end">
          <Button label="Сохранить изменения" severity="success" @click="send" :loading="pending" />
        </div>
      </section>

      <!-- Секция: Пароль -->
      <section class="mb-6 pb-6 border-b border-gray-100">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <h2 class="text-base font-semibold">Пароль</h2>
            <p class="text-sm text-gray-500 mt-0.5">Для безопасности меняйте пароль раз в несколько месяцев</p>
          </div>
          <Button
              :label="show_password_form ? 'Свернуть' : 'Изменить пароль'"
              severity="secondary"
              outlined
              @click="show_password_form = !show_password_form"
          />
        </div>

        <div v-if="show_password_form" class="mt-4 pt-4 border-t border-gray-100 space-y-3">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <UIInput fluid
                     placeholder="Новый пароль"
                     label="Новый пароль"
                     id="password"
                     type="password"
                     v-model="user_data.password"/>
            <UIInput fluid
                     placeholder="Повторите пароль"
                     label="Повторите пароль"
                     id="password1"
                     type="password"
                     v-model="user_data.password1"/>
          </div>
          <div class="flex justify-end">
            <Button label="Обновить пароль" severity="success" @click="send" :loading="pending" />
          </div>
        </div>
      </section>

      <!-- Секция: Активные сессии (заглушка до S1.9) -->
      <section class="mb-6 pb-6 border-b border-gray-100">
        <div class="flex items-center justify-between mb-0.5 flex-wrap gap-2">
          <h2 class="text-base font-semibold">Активные сессии</h2>
          <span class="text-sm text-gray-500">
            1 из {{ user?.max_logins || 1 }} активны
          </span>
        </div>
        <p class="text-sm text-gray-500 mb-3">Устройства где вы сейчас вошли</p>

        <div class="flex justify-between items-center py-3 flex-wrap gap-2">
          <div>
            <p class="font-medium text-sm">{{ current_device_name }}</p>
            <p class="text-xs text-gray-500">Последняя активность: сейчас</p>
          </div>
          <span class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
            Эта сессия
          </span>
        </div>
        <p class="text-xs text-gray-400 mt-2 italic">
          Полный список сессий и управление появятся в ближайшем обновлении
        </p>
      </section>

      <!-- Секция: Опасная зона (без заголовка) -->
      <section v-if="user && !user.is_pupil">
        <div class="rounded-xl p-4 border space-y-3" style="background: #FFFBFB; border-color: #FECACA;">
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div>
              <p class="font-medium text-sm">Выйти из аккаунта</p>
              <p class="text-xs text-gray-500">На этом устройстве</p>
            </div>
            <Button label="Выйти" severity="danger" outlined @click="$api.auth.logout(false)" />
          </div>
          <div class="flex items-center justify-between flex-wrap gap-2">
            <div>
              <p class="font-medium text-sm">Выйти со всех устройств</p>
              <p class="text-xs text-gray-500">Завершить все активные сессии</p>
            </div>
            <Button label="Выйти везде" severity="danger" outlined @click="$api.auth.logout(true)" />
          </div>
        </div>
      </section>
    </CardBase>
  </div>
</template>
```

**В `<script setup>`** добавь вычисление имени текущего устройства (сразу после `const sessions_expanded = ref(false)` или рядом — в любом месте до `useSeoMeta`):

```ts
// Определение текущего устройства для секции сессий (заглушка до S1.9-BACKEND)
const current_device_name = computed(() => {
  if (typeof navigator === 'undefined') return 'Текущее устройство'
  const ua = navigator.userAgent

  let browser = 'Браузер'
  if (ua.includes('Firefox/')) browser = 'Firefox'
  else if (ua.includes('Edg/')) browser = 'Edge'
  else if (ua.includes('Chrome/')) browser = 'Chrome'
  else if (ua.includes('Safari/')) browser = 'Safari'
  else if (ua.includes('OPR/') || ua.includes('Opera/')) browser = 'Opera'

  let os = 'устройство'
  if (ua.includes('Windows')) os = 'Windows'
  else if (ua.includes('Mac OS') || ua.includes('Macintosh')) os = 'macOS'
  else if (ua.includes('Linux')) os = 'Linux'
  else if (ua.includes('Android')) os = 'Android'
  else if (ua.includes('iPhone') || ua.includes('iPad')) os = 'iOS'

  return `${browser} на ${os}`
})
```

Неиспользуемые блоки в `<script>` которые можно удалить (опционально, для чистоты):
- `sessions_data`, `sessions_expanded`, `visible_sessions`, `hidden_sessions_count`, `terminate_session` — они больше не нужны, заглушка рендерится без них. Если удаляешь — удали ВСЁ вместе чтобы не было мёртвого кода.

---

## Задача 3 — Фронтенд: страница прогресса

**Файл:** `ucanspeak_front-master/app/pages/profile/progress.vue`

Перепиши `<template>` так, чтобы вся страница была в одной `CardBase`. `<script setup>` не трогай.

```vue
<template>
  <CardBase padding="md">
    <BlockBaseBreadcrumbs :items="[{label: 'Главная', to: '/'}, {label: 'Прогресс'}]"/>
    <TypingText28 text="Прогресс" class="mb-6"/>

    <div class="space-y-8">

      <!-- Тренажёр -->
      <section v-if="trainer_courses && trainer_courses.length">
        <h2 class="text-base font-semibold text-gray-800 mb-3">Разговорный тренажёр</h2>
        <div class="space-y-2">
          <template v-for="course in trainer_courses" :key="'tr_' + course.id">
            <NuxtLink
                v-for="level in course.levels"
                :key="'tr_lvl_' + level.id"
                :to="`/courses/trainer/${course.slug}/${level.slug}`"
                class="flex items-center gap-4 p-[10px] bg-white border border-[#18181b]/10 rounded-[20px] hover:border-[#7575F0] transition"
            >
              <div class="shrink-0 w-16 h-16 flex items-center justify-center rounded-[10px] border border-[#18181b]/10 bg-gray-50 overflow-hidden">
                <img v-if="level.icon" :src="level.icon" alt="" class="max-w-full max-h-full object-contain">
              </div>
              <div class="w-full flex flex-col">
                <span class="font-bold text-[14px] leading-[130%] text-[#2c2c2c] uppercase">{{ course.name }}</span>
                <div class="font-medium text-xs leading-[130%] text-[#778]">{{ level.title }}</div>
                <div v-if="user && !user.is_pupil">
                  <UIPLine
                      progress_bg_color="#F2F2FD"
                      progress_color="#8B8BF2"
                      :value="level.progress || 0"
                      class="my-[5px]"
                  />
                  <p class="font-normal text-xs leading-[130%] text-[#8f8fa3]">
                    {{ level.done_lessons_count || 0 }} из {{ level.lessons_count || 0 }} уровней пройдено
                  </p>
                </div>
              </div>
            </NuxtLink>
          </template>
        </div>
      </section>

      <!-- Курсы -->
      <section v-if="courses && courses.length">
        <h2 class="text-base font-semibold text-gray-800 mb-3">Курсы</h2>
        <div class="space-y-2">
          <template v-for="course in courses" :key="course.id">
            <NuxtLink
                v-for="level in course.levels"
                :key="'lvl_' + level.id"
                :to="`/courses/${course.slug}/${level.slug}`"
                class="flex items-center gap-4 p-[10px] bg-white border border-[#18181b]/10 rounded-[20px] hover:border-[#7575F0] transition"
            >
              <div class="shrink-0 w-16 h-16 flex items-center justify-center rounded-[10px] border border-[#18181b]/10 bg-gray-50 overflow-hidden">
                <img v-if="level.icon" :src="level.icon" alt="" class="max-w-full max-h-full object-contain">
              </div>
              <div class="w-full flex flex-col">
                <div class="flex items-center">
                  <span class="font-bold text-[14px] leading-[130%] text-[#2c2c2c] uppercase">{{ course.title }}</span>
                </div>
                <div class="font-medium text-xs leading-[130%] text-[#778]">{{ level.title }}</div>
                <p class="font-normal text-xs leading-[130%] text-[#8f8fa3]">{{ level.description }}</p>
                <div v-if="user && !user.is_pupil">
                  <UIPLine
                      :value="level.progress || 0"
                      :progress_bg_color="course.progress_bg_color"
                      :progress_color="course.progress_color"
                      class="my-[5px]"
                  />
                  <p class="font-normal text-xs leading-[130%] text-[#8f8fa3]">
                    {{ level.done_lessons_count }} из {{ level.lessons_count }} уроков пройдено
                  </p>
                </div>
              </div>
            </NuxtLink>
          </template>
        </div>
      </section>

      <!-- Empty state -->
      <div v-if="(!courses || !courses.length) && (!trainer_courses || !trainer_courses.length)"
           class="text-center py-12">
        <p class="text-gray-500">Начните проходить уроки чтобы увидеть прогресс</p>
        <NuxtLink to="/courses" class="inline-block mt-3 text-[#7575F0] hover:underline font-medium text-sm">
          К курсам →
        </NuxtLink>
      </div>

    </div>
  </CardBase>
</template>
```

---

## Проверки после правок

1. Запусти `python manage.py check` в `ucanspeack_api-master/` — должно быть `System check identified no issues`.
2. Файл миграции `ucanspeack_api-master/lesson/migrations/0040_*.py` создан и содержит только `AddField` для `thumbnail`.
3. `ucanspeak_front-master/app/pages/profile/index.vue` — битый символ `'ча��'` заменён на `'час'`.
4. В `index.vue` и `progress.vue` вся страница обёрнута в `<CardBase padding="md">`, внутри — breadcrumbs + `<TypingText28>` + разделы.
5. CTA-баннер в `index.vue` — отдельным `<div>` НАД `<CardBase>`, без `<CardBase>`-обёртки.

## Не делать

- Не запускать `migrate` локально.
- Не трогать `favorite.vue`, `CardDictionaryItem.vue`, `LikeBtn.vue`.
- Не менять структуру `Dockerfile`, `docker-compose.yml`, `settings.py`.
- Не добавлять зависимости в `requirements.txt` или `package.json`.

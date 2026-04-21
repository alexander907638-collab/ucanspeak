# Сессия 1.8 Frontend PAGES v2 — Прогресс, Профиль, Видео с thumbnail

Контекст: продолжение S1.8 после CORE. В этой сессии — переделанные страницы Профиль и Прогресс + использование нового поля `video.thumbnail` с бека.

Все пути от `ucanspeak_front-master/`.

---

## ВАЖНО: принцип визуальной консистентности

**Перед тем как писать вёрстку, посмотри как оформлены другие страницы платформы:**

```bash
cat app/pages/profile/favorite.vue
cat app/pages/tariffs.vue 2>/dev/null
cat app/pages/profile/pupils.vue
cat app/components/Card/Base.vue 2>/dev/null
ls app/components/Card/
ls app/components/UI/
```

**Цель:** новые страницы (Прогресс, Профиль) должны визуально **сливаться** с остальной платформой, а не выглядеть чужеродно.

Правила:
- **Используй существующие компоненты** (`<CardBase>`, `<BlockBaseBreadcrumbs>`, `<TypingText48>`, PrimeVue `<Button>`, `<InputText>`, `<Password>`) **если они уже применяются** на других страницах профиля. Не создавай свои аналоги.
- **Отступы между блоками** — такие же как на `favorite.vue` или `pupils.vue` (обычно `space-y-3` или `space-y-4`).
- **Скругления, padding карточек** — такие же. Скорее всего `rounded-xl` или `rounded-2xl` с `padding` через `<CardBase padding="md">` или явно.
- **Цвета brand** — если есть `#7575F0` (брендовый фиолетовый) в других страницах — используй его, **не `#4F46E5`** из мокапа.
- **Bg-градиент CTA** — если на странице тарифов или где-то есть градиент — возьми оттуда. Иначе сделай мягче: `from-[#7575F0] to-[#9F7AEA]`.

**Что из HTML-мокапов оставляем:**
- Композицию (что где лежит, иерархия блоков)
- Типографику помягче: `font-semibold` вместо `font-bold`, текст-помощник `text-gray-500 text-sm`, заголовки секций `text-base font-semibold` не `text-lg font-bold`

---

Выполни 3 задачи последовательно.

---

## Задача 1 — Страница Прогресса

Файл: `app/pages/profile/progress.vue` (проверь точное имя в `app/pages/profile/`).

Сначала посмотри как сейчас рендерятся плашки на главной:
```bash
cat app/pages/index.vue 2>/dev/null
cat app/pages/courses/index.vue 2>/dev/null
grep -rn "из.*уроков пройдено\|из.*уровней пройдено" app/
```

Найди компонент который рендерит "уровень с прогресс-баром" на главной — скорее всего `CardLevel.vue`, `CardCourseLevel.vue` или inline-вёрстка внутри страницы. Если inline — вынеси в отдельный компонент и используй на обеих страницах.

### 1.1 — `<script setup>`

```typescript
<script setup lang="ts">
const {$api} = useNuxtApp()
const {data: courses} = useHttpRequest(await useAsyncData(() => $api.lessons.courses()))
const {data: trainer_courses} = useHttpRequest(await useAsyncData(() => $api.trainer.courses()))

useSeoMeta({ title: 'Прогресс' })
</script>
```

Если `$api.trainer.courses()` не существует — проверь `app/repository/trainer/index.ts` или `app/repository/train/index.ts`.

### 1.2 — `<template>` (адаптируй под реальные компоненты платформы)

```vue
<template>
  <div>
    <BlockBaseBreadcrumbs :items="[{ label: 'Главная', to: '/' }, { label: 'Прогресс' }]" />
    <TypingText48 text="Прогресс" class="mb-6" />

    <div class="space-y-6">
      <!-- Тренажёр -->
      <section v-if="trainer_courses && trainer_courses.length">
        <h2 class="text-base font-semibold text-gray-800 mb-3">Разговорный тренажёр</h2>
        <div class="space-y-2">
          <template v-for="course in trainer_courses" :key="'tr_' + course.id">
            <CardLevel
                v-for="level in course.levels"
                :key="'tr_lvl_' + level.id"
                :course="course"
                :level="level"
                :is_trainer="true"
            />
          </template>
        </div>
      </section>

      <!-- Курсы -->
      <section v-if="courses && courses.length">
        <h2 class="text-base font-semibold text-gray-800 mb-3">Курсы</h2>
        <div class="space-y-2">
          <template v-for="course in courses" :key="course.id">
            <CardLevel
                v-for="level in course.levels"
                :key="'lvl_' + level.id"
                :course="course"
                :level="level"
            />
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
  </div>
</template>
```

**Важно:**
- `<CardLevel>` — это пример. Найди **реальный компонент** на главной. Если inline — вынеси.
- Пропы полей прогресса (`done_lessons_count`, `total_lessons`, `progress`) — проверь через Network что реально приходит.

---

## Задача 2 — Страница Профиля

Файл: `app/pages/profile/index.vue` (или `profile.vue` — проверь).

### 2.0 — Посмотри текущий файл ПЕРЕД правкой

```bash
cat app/pages/profile/index.vue
```

Выдели:
- Какие поля формы (`form.full_name`, `form.phone`?)
- Какие методы в `<script setup>` (`updateProfile`, `changePassword`, `logout`, `logoutAll`?)
- Какие компоненты импортированы
- Есть ли `useAuthStore()` / `storeToRefs`

**Сохрани все существующие методы и переменные** под теми же именами. Меняем только template.

### 2.1 — `<script setup>` — ДОПОЛНЕНИЯ

К существующему коду добавь:

```typescript
const show_password_form = ref(false)
const password_form = ref({ new_password: '', repeat_password: '' })
const password_saving = ref(false)

// Сессии
const sessions_expanded = ref(false)
const {data: sessions_data, refresh: refresh_sessions} = useHttpRequest(
    await useAsyncData(() => $api.user.active_sessions())
)
// Ожидается: { total_active: number, max_logins: number, sessions: [{id, user_agent, ip_address, last_used_at, is_current}] }

const visible_sessions = computed(() => {
  const list = sessions_data.value?.sessions || []
  return sessions_expanded.value ? list : list.slice(0, 4)
})

const hidden_sessions_count = computed(() => {
  const total = sessions_data.value?.sessions?.length || 0
  return Math.max(0, total - 4)
})

async function terminate_session(session_id: number) {
  try {
    await $api.user.terminate_session(session_id)
    await refresh_sessions()
    toast.add({ severity: 'success', summary: 'Сессия завершена', life: 2000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Не удалось завершить сессию', life: 3000 })
  }
}

function formatDate(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return `${String(d.getDate()).padStart(2, '0')}.${String(d.getMonth() + 1).padStart(2, '0')}.${d.getFullYear()}`
}

function formatSessionTime(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 2) return 'сейчас'
  if (diffMin < 60) return `${diffMin} мин назад`
  const diffHr = Math.floor(diffMin / 60)
  if (diffHr < 24) return `${diffHr} ${pluralize(diffHr, 'час', 'часа', 'часов')} назад`
  const diffDay = Math.floor(diffHr / 24)
  if (diffDay < 7) return `${diffDay} ${pluralize(diffDay, 'день', 'дня', 'дней')} назад`
  return formatDate(iso)
}

function getInitials(name: string): string {
  if (!name) return '?'
  return name.split(/\s+/).map(p => p.charAt(0).toUpperCase()).slice(0, 2).join('')
}

function pluralize(n: number, one: string, few: string, many: string): string {
  const mod10 = n % 10, mod100 = n % 100
  if (mod100 >= 11 && mod100 <= 14) return many
  if (mod10 === 1) return one
  if (mod10 >= 2 && mod10 <= 4) return few
  return many
}
```

### 2.2 — `<template>`

Композиция из утверждённого артефакта `profile_mockup_v2.html`. Стили — **с платформы**, не из мокапа.

Логика блоков:
1. CTA баннер подписки (фиолетовый gradient) + кнопка Продлить
2. Карточка «Личные данные» (аватар + форма) + кнопка Сохранить
3. Карточка «Пароль» — свёрнута, разворачивается по клику
4. Карточка «Активные сессии» — `X из Y активны`, список первых 4, кнопка «Показать все»
5. Красный блок — две кнопки выхода, без заголовка "Опасная зона"

Шаблон (адаптируй под реальные компоненты):

```vue
<template>
  <div>
    <BlockBaseBreadcrumbs :items="[{ label: 'Главная', to: '/' }, { label: 'Профиль' }]" />
    <TypingText48 text="Профиль" class="mb-6" />

    <div class="space-y-3">

      <!-- 1. CTA подписка -->
      <CardBase padding="sm" class="relative overflow-hidden">
        <div class="absolute inset-0 -z-10"
             style="background: linear-gradient(135deg, #7575F0 0%, #9F7AEA 100%);"></div>
        <div class="flex items-center justify-between gap-4 flex-wrap text-white">
          <div>
            <p class="text-xs opacity-80 uppercase tracking-wider mb-1">Ваша подписка</p>
            <p class="text-lg font-semibold mb-1">
              {{ user?.account_type || 'Ученик' }}
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
      </CardBase>

      <!-- 2. Личные данные -->
      <CardBase padding="sm">
        <h2 class="text-base font-semibold mb-4">Личные данные</h2>

        <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
          <div class="md:col-span-3 flex flex-col items-center gap-2">
            <div class="w-20 h-20 rounded-full bg-gradient-to-br from-[#EFEFF5] to-[#D1D5DB] flex items-center justify-center text-2xl font-semibold text-gray-600 overflow-hidden">
              <img v-if="form.avatar" :src="form.avatar" alt="" class="w-full h-full object-cover">
              <span v-else>{{ getInitials(form.full_name) }}</span>
            </div>
            <label class="text-xs text-[#7575F0] hover:underline cursor-pointer">
              Загрузить фото
              <input type="file" class="hidden" accept="image/*" @change="handleAvatarChange">
            </label>
          </div>

          <div class="md:col-span-9 space-y-3">
            <div>
              <label class="block text-xs text-gray-500 mb-1">Имя и фамилия</label>
              <InputText v-model="form.full_name" fluid />
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs text-gray-500 mb-1">Email</label>
                <InputText v-model="form.email" type="email" fluid />
              </div>
              <div>
                <label class="block text-xs text-gray-500 mb-1">Телефон</label>
                <InputText v-model="form.phone" type="tel" placeholder="+7 (___) ___-__-__" fluid />
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4 flex justify-end">
          <Button label="Сохранить изменения" severity="success" @click="updateProfile" :loading="saving" />
        </div>
      </CardBase>

      <!-- 3. Пароль -->
      <CardBase padding="sm">
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
            <div>
              <label class="block text-xs text-gray-500 mb-1">Новый пароль</label>
              <Password v-model="password_form.new_password" toggleMask fluid :feedback="false" />
            </div>
            <div>
              <label class="block text-xs text-gray-500 mb-1">Повторите пароль</label>
              <Password v-model="password_form.repeat_password" toggleMask fluid :feedback="false" />
            </div>
          </div>
          <div class="flex justify-end">
            <Button label="Обновить пароль" severity="success" @click="changePassword" :loading="password_saving" />
          </div>
        </div>
      </CardBase>

      <!-- 4. Сессии -->
      <CardBase padding="sm" v-if="sessions_data">
        <div class="flex items-center justify-between mb-0.5 flex-wrap gap-2">
          <h2 class="text-base font-semibold">Активные сессии</h2>
          <span class="text-sm text-gray-500">
            {{ sessions_data.total_active || 0 }} из {{ sessions_data.max_logins || 0 }} активны
          </span>
        </div>
        <p class="text-sm text-gray-500 mb-3">Устройства где вы сейчас вошли</p>

        <div>
          <div
              v-for="session in visible_sessions"
              :key="session.id"
              class="flex justify-between items-center py-3 border-b border-gray-100 last:border-b-0 flex-wrap gap-2"
          >
            <div>
              <p class="font-medium text-sm">{{ session.user_agent_short || session.user_agent || 'Неизвестное устройство' }}</p>
              <p class="text-xs text-gray-500">
                Последняя активность: {{ formatSessionTime(session.last_used_at) }}
                <span v-if="session.ip_address"> · IP {{ session.ip_address }}</span>
              </p>
            </div>
            <span v-if="session.is_current"
                  class="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
              Эта сессия
            </span>
            <button v-else
                    class="text-xs text-red-600 hover:underline cursor-pointer"
                    @click="terminate_session(session.id)">
              Завершить
            </button>
          </div>

          <div v-if="hidden_sessions_count > 0" class="pt-3 text-center">
            <button
                class="text-sm text-[#7575F0] hover:underline cursor-pointer font-medium"
                @click="sessions_expanded = !sessions_expanded"
            >
              {{ sessions_expanded ? 'Свернуть' : `Показать все (${hidden_sessions_count} скрыто)` }}
            </button>
          </div>
        </div>
      </CardBase>

      <!-- 5. Кнопки выхода (без заголовка "Опасная зона") -->
      <div class="rounded-xl p-4 border space-y-3" style="background: #FFFBFB; border-color: #FECACA;">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <p class="font-medium text-sm">Выйти из аккаунта</p>
            <p class="text-xs text-gray-500">На этом устройстве</p>
          </div>
          <Button label="Выйти" severity="danger" outlined @click="logout" />
        </div>
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div>
            <p class="font-medium text-sm">Выйти со всех устройств</p>
            <p class="text-xs text-gray-500">Завершить все активные сессии</p>
          </div>
          <Button label="Выйти везде" severity="danger" outlined @click="logoutAll" />
        </div>
      </div>

    </div>
  </div>
</template>
```

### 2.3 — API для активных сессий (если методов нет)

Файл: `app/repository/user/index.ts`. Добавь если нет:

```typescript
active_sessions() {
  return appFetch('/api/user/active_sessions/', { method: 'GET' })
},
terminate_session(session_id: number) {
  return appFetch(`/api/user/sessions/${session_id}/terminate/`, { method: 'POST' })
},
```

**Внимание:** бек-эндпоинтов может ещё не быть. Если ответ 404 — **временно** в `<script setup>` замени useAsyncData на заглушку:

```typescript
const sessions_data = ref({
  total_active: 1,
  max_logins: user?.max_logins || 0,
  sessions: []
})
```

И пометь комментарием `// TODO: нужны бек-эндпоинты active_sessions/terminate_session` — это пойдёт в S1.9.

---

## Задача 3 — Использовать thumbnail в VideoWithPreview

Файл: `app/components/Block/VideoWithPreview.vue`.

### 3.1 — Добавь `thumbnail` в `defineProps`

Найди `const props = defineProps<{ data: { ... } }>()` и добавь `thumbnail?: string | null`:

```typescript
const props = defineProps<{
  showPreview: boolean;
  data: {
    video_src: string
    file: string
    thumbnail?: string | null
    phrases: {...}[]
    watermarks: {...}[]
  }
}>()
```

### 3.2 — Приоритизируй thumbnail в `onMounted`

В блоке `onMounted(() => { if(!props.showPreview) return ... })` после `document.addEventListener('fullscreenchange', onFullscreenChange)` добавь:

```typescript
// Приоритет 1: thumbnail с сервера — мгновенно, без загрузки видеофайла
if (props.data.thumbnail) {
  firstFrame.value = props.data.thumbnail
  return
}

// Приоритет 2: fallback — canvas-генерация (существующий код)
const tempVideo = document.createElement('video')
// ... далее существующая логика ...
```

Когда бек через management-команду сгенерирует thumbnails — они будут мгновенно, без canvas.

---

## Финальная сводка

Выведи:
1. Список изменённых файлов
2. Имя и путь компонента для рендера уровня курса (например `CardLevel`)
3. Реальные названия полей API прогресса (если отличаются от `done_lessons_count` / `total_lessons` / `progress`)
4. Существуют ли бек-эндпоинты `active_sessions` / `terminate_session`. Если нет — пометить TODO для следующей сессии
5. Что проверить Александру в браузере:
   - `/profile` — композиция как на макете v2, но стили платформенные (не чужеродно)
   - Раскрывашка сессий работает если больше 5
   - `updateProfile` / `changePassword` / `logout` / `logoutAll` работают как раньше
   - `/profile/progress` — плашки уровней с прогресс-барами, две секции
   - Видео в уроке с сгенерированным thumbnail — первый кадр мгновенно

# Сессия 4 — Кнопки «Редактировать» в тренажёре

Контекст: S1 + S1.5 + S2 + S3 уже выполнены. На странице урока (`pages/courses/[course_slug]/[level_slug]/[lesson_slug]/index.vue`) уже есть кнопки-карандашики для админа (где `user.is_superuser`), которые ведут в Django admin. На страницах тренажёра (`pages/courses/trainer/...`) таких кнопок нет — нужно добавить.

Все пути — от родительской папки:
- `ucanspeak_front-master/` — фронт (только его трогаем в S4)

Цели:
- Создать общий компонент `<UIEditAdminBtn>` чтобы не копипастить логику кнопки в 5+ местах
- На странице тренажёра (`pages/courses/trainer/[course_slug]/[level_slug]/[topic_slug]/index.vue`) добавить кнопку «Редактировать» возле названия топика (ведёт в `/admin/train/topic/<id>/change/`)
- На странице списка топиков (`pages/courses/trainer/[course_slug]/[level_slug]/index.vue`) — кнопка возле каждого топика
- На странице курса тренажёра (`pages/courses/trainer/[course_slug]/index.vue`) — кнопка возле каждого уровня
- На странице тренажёров (`pages/courses/trainer/index.vue`) — кнопка возле каждого курса
- В существующих местах в уроке (`lesson_slug/index.vue`) — заменить inline-разметку на новый компонент. Это не обязательно, но желательно чтоб всё было единообразно.

Выполни 4 задачи последовательно. После каждой — короткий отчёт. В конце — финальная сводка с инструкцией по проверке.

---

## Задача 1 — создать компонент UIEditAdminBtn

Создай новый файл: `ucanspeak_front-master/app/components/UI/EditAdminBtn.vue`.

Содержимое:
```vue
<script setup lang="ts">
const config = useRuntimeConfig()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const props = defineProps<{
  app: string         // 'lesson' | 'train' | 'user'
  model: string       // 'lesson' | 'topic' | 'video' и т.д.
  id: number | string
  label?: string      // если не передан — только иконка
  fluid?: boolean
}>()

const href = computed(() =>
  `${config.public.apiUrl}/admin/${props.app}/${props.model}/${props.id}/change/`
)
</script>

<template>
  <a
    v-if="user && user.is_superuser"
    :href="href"
    target="_blank"
    rel="noopener"
    @click.stop
  >
    <Button
      :fluid="fluid"
      outlined
      severity="secondary"
      icon="pi pi-pencil"
      :label="label"
    />
  </a>
</template>
```

Логика:
- Кнопка рендерится только если `user.is_superuser === true` (как сейчас в уроке)
- Открывает админку Django в новой вкладке
- Принимает `app`, `model`, `id` — строит URL `/admin/<app>/<model>/<id>/change/`
- Опциональный `label` — если есть, рядом с иконкой будет текст; если нет — только иконка
- `@click.stop` чтобы клик по кнопке не пробивал по родительской ссылке (на страницах со списком кнопка часто внутри карточки-ссылки)

Компонент использует Nuxt auto-import — будет доступен в шаблонах как `<UIEditAdminBtn>` (без явного import).

---

## Задача 2 — добавить кнопки в страницы тренажёра

Везде используй компонент из Задачи 1.

### 2a. Страница топика (внутренняя)

Файл: `ucanspeak_front-master/app/pages/courses/trainer/[course_slug]/[level_slug]/[topic_slug]/index.vue`.

В `<template>` найди заголовок топика (где-то в районе `<TypingText28 :text="topic_data.topic.name" />` или подобного — это название аудиоурока). Сразу под ним или рядом добавь:

```vue
<UIEditAdminBtn
  app="train"
  model="topic"
  :id="topic_data.topic.id"
  label="Редактировать топик"
  class="mt-2"
/>
```

Также — каждый аудиофайл в списке слева. Найди `v-for="audio_file in topic_data.topic.audio_files"`. Внутри карточки аудиофайла, рядом с названием, добавь:

```vue
<UIEditAdminBtn
  app="train"
  model="audiofile"
  :id="audio_file.id"
  class="mt-1"
/>
```

(без label, только иконка, чтобы не ломать вёрстку маленькой карточки)

### 2b. Страница списка топиков уровня

Файл: `ucanspeak_front-master/app/pages/courses/trainer/[course_slug]/[level_slug]/index.vue`.

Найди цикл по топикам (наверняка `v-for="topic in topics"` или похоже). Внутри карточки топика добавь:

```vue
<UIEditAdminBtn
  app="train"
  model="topic"
  :id="topic.id"
  class="mt-2"
/>
```

### 2c. Страница списка уровней курса тренажёра

Файл: `ucanspeak_front-master/app/pages/courses/trainer/[course_slug]/index.vue`.

Найди цикл по уровням. Внутри карточки уровня добавь:

```vue
<UIEditAdminBtn
  app="train"
  model="level"
  :id="level.id"
  class="mt-2"
/>
```

### 2d. Главная страница тренажёра

Файл: `ucanspeak_front-master/app/pages/courses/trainer/index.vue`.

Найди цикл по курсам. Внутри карточки курса добавь:

```vue
<UIEditAdminBtn
  app="train"
  model="course"
  :id="course.id"
  class="mt-2"
/>
```

---

## Задача 3 — заменить inline-кнопки в уроке на компонент

Это **необязательно для работы**, но единообразие лучше. Если по ходу работы видишь что замена легко делается без риска сломать вёрстку — делай. Если рискованно (вложено в нестандартный layout) — оставь как есть, отмечай в отчёте.

Файл: `ucanspeak_front-master/app/pages/courses/[course_slug]/[level_slug]/[lesson_slug]/index.vue`.

Найди три места и замени:

1. **Кнопка «Редактировать урок»** (около строки 311):
   ```vue
   <a v-if="user && user.is_superuser" class="block mt-3" target="_blank" :href="`${config.public.apiUrl}/admin/lesson/lesson/${lesson.id}/change/`">
     <Button fluid outlined severity="secondary" icon="pi pi-pencil" label="Редактировать урок"/>
   </a>
   ```
   Заменить на:
   ```vue
   <UIEditAdminBtn
     app="lesson"
     model="lesson"
     :id="lesson.id"
     label="Редактировать урок"
     :fluid="true"
     class="block mt-3"
   />
   ```

2. **Карандашик блока модуля** (около строки 398):
   ```vue
   <a v-if="user && user.is_superuser" target="_blank" :href="`${config.public.apiUrl}/admin/lesson/moduleblock/${block.id}/change/`">
     <Button outlined severity="secondary" icon="pi pi-pencil"/>
   </a>
   ```
   Заменить на:
   ```vue
   <UIEditAdminBtn
     app="lesson"
     model="moduleblock"
     :id="block.id"
   />
   ```

3. **Кнопка с label у группы словаря** (около строки 428):
   ```vue
   <a v-if="user && user.is_superuser" target="_blank" :href="`${config.public.apiUrl}/admin/lesson/dictionarygroup/${group.id}/change/`">
     <Button outlined severity="secondary" icon="pi pi-pencil" :label="`${group.title}`"/>
   </a>
   ```
   Заменить на:
   ```vue
   <UIEditAdminBtn
     app="lesson"
     model="dictionarygroup"
     :id="group.id"
     :label="group.title"
   />
   ```

Если в коде есть ещё места с такими же inline-кнопками (grep по `is_superuser` в этом файле) — тоже замени.

---

## Задача 4 — добавить кнопку Video в админку через карандаш на фронте

В уроке возле видео сейчас нет кнопки edit. Это упущение. На страницах с видео-плеером (где рендерится `<BlockVideoWithPreview>` или подобный компонент видео) рядом с превью/в углу добавь кнопку:

```vue
<UIEditAdminBtn
  app="lesson"
  model="video"
  :id="video.id"
  class="mt-2"
/>
```

Найди в `pages/courses/[course_slug]/[level_slug]/[lesson_slug]/index.vue` все места где `block.videos[0]` или `<BlockVideoWithPreview ... :data="...">` рендерится, и рядом добавь кнопку. Пример контекста (около строк 380-385):
```vue
<div v-if="block.videos.length > 0 && block.videos[0].phrases.length > 0" class="mt-3">
  <BlockVideoWithPreview :showPreview="false" :data="block.videos[0]"/>
</div>
```
После этого блока добавь:
```vue
<UIEditAdminBtn
  v-if="block.videos.length > 0"
  app="lesson"
  model="video"
  :id="block.videos[0].id"
  class="mt-2"
/>
```

Также если есть отдельный template `viewMode === 'videos'` (около строк 350-360, где `v-for="video in videos"`), там тоже добавь рядом с каждым видео:
```vue
<UIEditAdminBtn
  app="lesson"
  model="video"
  :id="video.id"
  class="mt-1"
/>
```

---

## Финальная сводка

Выведи:
1. Список изменённых файлов
2. Подтверждение что миграции **не нужны** (мы трогаем только фронт)
3. Чеклист ручной проверки:
   - Зайти под суперюзером (`is_superuser=true` в Django)
   - На странице урока — карандашики на месте, ведут в админку
   - На странице тренажёра (любой топик) — появилась кнопка «Редактировать топик» и карандашики возле аудиофайлов
   - На странице списка топиков уровня — карандашики возле каждого топика
   - На странице курса тренажёра — карандашики возле уровней
   - На главной тренажёров — карандашики возле курсов
   - Зайти под обычным юзером (`is_superuser=false`) — никаких карандашиков нигде
   - Клик по карандашу открывает Django admin в новой вкладке, нужный объект сразу открыт
4. Что НЕ сделано / отложено:
   - S5 — onsite-editor видеофраз (отдельная сессия после старта сервера №2)

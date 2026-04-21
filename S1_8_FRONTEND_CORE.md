# Сессия 1.8 Frontend CORE — DictionaryItem, LikeBtn, язык на поиске, тренажёр

Контекст: платформа Ucanspeak (Nuxt 4 + Vue 3 + TypeScript + Tailwind + PrimeVue). После S1.8-BACKEND делаем фронт. В этой сессии — 4 задачи по карточкам и базовому UX.

Все пути от `ucanspeak_front-master/`.

Выполни 4 задачи последовательно.

---

## Задача 1 — LikeBtn: серое если не в избранном, фиолетовое если в избранном

Файл: `app/components/UI/LikeBtn.vue`.

Сейчас сердечко **всегда фиолетовое** (outline), при `value=true` рендерится второй path поверх (заполнение). Надо: при `value=false` — **серое** (`#9CA3AF`), при `value=true` — **фиолетовое заполненное** (`#7575F0`).

Перепиши `<template>` полностью:

```vue
<template>
  <button @click="emit('update:value', !value)" class="flex items-center justify-center">
    <svg width="17" height="15" viewBox="0 0 17 15" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
          d="M8.33803 1.27743C7.36788 0.407497 6.09644 -0.0493334 4.79447 0.0042301C3.4925 0.0577936 2.26288 0.617518 1.36747 1.56421C0.472051 2.5109 -0.0184111 3.76975 0.000528821 5.07268C0.0194687 6.37561 0.546314 7.61967 1.46887 8.53994L7.1597 14.2299C7.47225 14.5424 7.89609 14.7179 8.33803 14.7179C8.77997 14.7179 9.20382 14.5424 9.51637 14.2299L15.2072 8.53994C16.1298 7.61967 16.6566 6.37561 16.6755 5.07268C16.6945 3.76975 16.204 2.5109 15.3086 1.56421C14.4132 0.617518 13.1836 0.0577936 11.8816 0.0042301C10.5796 -0.0493334 9.30819 0.407497 8.33803 1.27743ZM7.36137 2.64743L7.74887 3.0341C7.90514 3.19033 8.11706 3.27809 8.33803 3.27809C8.559 3.27809 8.77093 3.19033 8.9272 3.0341L9.3147 2.64743C9.62219 2.32907 9.99001 2.07513 10.3967 1.90043C10.8034 1.72573 11.2408 1.63378 11.6834 1.62993C12.126 1.62609 12.5649 1.71043 12.9745 1.87803C13.3842 2.04563 13.7564 2.29314 14.0694 2.60612C14.3823 2.91909 14.6298 3.29127 14.7974 3.70092C14.965 4.11058 15.0494 4.54951 15.0455 4.99211C15.0417 5.4347 14.9497 5.8721 14.775 6.27878C14.6003 6.68546 14.3464 7.05328 14.028 7.36077L8.33803 13.0516L2.64804 7.36077C2.04084 6.73209 1.70486 5.89009 1.71246 5.0161C1.72005 4.14211 2.07061 3.30607 2.68864 2.68804C3.30667 2.07001 4.14271 1.71945 5.0167 1.71185C5.89069 1.70426 6.73269 2.04024 7.36137 2.64743Z"
          :fill="value ? '#7575F0' : '#9CA3AF'"
      />
      <path
          v-if="value"
          d="M7.36137 2.64743L7.74887 3.0341C7.90514 3.19033 8.11706 3.27809 8.33803 3.27809C8.559 3.27809 8.77093 3.19033 8.9272 3.0341L9.3147 2.64743C9.62219 2.32907 9.99001 2.07513 10.3967 1.90043C10.8034 1.72573 11.2408 1.63378 11.6834 1.62993C12.126 1.62609 12.5649 1.71043 12.9745 1.87803C13.3842 2.04563 13.7564 2.29314 14.0694 2.60612C14.3823 2.91909 14.6298 3.29127 14.7974 3.70092C14.965 4.11058 15.0494 4.54951 15.0455 4.99211C15.0417 5.4347 14.9497 5.8721 14.775 6.27878C14.6003 6.68546 14.3464 7.05328 14.028 7.36077L8.33803 13.0516L2.64804 7.36077C2.04084 6.73209 1.70486 5.89009 1.71246 5.0161C1.72005 4.14211 2.07061 3.30607 2.68864 2.68804C3.30667 2.07001 4.14271 1.71945 5.0167 1.71185C5.89069 1.70426 6.73269 2.04024 7.36137 2.64743Z"
          fill="#7575F0"
      />
    </svg>
  </button>
</template>
```

Что поменялось: только **первый path `:fill`** — теперь зависит от `value`. Второй path (заполнение) оставлен как был.

---

## Задача 2 — CardDictionaryItem: две отдельные пилюли + опциональный чекбокс

Файл: `app/components/Card/DictionaryItem.vue`.

### 2.1 — В `<script setup lang="ts">`

Найди блок `defineProps` (или `const props = defineProps<{...}>()`). Добавь в список пропов:
```typescript
show_checkbox?: boolean
```

Если defineProps не обёрнут в `withDefaults` — оберни:
```typescript
const props = withDefaults(defineProps<{
  // ...существующие пропы оставь как есть...
  show_checkbox?: boolean
}>(), {
  show_checkbox: false,
  // ...существующие дефолты если были...
})
```

Сразу после `defineProps`/`withDefaults` добавь локальный ref для визуального чекбокса:
```typescript
const checked = ref(false)
```

### 2.2 — Полностью замени `<template>`

Предполагаю что ref на авторизацию уже есть в компоненте (через useAuthStore). Если нет — надо сохранить существующую логику доступа к `user` и `play` и другим. То что ниже — только вёрстка с сохранением логики `@click="emits('toggle_open', ...)"`, `play`, `emits('toggle_fav', ...)`.

```vue
<template>
  <div class="flex items-start gap-3 w-full">
    <!-- Чекбокс: только если show_checkbox=true -->
    <input
        v-if="show_checkbox"
        type="checkbox"
        class="custom-checkbox mt-1.5"
        v-model="checked"
        @click.stop
    >

    <!-- Колонка с двумя пилюлями (items-end прижимает перевод к правому краю оригинала) -->
    <div class="inline-flex flex-col items-end max-w-full min-w-0">

      <!-- Пилюля оригинала, ширина по контенту -->
      <div
          @click="emits('toggle_open', item.id)"
          class="inline-flex items-center gap-2 bg-[#EFEFF5] hover:bg-[#e9e9e9] cursor-pointer px-3 py-1.5 select-none max-w-full"
          style="border-radius: 10px;"
      >
        <span
            @click.stop="play"
            class="text-base leading-[130%] break-words cursor-pointer"
        >
          {{ dictionary_direction === 'ruEN' ? item.text_ru : item.text_en }}
        </span>
        <UILikeBtn
            v-if="user"
            :class="loading ? 'disabled opacity-50' : ''"
            @click.stop="emits('toggle_fav', item.id)"
            v-model:value="item.is_favorite"
            class="flex-shrink-0"
        />
      </div>

      <!-- Пилюля перевода (видна при opened) — прижата к правому краю оригинала через items-end родителя -->
      <div
          v-if="opened"
          class="bg-[#7575F0] px-3 py-1.5 max-w-full mt-1"
          style="border-radius: 10px;"
      >
        <p class="text-base text-white leading-[130%] break-words">
          {{ dictionary_direction === 'ruEN' ? item.text_en : item.text_ru }}
        </p>
      </div>

    </div>
  </div>
</template>
```

### 2.3 — Добавь `<style scoped>` в конец файла

Если уже есть `<style scoped>` — добавь в него. Если нет — создай:

```vue
<style scoped>
.custom-checkbox {
  appearance: none;
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  border: 1.5px solid #D1D5DB;
  background: white;
  cursor: pointer;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  margin: 0;
}
.custom-checkbox:hover {
  border-color: #10B981;
}
.custom-checkbox:checked {
  background-color: #10B981;
  border-color: #10B981;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='white'%3E%3Cpath d='M13.854 3.146a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 9.793l6.646-6.647a.5.5 0 0 1 .708 0z'/%3E%3C/svg%3E");
  background-position: center;
  background-repeat: no-repeat;
  background-size: 14px 14px;
}
</style>
```

---

## Задача 3 — show_checkbox: добавить на странице урока, НЕ добавлять на других

Сначала найди все места где используется `<CardDictionaryItem>`:

```bash
grep -rn "CardDictionaryItem\|<DictionaryItem" app/
```

Ожидаемые места:
- `app/pages/courses/[course_slug]/[level_slug]/[lesson_slug]/index.vue` — страница урока, **добавить** `:show_checkbox="true"`
- `app/pages/profile/favorite.vue` — страница избранного, **не трогать** (default=false)
- `app/pages/search.vue` — страница поиска, **не трогать**

Если найдёшь ещё места — оставь без чекбокса (по умолчанию).

На странице урока пример что поменять:

Было:
```vue
<CardDictionaryItem
    :dictionary_direction="dictionary_direction"
    :item="item"
    v-for="item in group.items"
    :opened="opened_dictionary_id === item.id"
    @toggle_open="handleToggleDictionaryOpen"
    @toggle_fav="handleToggleFav"
    :loading="fav_loading"/>
```

Стало:
```vue
<CardDictionaryItem
    :dictionary_direction="dictionary_direction"
    :item="item"
    v-for="item in group.items"
    :opened="opened_dictionary_id === item.id"
    :show_checkbox="true"
    @toggle_open="handleToggleDictionaryOpen"
    @toggle_fav="handleToggleFav"
    :loading="fav_loading"/>
```

---

## Задача 4 — Определение языка запроса на поиске

Файл: `app/pages/search.vue`.

Сейчас `dictionary_direction="ruEN"` захардкожено. Надо: определять язык по `q.value` и передавать в компонент.

### 4.1 — Добавь computed для определения направления

В `<script setup>` после объявления `const q = ref('')`:

```typescript
const dictionary_direction = computed(() => {
  // Если в строке есть кириллица — запрос русский, ответ английский
  const hasCyrillic = /[а-яё]/i.test(q.value)
  return hasCyrillic ? 'ruEN' : 'enRU'
})
```

### 4.2 — Используй в CardDictionaryItem

Было:
```vue
<CardDictionaryItem
    :item="item"
    dictionary_direction="ruEN"
    ...
```

Стало:
```vue
<CardDictionaryItem
    :item="item"
    :dictionary_direction="dictionary_direction"
    ...
```

Обрати внимание: `dictionary_direction="ruEN"` без `:` — это строковая константа. А `:dictionary_direction="dictionary_direction"` — уже Vue-binding на computed.

### 4.3 — Тот же принцип для CardVoiceFile во вкладках «Фразы» и «Тренажер»

Проверь — принимает ли `CardVoiceFile` проп `dictionary_direction`? Если да — передай туда так же `:dictionary_direction="dictionary_direction"`. Если не принимает (работает по-другому для фраз) — оставь как есть, поправим в следующей сессии.

---

## Задача 5 — Меняем «уроков» на «уровни» в тренажёре

Сначала найди файл тренажёра. Возможные места:
- `app/components/Card/TrainerCourse.vue`
- `app/pages/courses/trainer/...`
- `app/pages/index.vue`

```bash
grep -rn 'уроков пройдено\|уроков пройд\|уровней пройдено' app/
```

Когда найдёшь файл с «уроков пройдено» для тренажёра — покажи какой это файл.

В тренажёре у плашек уровней Курса (у `train/Course`) под-плашки это именно **уровни** (`train/Level`), а не уроки. Надо заменить:

Было (например):
```vue
<p class="text-sm text-gray-500">
  {{ level.done_lessons_count }} из {{ level.total_lessons }} уроков пройдено
</p>
```

Стало:
```vue
<p class="text-sm text-gray-500">
  {{ level.done_lessons_count }} из {{ level.total_lessons }} уровней пройдено
</p>
```

**Важно:** делай замену **только в компонентах/страницах связанных с тренажёром** (там где рендерится `train.Course.levels`), не трогай обычные курсы (там действительно уроки).

Как отличить: если в data/props есть `course.title === 'Разговорный тренажёр'` или идёт работа с `$api.trainer.*` — это тренажёр. Если `$api.lessons.*` — это обычный курс.

---

## Финальная сводка

Выведи:
1. Список изменённых файлов
2. Список найденных мест использования `<CardDictionaryItem>` и где добавлен `:show_checkbox="true"`
3. Какой файл/компонент содержал «уроков пройдено» для тренажёра
4. Что НЕ сделано в этой сессии (идёт в следующих):
   - Страница Прогресса
   - Страница Профиля
   - Видео preview через thumbnail с бека

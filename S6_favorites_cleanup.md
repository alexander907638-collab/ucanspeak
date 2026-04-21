# Сессия 6 — Тарифы, избранное, чистка фронта

Контекст: S1 + S1.5 + S2 + S3 + S4 уже выполнены. Это последняя сессия фиксов перед запуском на сервере №2.

Все пути — от родительской папки:
- `ucanspeack_api-master/` — Django бэк
- `ucanspeak_front-master/` — Nuxt фронт

Цели:
- Избранное: убрать поиск, убрать Checkbox со словарных карточек, добавить кнопку «Очистить избранное» с модалкой подтверждения, кнопка действует только на текущую вкладку
- Удалить мёртвый файл `index_old.vue` в тренажёре
- Привести `pages/index.vue` в порядок (там сейчас лежит мёртвый код)
- Поправить middleware: юзер с истёкшей подпиской заперт на `/tariff` без возможности выйти
- Убрать дубль `useAuthToken` watch (мелкая оптимизация)
- НЕ трогаем тарифы — они выглядят сломанными, но это контентный баг (тестовые данные «лалаав» в БД) — клиенту просто наполнить через админку. Если в S6 окажется что в тарифах битая логика — отметим в финальной сводке.

Выполни 5 задач последовательно. После каждой — короткий отчёт.

---

## Задача 1 — избранное: убрать поиск + Checkbox + добавить «Очистить»

### 1a. Backend: bulk-эндпоинты для очистки

Файл: `ucanspeack_api-master/lesson/views.py`.

В конец файла добавь:
```python
class ClearDictionaryFavoritesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        DictionaryItemFavorite.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)


class ClearLessonItemFavoritesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        LessonItemFavoriteItem.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)
```

Импорт `APIView` уже должен быть в файле (или добавь `from rest_framework.views import APIView`). `IsAuthenticated` — `from rest_framework.permissions import IsAuthenticated`.

В файл `ucanspeack_api-master/lesson/urls.py` добавь два пути перед `+ router.urls`:
```python
path('dictionary_favorites/clear/', ClearDictionaryFavoritesAPIView.as_view()),
path('lesson_item_favorites/clear/', ClearLessonItemFavoritesAPIView.as_view()),
```

Файл: `ucanspeack_api-master/train/views.py`.

В конец добавь:
```python
class ClearTrainerFavoritesAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        PhraseFavorite.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_200_OK)
```

(Импорты `APIView`, `IsAuthenticated` — добавь если нет.)

В `ucanspeack_api-master/train/urls.py` добавь путь:
```python
path('favorites/clear/', ClearTrainerFavoritesAPIView.as_view()),
```

### 1b. Frontend repository: методы очистки

Файл: `ucanspeak_front-master/app/repository/lessons/index.ts`. Добавь в возвращаемый объект:
```typescript
clear_dictionary_favorites() {
    return appFetch('/api/lesson/dictionary_favorites/clear/', { method: 'POST' })
},
clear_lesson_item_favorites() {
    return appFetch('/api/lesson/lesson_item_favorites/clear/', { method: 'POST' })
},
```

Файл: `ucanspeak_front-master/app/repository/trainer/index.ts`. Добавь:
```typescript
clear_favorites() {
    return appFetch('/api/trainer/favorites/clear/', { method: 'POST' })
},
```

### 1c. Frontend: убрать поиск, добавить кнопку «Очистить» в текущей вкладке

Файл: `ucanspeak_front-master/app/pages/profile/favorite.vue`.

Перепиши целиком (короче и без бага):
```vue
<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

const {$api} = useNuxtApp()
const toast = useToast()

const {data: dictionary_favorites, refresh: refresh_dictionary_favorites} =
    useHttpRequest(await useAsyncData(() => $api.lessons.dictionary_favorites()))
const {data: lesson_item_favorites, refresh: refresh_lesson_item_favorites} =
    useHttpRequest(await useAsyncData(() => $api.lessons.lesson_item_favorites()))
const {data: trainer_item_favorites, refresh: refresh_trainer_item_favorites} =
    useHttpRequest(await useAsyncData(() => $api.trainer.favorites()))

const openedId = ref<number | null>(null)
const opened_dictionary_id = ref<number | null>(null)

const active_tab = ref('0')
const clear_dialog_visible = ref(false)
const clearing = ref(false)

const handleToggleOpen = (id: number) => {
  openedId.value = openedId.value === id ? null : id
}
const handleToggleDictionaryOpen = (id: number) => {
  opened_dictionary_id.value = opened_dictionary_id.value === id ? null : id
}

const handleToggleDictionaryFav = async (id: number) => {
  await $api.lessons.toggle_dictionary_favorite({ id })
  await refresh_dictionary_favorites()
}
const handlePhraseToggleFav = async (id: number) => {
  await $api.lessons.toggle_phrase_favorite({ id })
  await refresh_lesson_item_favorites()
}
const handleTrainerToggleFav = async (id: number) => {
  await $api.trainer.toggle_trainer_favorite({ id })
  await refresh_trainer_item_favorites()
}

const tabLabels: Record<string, string> = {
  '0': 'словарь',
  '1': 'фразы',
  '2': 'тренажёр',
}

const clearCurrentTab = async () => {
  clearing.value = true
  try {
    if (active_tab.value === '0') {
      await $api.lessons.clear_dictionary_favorites()
      await refresh_dictionary_favorites()
    } else if (active_tab.value === '1') {
      await $api.lessons.clear_lesson_item_favorites()
      await refresh_lesson_item_favorites()
    } else if (active_tab.value === '2') {
      await $api.trainer.clear_favorites()
      await refresh_trainer_item_favorites()
    }
    toast.add({ severity: 'success', summary: 'Готово', detail: 'Избранное очищено', life: 2500 })
    clear_dialog_visible.value = false
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось очистить избранное', life: 3000 })
  } finally {
    clearing.value = false
  }
}

const currentTabIsEmpty = computed(() => {
  if (active_tab.value === '0') return !dictionary_favorites.value || dictionary_favorites.value.length === 0
  if (active_tab.value === '1') return !lesson_item_favorites.value || lesson_item_favorites.value.length === 0
  if (active_tab.value === '2') return !trainer_item_favorites.value || trainer_item_favorites.value.length === 0
  return true
})

useSeoMeta({ title: 'Избранное' })
</script>

<template>
  <CardBase padding="md">
    <div class="flex items-center justify-between mb-6">
      <TypingText28 text="Избранное" />
      <Button
          v-if="!currentTabIsEmpty"
          @click="clear_dialog_visible = true"
          severity="danger"
          outlined
          size="small"
          icon="pi pi-trash"
          label="Очистить"
      />
    </div>

    <Tabs v-model:value="active_tab" class="relative">
      <TabList>
        <Tab value="0">Слова</Tab>
        <Tab value="1">Фразы</Tab>
        <Tab value="2">Тренажер</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-1 mb-6">
            <CardDictionaryItem
                v-if="dictionary_favorites && dictionary_favorites.length > 0"
                v-for="item in dictionary_favorites"
                :key="item.id"
                :item="item"
                dictionary_direction="ruEN"
                :opened="opened_dictionary_id === item.id"
                @toggle_open="handleToggleDictionaryOpen"
                @toggle_fav="handleToggleDictionaryFav"/>
            <p v-else class="text-sm text-gray-400 font-normal">В избранном пока ничего нет</p>
          </div>
        </TabPanel>
        <TabPanel value="1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-1 mb-6">
            <CardVoiceFile
                v-if="lesson_item_favorites && lesson_item_favorites.length > 0"
                v-for="item in lesson_item_favorites"
                :key="item.id"
                :item="item"
                :show_add_to_fav="true"
                :opened="openedId === item.id"
                @toggle_open="handleToggleOpen"
                @toggle_fav="handlePhraseToggleFav"/>
            <p v-else class="text-sm text-gray-400 font-normal w-full">В избранном пока ничего нет</p>
          </div>
        </TabPanel>
        <TabPanel value="2">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-1">
            <CardVoiceFile
                v-if="trainer_item_favorites && trainer_item_favorites.length > 0"
                v-for="item in trainer_item_favorites"
                :key="item.id"
                :item="item"
                :show_add_to_fav="true"
                :opened="openedId === item.id"
                @toggle_open="handleToggleOpen"
                @toggle_fav="handleTrainerToggleFav"/>
            <p v-else class="text-sm text-gray-400 font-normal">В избранном пока ничего нет</p>
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>

    <Dialog
        v-model:visible="clear_dialog_visible"
        modal
        header="Очистить избранное?"
        :style="{ width: '420px' }"
    >
      <p class="mb-2">
        Вы уверены, что хотите очистить избранное во вкладке <b>{{ tabLabels[active_tab] }}</b>?
      </p>
      <p class="text-sm text-gray-500">Действие нельзя отменить. Другие вкладки не затрагиваются.</p>
      <template #footer>
        <Button label="Отмена" severity="secondary" text @click="clear_dialog_visible = false" />
        <Button label="Очистить" severity="danger" :loading="clearing" @click="clearCurrentTab" />
      </template>
    </Dialog>
  </CardBase>
</template>
```

Что изменилось:
- Удалён InputGroup с поиском
- Удалена inline-плашка «Очистить избранное» только для словаря
- Кнопка «Очистить» в шапке, действует на активную вкладку
- Модалка подтверждения с явным указанием какая вкладка
- Корректное v-for (key, без ошибок mixed v-if/v-for на одном теге)

### 1d. Убрать Checkbox со словарной карточки

Файл: `ucanspeak_front-master/app/components/Card/DictionaryItem.vue`.

Найди в `<template>` строку с `<Checkbox v-model="checked" binary class="shrink-0 mt-1" />` (после S1.5 она там есть). Удали её. И в `<script setup>` удали `const checked = ref(false)`.

После правки template должен начинаться так:
```vue
<template>
  <div class="w-full">
    <div class="relative flex items-start gap-4 w-full" :class="opened ? 'min-h-[85px]' : ''">
      <div class="bg-[#EFEFF5] hover:bg-[#e9e9e9] overflow-hidden p-2.5 rounded-lg flex-1 min-w-0 max-w-full">
        ...
```

(чекбокса нет, остальное — как было после S1.5)

---

## Задача 2 — починить middleware: юзер с истёкшей подпиской

Файл: `ucanspeak_front-master/app/middleware/auth.global.ts`.

Сейчас если у юзера `is_subscription_expired === true` — middleware кидает на `/tariff` отовсюду кроме `/tariff`. Это значит юзер не может выйти из аккаунта (зайти на `/profile` нельзя), не может посмотреть демоуроки. Это слишком жёстко.

Перепиши файл так:
```typescript
export default defineNuxtRouteMiddleware(async (to, from) => {
  if (to.fullPath === '/') return navigateTo({ name: 'courses' })

  const authStore = useAuthStore()
  const { user } = storeToRefs(authStore)

  // юзер с истёкшей подпиской: пускаем только в тариф, профиль, логин
  const allowedForExpired = ['tariff', 'profile', 'profile-index', 'login', 'login-school_slug']
  if (
      user.value &&
      user.value.is_subscription_expired &&
      to.name &&
      !allowedForExpired.includes(to.name as string)
  ) {
    return navigateTo({ name: 'tariff' })
  }

  if (to.meta.auth || to.meta.guest) {
    if (to.meta.auth && !authStore.user) {
      return navigateTo({ name: 'courses' })
    } else if (to.meta.guest && authStore.user) {
      return navigateTo({ name: 'courses' })
    }
  }
})
```

(`console.log` уже удалён в S1.5, проверь что его нет)

---

## Задача 3 — удалить мёртвый код

1. Удали файл `ucanspeak_front-master/app/pages/courses/trainer/[course_slug]/[level_slug]/[topic_slug]/index_old.vue` целиком. Это старая версия страницы тренажёра, Nuxt может подхватить её как маршрут `/courses/trainer/.../index_old`.

2. Файл `ucanspeak_front-master/app/pages/index.vue` — там остался мёртвый template с ссылкой `<nuxt-link to="/auth">auth</nuxt-link>` (роута `/auth` нет). Перепиши целиком:
   ```vue
   <script setup lang="ts">
   definePageMeta({
     guest: true,
     layout: 'default'
   })
   navigateTo('/courses')
   </script>

   <template>
     <div></div>
   </template>
   ```

3. Файл `ucanspeak_front-master/app/composables/useAuthToken.ts` — убери лишний watch:
   ```typescript
   export const useAuthToken = () => {
       const token = useCookie<string | null>('auth_token')
       const reset_token = () => token.value = null
       return {
           authToken: token,
           reset_token
       }
   }
   ```
   (раньше был useState + watch — это давало двойной источник правды и потенциальную рассинхронизацию)

---

## Задача 4 — закрыть тарифную witholding регистрацию проверкой

Эту задачу не делаем — клиент сам наполнит данные тарифов через админку. На скрине были тестовые данные. Если после старта на сервере №2 всё ещё видны «лалаав» / «Первое-Второе-Третье» — посмотри в админке `/admin/lesson/tariff/`, там это просто записи, удали и наполни заново.

(Эта задача — заглушка, чтобы было ровно 5 задач в счётчике; ничего не делать)

---

## Задача 5 — фронтовая проверка типов user

Файл: `ucanspeak_front-master/app/repository/auth/types.ts`.

Сейчас тип `User` описан полями от другого проекта (`balance`, `tokens`, `is_streamer`). Это враньё типов, TypeScript ничего не валидирует. Перепиши:

```typescript
export interface User {
    id: number
    email: string
    full_name: string | null
    phone: string | null
    avatar: string | null
    is_school: boolean
    is_pupil: boolean
    is_superuser: boolean
    is_subscription_expired: boolean
    subscription_expire: string | null
    max_logins: number | null
    last_lesson_url: string | null
    school: {
        slug: string | null
        image: string | null
    } | null
}
```

Это поля которые реально отдаёт `UserSerializer` после S1 (`is_superuser`, `subscription_expire`, `is_school` уже в read_only_fields, но всё равно отдаются на чтение).

---

## Финальная сводка

Выведи:
1. Список всех изменённых и удалённых файлов
2. **Команда для Александра — выполнить вручную:**
   ```
   cd ucanspeack_api-master
   python manage.py check
   ```
   Миграции **не нужны** (добавили только endpoints, моделей не трогали). `check` должен пройти без ошибок.
3. **Чеклист ручной проверки на сервере №2 (после старта):**
   - `/profile/favorite` — нет поля поиска, нет Checkbox у словарных карточек, есть кнопка «Очистить» в шапке
   - Кнопка «Очистить» открывает модалку с указанием активной вкладки, при подтверждении очищается только эта вкладка
   - Юзер с истёкшей подпиской — может зайти на `/profile`, может выйти из аккаунта, кнопка «Продлить» работает
   - Открыть `/courses/trainer/<любой>/<любой>/<любой>/index_old` — должен быть 404 (файл удалён)
   - Открыть `/` — мгновенный редирект на `/courses`
4. Что НЕ сделано / отложено:
   - S5 — onsite-editor видеофраз (после старта сервера №2)
   - Тарифные данные — клиент сам через админку
   - Endpoint «выгнать ученика» школьным админом (заглушка из S1.5 пока показывает info-toast)

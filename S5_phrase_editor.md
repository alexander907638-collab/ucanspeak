# Сессия 5 — Onsite-editor видеофраз: модалка правки + drag-and-drop порядка

Контекст: S1 + S1.5 + S2 + S3 + S4 + S6 уже выполнены. Эта сессия — единственная пока что фича где админ редактирует контент **без ухода в Django admin**.

Все пути — от родительской папки:
- `ucanspeack_api-master/` — Django бэк
- `ucanspeak_front-master/` — Nuxt фронт

Цели:
- На странице урока в видео-плеере (`<BlockVideoWithPreview>`) если юзер `is_superuser` — рядом с каждой фразой кнопка-карандаш «Редактировать фразу». По клику открывается модалка с полями `text_ru`, `text_en`, `start_time`, `end_time`, кнопками Сохранить/Удалить/Отмена.
- Под списком фраз (только для админа) — кнопка «Изменить порядок». По клику включается режим drag-and-drop (фразы можно перетаскивать). Кнопка «Сохранить порядок» — отправляет новый порядок на бэк одним запросом.

Бэк-часть:
- Снять ограничение `http_method_names = ['get', 'head', 'options', 'post']` с `PhraseViewSet` (после S1) — разрешить PATCH/DELETE
- Permission на write-методы: `[IsAdminUser]`
- Endpoint `POST /api/lesson/videos/<id>/reorder_phrases/` с body `{ids: [1,2,3,...]}` для массового update `order`

Выполни 5 задач последовательно.

---

## Задача 1 — снять ограничения с PhraseViewSet, добавить permissions

Файл: `ucanspeack_api-master/lesson/views.py`.

В классе `PhraseViewSet` (после S1 он `ModelViewSet` с `http_method_names=['get','head','options','post']` и `IsAuthenticatedOrReadOnly`):

1. **Удали** строку `http_method_names = ['get', 'head', 'options', 'post']` если она есть в `PhraseViewSet`. Тем самым PATCH/DELETE снова доступны.
2. **Замени** `permission_classes = [IsAuthenticatedOrReadOnly]` на:
   ```python
   def get_permissions(self):
       if self.action in ('list', 'retrieve'):
           return [permissions.AllowAny()]
       return [permissions.IsAdminUser()]
   ```
3. Добавь импорт сверху файла если ещё нет: `from rest_framework import permissions`.

Это даёт: GET — всем, PATCH/DELETE/PUT — только пользователям с `is_staff=True` (стандартное `IsAdminUser` в DRF проверяет `is_staff`).

**Проверь** что в `User` модели админы помечены `is_staff=True`. По умолчанию superuser имеет `is_staff=True`, обычный юзер — нет. То есть `is_superuser=True` означает доступ к редактированию (через is_staff). Если на проекте у админов `is_staff=False, is_superuser=True` — это редкость, но проверь у текущих админов в БД.

---

## Задача 2 — endpoint reorder_phrases в VideoViewSet

В том же файле `ucanspeack_api-master/lesson/views.py` найди класс `VideoViewSet`. Добавь action:

```python
@action(detail=True, methods=['post'], url_path='reorder_phrases',
        permission_classes=[permissions.IsAdminUser])
def reorder_phrases(self, request, pk=None):
    """
    Body: {"ids": [3, 1, 2, 4]}
    Принимает список ID фраз в новом порядке.
    Все фразы должны принадлежать этому видео — иначе 400.
    """
    video = self.get_object()
    ids = request.data.get('ids', [])
    if not isinstance(ids, list) or not all(isinstance(i, int) for i in ids):
        return Response({"detail": "ids должен быть списком целых чисел"},
                        status=status.HTTP_400_BAD_REQUEST)

    video_phrase_ids = set(video.phrases.values_list('id', flat=True))
    if set(ids) != video_phrase_ids:
        return Response({
            "detail": "Список ids должен содержать ровно все фразы этого видео"
        }, status=status.HTTP_400_BAD_REQUEST)

    # массовое обновление одним запросом через CASE
    from django.db.models import Case, When, IntegerField, Value
    cases = [When(id=phrase_id, then=Value(idx)) for idx, phrase_id in enumerate(ids)]
    Phrase.objects.filter(id__in=ids).update(
        order=Case(*cases, output_field=IntegerField())
    )

    return Response({"detail": "Порядок обновлён"}, status=status.HTTP_200_OK)
```

Проверь что в импортах есть `Phrase`, `status`, `Response`, `action`. После S1 все эти импорты должны быть.

Также в `VideoViewSet` сними `http_method_names` если есть, добавь `get_permissions` по той же схеме (GET — всем, write — IsAdminUser):
```python
def get_permissions(self):
    if self.action in ('list', 'retrieve'):
        return [permissions.AllowAny()]
    return [permissions.IsAdminUser()]
```

---

## Задача 3 — frontend repository: методы редактирования фраз

Файл: `ucanspeak_front-master/app/repository/lessons/index.ts`. Добавь в возвращаемый объект:

```typescript
update_phrase(id: number, body: any) {
    return appFetch(`/api/lesson/phrases/${id}/`, {
        method: 'PATCH',
        body
    })
},
delete_phrase(id: number) {
    return appFetch(`/api/lesson/phrases/${id}/`, {
        method: 'DELETE'
    })
},
reorder_phrases(video_id: number, ids: number[]) {
    return appFetch(`/api/lesson/videos/${video_id}/reorder_phrases/`, {
        method: 'POST',
        body: { ids }
    })
},
```

---

## Задача 4 — модалка PhraseEditDialog

Создай новый файл: `ucanspeak_front-master/app/components/Modal/PhraseEditDialog.vue`.

Содержимое:

```vue
<script setup lang="ts">
import { useToast } from 'primevue/usetoast'

const toast = useToast()
const {$api} = useNuxtApp()

const props = defineProps<{
  visible: boolean
  phrase: {
    id: number
    text_ru: string | null
    text_en: string | null
    start_time: string | null
    end_time: string | null
  } | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'saved'): void
  (e: 'deleted', id: number): void
}>()

const form = ref({
  text_ru: '',
  text_en: '',
  start_time: '',
  end_time: '',
})

const saving = ref(false)
const deleting = ref(false)
const delete_confirm_visible = ref(false)

watch(() => props.phrase, (val) => {
  if (val) {
    form.value = {
      text_ru: val.text_ru || '',
      text_en: val.text_en || '',
      start_time: val.start_time || '',
      end_time: val.end_time || '',
    }
  }
}, { immediate: true })

const close = () => emit('update:visible', false)

const save = async () => {
  if (!props.phrase) return
  saving.value = true
  try {
    await $api.lessons.update_phrase(props.phrase.id, form.value)
    toast.add({ severity: 'success', summary: 'Сохранено', detail: 'Фраза обновлена', life: 2000 })
    emit('saved')
    close()
  } catch (e: any) {
    const detail = e?.data?.detail
        || (e?.data && typeof e.data === 'object' ? JSON.stringify(e.data) : 'Ошибка сохранения')
    toast.add({ severity: 'error', summary: 'Ошибка', detail, life: 4000 })
  } finally {
    saving.value = false
  }
}

const askDelete = () => {
  delete_confirm_visible.value = true
}

const doDelete = async () => {
  if (!props.phrase) return
  deleting.value = true
  try {
    await $api.lessons.delete_phrase(props.phrase.id)
    toast.add({ severity: 'success', summary: 'Удалено', detail: 'Фраза удалена', life: 2000 })
    emit('deleted', props.phrase.id)
    delete_confirm_visible.value = false
    close()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось удалить', life: 3000 })
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <Dialog
      :visible="visible"
      @update:visible="(v) => emit('update:visible', v)"
      modal
      header="Редактировать фразу"
      :style="{ width: '520px' }"
  >
    <div class="space-y-3 pt-2">
      <UIInput
          fluid
          label="Текст на русском"
          id="phrase_text_ru"
          v-model="form.text_ru"
      />
      <UIInput
          fluid
          label="Текст на английском"
          id="phrase_text_en"
          v-model="form.text_en"
      />
      <div class="grid grid-cols-2 gap-3">
        <UIInput
            fluid
            label="Начало (HH.MM.SS)"
            id="phrase_start"
            placeholder="00.00.00"
            v-model="form.start_time"
        />
        <UIInput
            fluid
            label="Конец (HH.MM.SS)"
            id="phrase_end"
            placeholder="00.00.00"
            v-model="form.end_time"
        />
      </div>
      <p class="text-xs text-gray-500">
        Формат таймкода — точки, не двоеточия. Пример: <code>00.01.23</code>
      </p>
    </div>

    <template #footer>
      <div class="flex justify-between w-full">
        <Button
            label="Удалить"
            severity="danger"
            text
            icon="pi pi-trash"
            @click="askDelete"
        />
        <div class="flex gap-2">
          <Button label="Отмена" severity="secondary" text @click="close" />
          <Button label="Сохранить" :loading="saving" @click="save" />
        </div>
      </div>
    </template>
  </Dialog>

  <Dialog
      v-model:visible="delete_confirm_visible"
      modal
      header="Удалить фразу?"
      :style="{ width: '380px' }"
  >
    <p>Действие нельзя отменить.</p>
    <template #footer>
      <Button label="Отмена" severity="secondary" text @click="delete_confirm_visible = false" />
      <Button label="Удалить" severity="danger" :loading="deleting" @click="doDelete" />
    </template>
  </Dialog>
</template>
```

---

## Задача 5 — интеграция в BlockVideoWithPreview

Файл: `ucanspeak_front-master/app/components/Block/VideoWithPreview.vue`.

Это большой файл (331 строка). Нужно добавить:
- Кнопка-карандаш возле каждой фразы в списке `visiblePhrases` (показывается админу)
- Кнопка «Изменить порядок» под списком (показывается админу)
- Режим reorder: фразы становятся sortable, появляется кнопка «Сохранить порядок» / «Отмена»
- Подключить `<ModalPhraseEditDialog>`

В `<script setup lang="ts">` добавь импорты и состояние (после существующих ref'ов):

```typescript
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const phrase_edit_visible = ref(false)
const phrase_being_edited = ref<any>(null)

const reorder_mode = ref(false)
const reorder_saving = ref(false)
const reorder_buffer = ref<any[]>([])

const openPhraseEdit = (phrase: any) => {
  phrase_being_edited.value = phrase
  phrase_edit_visible.value = true
}

const onPhraseSaved = () => {
  // обновим локальные данные — мутируем фразу в массиве
  // на самом деле проще пере-фетчить родителя, но т.к. данные приходят пропсом — мутируем здесь
  // фронт тут SPA-стейтовая, при следующем заходе на страницу подхватится свежий список
}

const onPhraseDeleted = (id: number) => {
  phrases.value = phrases.value.filter(p => p.id !== id)
}

const startReorder = () => {
  reorder_buffer.value = [...phrases.value]
  reorder_mode.value = true
}

const cancelReorder = () => {
  reorder_mode.value = false
  reorder_buffer.value = []
}

const moveItem = (idx: number, direction: -1 | 1) => {
  const newIdx = idx + direction
  if (newIdx < 0 || newIdx >= reorder_buffer.value.length) return
  const arr = [...reorder_buffer.value]
  ;[arr[idx], arr[newIdx]] = [arr[newIdx], arr[idx]]
  reorder_buffer.value = arr
}

const saveReorder = async () => {
  reorder_saving.value = true
  try {
    const ids = reorder_buffer.value.map(p => p.id)
    // video_id берём из props.data — у Video модели должен быть id
    // если нет — через первую фразу: phrases[0].video_id (зависит от сериализатора)
    const video_id = (props.data as any).id
    if (!video_id) {
      throw new Error('video_id не найден в data')
    }
    await $api.lessons.reorder_phrases(video_id, ids)
    phrases.value = [...reorder_buffer.value]
    reorder_mode.value = false
  } catch (e) {
    console.error('reorder error', e)
    alert('Не удалось сохранить порядок')
  } finally {
    reorder_saving.value = false
  }
}
```

В `<template>` найди существующий блок где рендерится `visiblePhrases` через `<CardVoiceFile>` (около строки 300-310). Замени на условный рендер:

**Вместо текущего блока:**
```vue
<div v-if="isPaused && !isFullscreen" class="relative">
  <transition-group name="fade" tag="div" class="bottom-0 left-0 right-0 p-4 space-y-2 flex flex-col">
    <CardVoiceFile
        v-for="item in visiblePhrases"
        :key="item.id"
        :item="item"
        :reverse="true"
        :show_add_to_fav="false"
        :opened="openedId === item.id"
        :loading="fav_loading"
        @toggle_open="handleToggleOpen"
    />
  </transition-group>
</div>
```

**Сделай так:**
```vue
<div v-if="(isPaused || reorder_mode) && !isFullscreen" class="relative">
  <!-- админ-режим reorder: пронумерованные строки со стрелками -->
  <div v-if="reorder_mode" class="p-4 space-y-2">
    <div
        v-for="(item, idx) in reorder_buffer"
        :key="item.id"
        class="flex items-center gap-2 p-2 bg-[#F6F6FB] rounded-lg"
    >
      <div class="flex flex-col gap-1">
        <button
            @click="moveItem(idx, -1)"
            :disabled="idx === 0"
            class="text-xs px-2 py-0.5 bg-white rounded disabled:opacity-30"
        >▲</button>
        <button
            @click="moveItem(idx, 1)"
            :disabled="idx === reorder_buffer.length - 1"
            class="text-xs px-2 py-0.5 bg-white rounded disabled:opacity-30"
        >▼</button>
      </div>
      <div class="flex-1">
        <div class="text-sm font-medium">{{ item.text_en }}</div>
        <div class="text-xs text-gray-500">{{ item.text_ru }}</div>
        <div class="text-xs text-gray-400">{{ item.start_time }} → {{ item.end_time }}</div>
      </div>
    </div>
    <div class="flex gap-2 pt-2">
      <Button
          label="Сохранить порядок"
          severity="success"
          :loading="reorder_saving"
          @click="saveReorder"
      />
      <Button
          label="Отмена"
          severity="secondary"
          text
          @click="cancelReorder"
      />
    </div>
  </div>

  <!-- обычный режим просмотра фраз -->
  <transition-group v-else name="fade" tag="div" class="bottom-0 left-0 right-0 p-4 space-y-2 flex flex-col">
    <div
        v-for="item in visiblePhrases"
        :key="item.id"
        class="flex items-center gap-2"
    >
      <CardVoiceFile
          :item="item"
          :reverse="true"
          :show_add_to_fav="false"
          :opened="openedId === item.id"
          :loading="fav_loading"
          @toggle_open="handleToggleOpen"
          class="flex-1"
      />
      <Button
          v-if="user && user.is_superuser"
          icon="pi pi-pencil"
          severity="secondary"
          outlined
          size="small"
          @click="openPhraseEdit(item)"
      />
    </div>
  </transition-group>

  <!-- кнопка переключения в режим reorder -->
  <div
      v-if="user && user.is_superuser && !reorder_mode && phrases.length > 1"
      class="px-4 pb-2"
  >
    <Button
        label="Изменить порядок"
        severity="secondary"
        outlined
        size="small"
        icon="pi pi-sort"
        @click="startReorder"
    />
  </div>
</div>

<ModalPhraseEditDialog
    v-model:visible="phrase_edit_visible"
    :phrase="phrase_being_edited"
    @saved="onPhraseSaved"
    @deleted="onPhraseDeleted"
/>
```

**Важно:** в существующем `<script setup>` есть `const phrases = ref(props.data.phrases)` — это уже есть, не дублируй. Используй именно его.

**Проверка:** компонент `<ModalPhraseEditDialog>` Nuxt подцепит автоматически благодаря auto-import (он лежит в `components/Modal/`).

---

## Финальная сводка

Выведи:
1. Список изменённых файлов
2. **Команда для Александра — выполнить вручную:**
   ```
   cd ucanspeack_api-master
   python manage.py check
   ```
   Миграции **не нужны** (только views и serializers, моделей не трогали).
3. **Чеклист ручной проверки на сервере №2 (после старта):**
   - Залогиниться суперюзером
   - Открыть любой урок где есть видео с фразами, развернуть видео-плеер, поставить на паузу — увидеть список фраз
   - Возле каждой фразы — карандаш. Клик — открывается модалка с полями ru/en/start/end
   - Изменить текст, нажать «Сохранить» — toast «Сохранено», при перезаходе изменения остались
   - Нажать «Удалить» в модалке — модалка-подтверждение, после Подтвердить — фраза исчезает из списка
   - Под списком фраз — кнопка «Изменить порядок». Клик — список перерендеривается со стрелками вверх/вниз
   - Перемещать стрелками, нажать «Сохранить порядок» — изменения уходят на бэк, при перезаходе порядок остался
   - Залогиниться обычным юзером (не staff/не superuser) — никаких карандашей, никакой кнопки «Изменить порядок»
   - Попытаться через консоль браузера сделать `fetch('/api/lesson/phrases/<id>/', {method: 'PATCH', ...})` от обычного юзера — должна вернуться 403 Forbidden
4. Что НЕ сделано / отложено:
   - Загрузка нового MP3 для фразы — не входит в B
   - Добавление новой фразы прямо с фронта — не входит в B
   - Аналогичный редактор для `LessonItem` и `DictionaryItem` — отложено

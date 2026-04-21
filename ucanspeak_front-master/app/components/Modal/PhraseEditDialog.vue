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

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

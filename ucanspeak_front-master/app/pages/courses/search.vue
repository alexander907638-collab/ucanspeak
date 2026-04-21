<script setup lang="ts">
const {$api} = useNuxtApp()
const {data:dictionary_favorites,refresh:refresh_dictionary_favorites} = useHttpRequest(await useAsyncData(()=>$api.lessons.dictionary_favorites()))
const {data:lesson_item_favorites,refresh:refresh_lesson_item_favorites} = useHttpRequest(await useAsyncData(()=>$api.lessons.lesson_item_favorites()))
const {data:trainer_item_favorites,refresh:refresh_trainer_item_favorites} = useHttpRequest(await useAsyncData(()=>$api.trainer.favorites()))
const openedId = ref<number | null>(null)
const loading = ref(false)
const result = ref([])
const q = ref('')
const dictionary_direction = computed(() => {
  // Если в строке есть кириллица — запрос русский, ответ английский
  const hasCyrillic = /[а-яё]/i.test(q.value)
  return hasCyrillic ? 'ruEN' : 'enRU'
})
const opened_dictionary_id = ref<number | null>(null)
const handleToggleOpen = (id: number) => {
  openedId.value = openedId.value === id ? null : id
}
const handleToggleDictionaryOpen = (id: number) => {
  opened_dictionary_id.value = opened_dictionary_id.value === id ? null : id
}

const search = async () => {
  loading.value = true
  result.value = await $api.lessons.search(q.value)

  loading.value = false
}


const handleToggleDictionaryFav = async (id) => {
  await $api.lessons.toggle_dictionary_favorite({
    id: id
  })
  await refresh_dictionary_favorites()
}
const handlePhraseToggleFav = async (id) => {
  await $api.lessons.toggle_phrase_favorite({
    id: id
  })
  await refresh_lesson_item_favorites()
}
const handleTrainerToggleFav = async (id) => {
  await $api.trainer.toggle_trainer_favorite({
    id: id
  })
  await refresh_trainer_item_favorites()
}
useSeoMeta({
  title: `Поиск `,
})
</script>

<template>
  <BlockBaseBreadcrumbs
      :items="[
    { label: 'Главная', to: '/' },
    { label: 'Результаты поиска' },
  ]"/>
  <TypingText48 text="Поиск" class="mb-10"/>


  <CardBase padding="sm" class="space-y-3">
    <InputGroup>
      <InputGroupAddon>
        <i class="pi pi-search"></i>
      </InputGroupAddon>
      <InputText :disabled="loading" v-model="q" @keydown.enter="search" placeholder="Поиск" />
    </InputGroup>
<!--    <p class="text-gray-400">Найдено 135 результатов</p>-->
    <Tabs value="0" class="relative">

      <TabList>
        <Tab value="0">Слова</Tab>
        <Tab value="1">Фразы</Tab>
        <Tab value="2">Тренажер</Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="0">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-1 mb-6">
            <div class="flex items-center gap-2" v-for="item in result.dictionary">
              <CardDictionaryItem
                  :item="item"
                  :dictionary_direction="dictionary_direction"
                  :opened="opened_dictionary_id === item.id"
                  @toggle_open="handleToggleDictionaryOpen"
                  @toggle_fav="handleToggleDictionaryFav"/>

              <a target="_blank" :href="`/courses/${item.group__lesson__level__course__slug}/${item.group__lesson__level__slug}/${item.group__lesson__slug}`">
                <i class="pi pi-link"></i>
              </a>
            </div>



          </div>
        </TabPanel>
        <TabPanel value="1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-1 mb-6">
            <div class="flex items-center gap-2" v-for="item in result.phrases">
            <CardVoiceFile
                           :key="item.id"
                           :item="item"
                           :show_add_to_fav="true"
                           :opened="openedId === item.id"
                           @toggle_open="handleToggleOpen"
                           @toggle_fav="handlePhraseToggleFav"/>
              <a target="_blank" :href="`/courses/${item.video__block__module__lesson__level__course__slug}/${item.video__block__module__lesson__level__slug}/${item.video__block__module__lesson__slug}`">
                <i class="pi pi-link"></i>
              </a>
            </div>


          </div>
        </TabPanel>
        <TabPanel value="2">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-1 ">
            <div class="flex items-center gap-2" v-for="item in result.trainer_phrases">
            <CardVoiceFile
                           :key="item.id"
                           :item="item"
                        :show_add_to_fav="true"
                           :opened="openedId === item.id"
                           @toggle_open="handleToggleOpen"
                           @toggle_fav="handleTrainerToggleFav"/>
              <a target="_blank" :href="`/courses/trainer/${item.topic__level__course__slug}/${item.topic__level__slug}/${item.topic__slug}`">
                <i class="pi pi-link"></i>
              </a>
            </div>
          </div>
        </TabPanel>
      </TabPanels>
    </Tabs>
  </CardBase>

</template>

<style scoped>

</style>
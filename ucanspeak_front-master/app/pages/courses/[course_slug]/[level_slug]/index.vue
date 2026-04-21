<!--level_slug-->
<script setup lang="ts">
const completed  = ref(false)
const {level_slug}  = useRoute().params
const {$api} = useNuxtApp()
const {data:level,pending} = useHttpRequest(await useAsyncData(()=>$api.lessons.level(level_slug)))
useSeoMeta({
  title: `${level.value.title} `,
})

const headerText = useState('header_text')
headerText.value = level.value?.title
</script>

<template>
  <BlockBaseBreadcrumbs
      :items="[
    { label: 'Главная', to: '/' },
    { label: 'Курсы', to: '/courses' },
    { label: level.course?.course_title, to: `/courses/${level.course?.course_slug}` },
    { label: level.title },
  ]"
  />

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2  pb-20">
    <CardLesson
        v-for="(lesson, i) in level.lessons"
        :key="i"
        :lesson="lesson"
    />
  </div>
</template>

<style scoped>

</style>
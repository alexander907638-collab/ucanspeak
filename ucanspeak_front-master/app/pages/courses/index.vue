<script setup lang="ts">
const {$api} = useNuxtApp()
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
if (user.value) await $api.auth.me()
const {data:courses,pending} = useHttpRequest(await useAsyncData(()=>$api.lessons.courses()))
useSeoMeta({
  title: `Курсы `,
})
const headerText = useState('header_text')
headerText.value = null
</script>

<template>
  <BlockBaseBreadcrumbs
      :items="[
    { label: 'Главная', to: '/' },
    { label: 'Курсы' },
  ]"
  />

      <div class="grid  grid-cols-1 lg:grid-cols-3 gap-2 sm:gap-6 pb-20 md:pb-0">
        <CardTrainer/>
        <CardCourse v-for="course in courses" :key="course.id" :course="course" />

      </div>

</template>
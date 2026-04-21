<!--course_slug-->
<script setup lang="ts">
const route = useRoute()
const {$api} = useNuxtApp()
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
const {data:course,pending} = useHttpRequest(await useAsyncData(
    () => `course-${route.params.course_slug}`,
    () => $api.lessons.course(route.params.course_slug),
    { watch: [() => route.params.course_slug] }
))
useSeoMeta({
  title: `${course.value.title} `,
})
</script>

<template>
  <BlockCourseHeader :title="course.title" :count="course?.levels.length" show_profile/>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-2 lg:gap-5">
      <NuxtLink v-for="level in course.levels"  :to="`/courses/${course.slug}/${level.slug}`"
                class="flex items-start gap-4 p-3 bg-white border border-[#18181b]/10 rounded-[20px]">
        <div class="shrink-0 w-16 h-16 flex items-center justify-center rounded-[10px]  border border-[18181b]/[0.5]">
          <img :src="level.icon" alt="" class="">
        </div>
        <div class="w-full flex flex-col">
          <div class="flex items-center">
            <span class="font-bold text-lg leading-[130%] text-[#2c2c2c] uppercase">{{level.title}}</span>

          </div>

          <div class="font-medium text-sm leading-[130%] text-[#778]">{{level.description}}</div>
          <div v-if="user">
            <UIPLine v-if="!user.is_pupil" :value="level.progress" class="my-[5px]"/>
            <p v-if="!user.is_pupil" class="font-normal text-xs leading-[130%] text-[#8f8fa3]">{{level.done_lessons_count}} из {{level.lessons_count}} уроков пройдено</p>

          </div>
          <div v-else>
            <UIPLine  :value="0" class="my-[5px]"/>
            <p  class="font-normal text-xs leading-[130%] text-[#8f8fa3]">0 из {{level.lessons_count}} уроков пройдено</p>

          </div>

        </div>
      </NuxtLink>
  </div>
</template>

<style scoped>

</style>
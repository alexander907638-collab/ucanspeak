<!--trainer course slug index-->
<script setup lang="ts">
const {$api} = useNuxtApp()
const {course_slug} = useRoute().params
const {data:levels_data,pending:pending} = useHttpRequest(await useAsyncData(()=>$api.trainer.course(course_slug)))
useSeoMeta({
  title: `${levels_data.value.course?.name}`,
})
const headerText = useState('header_text')
headerText.value = levels_data.value.course?.name
</script>

<template>

  <div class="grid grid-cols-1 lg:grid-cols-3 gap-2 pb-20">
    <NuxtLink v-for="level in levels_data.levels"  :to="`/courses/trainer/${course_slug}/${level.slug}`"
              class="flex  items-center gap-4 p-3 bg-white border border-[#18181b]/10 rounded-[20px]">
      <div class="shrink-0 w-16 h-16 flex items-center justify-center rounded-[10px]  border border-[18181b]/[0.5]">
        <img :src="level.icon" alt="" class="">
      </div>
      <div class="w-full flex flex-col gap-[3px]">

        <div class="font-bold text-lg leading-[130%] text-black">{{level.name}}</div>
        <p class="font-normal text-sm leading-[130%] text-[#8f8fa3]">{{level.description}} </p>
        <UIEditAdminBtn
          app="train"
          model="level"
          :id="level.id"
          class="mt-2"
        />

      </div>
    </NuxtLink>
  </div>
</template>

<style scoped>

</style>
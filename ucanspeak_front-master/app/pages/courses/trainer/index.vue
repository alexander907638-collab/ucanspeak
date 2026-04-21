<!--trainer index-->
<script setup lang="ts">
const {$api} = useNuxtApp()
const {data:trainer,pending:pending} = useHttpRequest(await useAsyncData(()=>$api.trainer.courses()))
useSeoMeta({
  title: `Тренажер`,
})
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
</script>

<template>
  <BlockBaseBreadcrumbs
      :items="[
    { label: 'Главная', to: '/' },
    { label: 'Тренажер' },
  ]"
  />
  <div class="block lg:hidden  text-white left-3 top-3 rounded-lg px-3 py-4 mb-3 bg-[#9A519F]" >
    <p class="font-medium  text-[16px]">Разговорный тренажер</p>
  </div>
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-2 md:gap-5">

    <NuxtLink v-for="course in trainer"  :to="`/courses/trainer/${course.slug}`" class="flex items-center gap-4 p-3 bg-white border border-[#18181b]/10 rounded-[20px]">
      <div class="shrink-0 w-16 h-16 flex items-center justify-center rounded-[10px]  border border-[18181b]/[0.5]">
        <img :src="course.icon" alt="" class="">
      </div>
      <div class="w-full flex flex-col ">

        <div class="font-bold text-[14px] leading-[130%] text-[#2c2c2c] uppercase">{{course.name}}</div>
        <p class="font-medium text-xs leading-[130%] text-[#778]">{{course.description}} </p>
        <div v-if="user">

          <UIPLine v-if="!user.is_pupil"
                   progress_bg_color="#F2F2FD"
                   progress_color ="#8B8BF2"
                   :value="course.progress_percentage"
                   class="my-[5px]"/>
          <p v-if="!user.is_pupil" class="font-normal text-xs leading-[130%] text-[#8f8fa3]">{{course.completed_levels}} из {{course.total_levels}} уроков пройдено</p>

        </div>
        <div v-else>
          <UIPLine
              progress_bg_color="#F2F2FD"
              progress_color ="#8B8BF2"
              :value="10" class="my-[5px]"/>
          <p class="font-normal text-xs leading-[130%] text-[#8f8fa3]">0 из {{course.total_levels}} уровней пройдено</p>

        </div>
        <UIEditAdminBtn
          app="train"
          model="course"
          :id="course.id"
          class="mt-2"
        />

      </div>
    </NuxtLink>

  </div>
</template>
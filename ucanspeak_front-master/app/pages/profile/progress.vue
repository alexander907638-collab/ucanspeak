<script setup lang="ts">
const {$api} = useNuxtApp()
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
const {data: courses, pending} = useHttpRequest(await useAsyncData(() => $api.lessons.courses()))
const {data: trainer_courses} = useHttpRequest(await useAsyncData(() => $api.trainer.courses()))

useSeoMeta({title: 'Прогресс'})
</script>

<template>
  <CardBase padding="md">
    <BlockBaseBreadcrumbs :items="[{label: 'Главная', to: '/'}, {label: 'Прогресс'}]"/>
    <TypingText28 text="Прогресс" class="mb-6"/>

    <div class="space-y-8">

      <!-- Тренажёр -->
      <section v-if="trainer_courses && trainer_courses.length">
        <h2 class="text-base font-semibold text-gray-800 mb-3">Разговорный тренажёр</h2>
        <div class="space-y-2">
          <template v-for="course in trainer_courses" :key="'tr_' + course.id">
            <NuxtLink
                v-for="level in course.levels"
                :key="'tr_lvl_' + level.id"
                :to="`/courses/trainer/${course.slug}/${level.slug}`"
                class="flex items-center gap-4 p-[10px] bg-white border border-[#18181b]/10 rounded-[20px] hover:border-[#7575F0] transition"
            >
              <div class="shrink-0 w-16 h-16 flex items-center justify-center rounded-[10px] border border-[#18181b]/10 bg-gray-50 overflow-hidden">
                <img v-if="level.icon" :src="level.icon" alt="" class="max-w-full max-h-full object-contain">
              </div>
              <div class="w-full flex flex-col">
                <span class="font-bold text-[14px] leading-[130%] text-[#2c2c2c] uppercase">{{ course.name }}</span>
                <div class="font-medium text-xs leading-[130%] text-[#778]">{{ level.title }}</div>
                <div v-if="user && !user.is_pupil">
                  <UIPLine
                      progress_bg_color="#F2F2FD"
                      progress_color="#8B8BF2"
                      :value="level.progress || 0"
                      class="my-[5px]"
                  />
                  <p class="font-normal text-xs leading-[130%] text-[#8f8fa3]">
                    {{ level.done_lessons_count || 0 }} из {{ level.lessons_count || 0 }} уровней пройдено
                  </p>
                </div>
              </div>
            </NuxtLink>
          </template>
        </div>
      </section>

      <!-- Курсы -->
      <section v-if="courses && courses.length">
        <h2 class="text-base font-semibold text-gray-800 mb-3">Курсы</h2>
        <div class="space-y-2">
          <template v-for="course in courses" :key="course.id">
            <NuxtLink
                v-for="level in course.levels"
                :key="'lvl_' + level.id"
                :to="`/courses/${course.slug}/${level.slug}`"
                class="flex items-center gap-4 p-[10px] bg-white border border-[#18181b]/10 rounded-[20px] hover:border-[#7575F0] transition"
            >
              <div class="shrink-0 w-16 h-16 flex items-center justify-center rounded-[10px] border border-[#18181b]/10 bg-gray-50 overflow-hidden">
                <img v-if="level.icon" :src="level.icon" alt="" class="max-w-full max-h-full object-contain">
              </div>
              <div class="w-full flex flex-col">
                <div class="flex items-center">
                  <span class="font-bold text-[14px] leading-[130%] text-[#2c2c2c] uppercase">{{ course.title }}</span>
                </div>
                <div class="font-medium text-xs leading-[130%] text-[#778]">{{ level.title }}</div>
                <p class="font-normal text-xs leading-[130%] text-[#8f8fa3]">{{ level.description }}</p>
                <div v-if="user && !user.is_pupil">
                  <UIPLine
                      :value="level.progress || 0"
                      :progress_bg_color="course.progress_bg_color"
                      :progress_color="course.progress_color"
                      class="my-[5px]"
                  />
                  <p class="font-normal text-xs leading-[130%] text-[#8f8fa3]">
                    {{ level.done_lessons_count }} из {{ level.lessons_count }} уроков пройдено
                  </p>
                </div>
              </div>
            </NuxtLink>
          </template>
        </div>
      </section>

      <!-- Empty state -->
      <div v-if="(!courses || !courses.length) && (!trainer_courses || !trainer_courses.length)"
           class="text-center py-12">
        <p class="text-gray-500">Начните проходить уроки чтобы увидеть прогресс</p>
        <NuxtLink to="/courses" class="inline-block mt-3 text-[#7575F0] hover:underline font-medium text-sm">
          К курсам →
        </NuxtLink>
      </div>

    </div>
  </CardBase>
</template>

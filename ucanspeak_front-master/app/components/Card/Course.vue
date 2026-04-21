<script setup lang="ts">
const props = defineProps(['course'])
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
</script>

<template>

  <div class="flex flex-col gap-2">
    <div @click="$router.push(`/courses/${course.slug}`)" class="hidden lg:flex h-[200px] lg:h-[240px] xl:h-[300px] w-full rounded-2xl overflow-hidden relative z-[1] items-end border border-solid border-[rgba(24,24,27,0.05)]">
      <div class="absolute  text-white left-3 top-3 rounded-lg px-3 py-[6px] " :style="{'background':course.bg_color}">
        <p class="font-medium  text-sm md:text-[16px]">{{course.title}}</p>

      </div>
      <img :src="course.cover" alt="" class="absolute z-[-1] left-0 top-0 w-full h-full  object-cover">
      <div class="w-full bg-gr p-3 pt-[5px] sm:pt-5 sm:px-6 sm:pb-6 text-base sm:text-[28px] font-semibold leading-[130%] text-white">
<!--        <nuxt-link :to="`/courses/${course.slug}`" class="flex sm:hidden items-center justify-center w-full h-9 gap-1 bg-white text-sm text-[#3333E8] rounded-lg mt-2">-->
<!--          <span>Перейти</span>-->
<!--          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">-->
<!--            <path d="M5.22149 3.6261C5.06365 3.42751 4.98719 3.17635 5.00759 2.92349C5.02799 2.67064 5.14372 2.43499 5.33135 2.26426C5.51899 2.09354 5.76449 2.0005 6.01814 2.004C6.27179 2.0075 6.51464 2.10727 6.69749 2.2831L6.78249 2.3761L10.7825 7.3761C10.9108 7.53659 10.9865 7.73269 10.9994 7.93774C11.0122 8.14278 10.9617 8.34682 10.8545 8.5221L10.7825 8.6261L6.78249 13.6261C6.62382 13.8255 6.39502 13.9568 6.14282 13.9932C5.89061 14.0296 5.63403 13.9683 5.42547 13.8219C5.2169 13.6755 5.0721 13.455 5.02062 13.2054C4.96914 12.9559 5.01488 12.6961 5.14849 12.4791L5.22049 12.3761L8.72149 8.0011L5.22149 3.6261Z" fill="#3333E8" />-->
<!--          </svg>-->
<!--        </nuxt-link>-->
      </div>
    </div>

    <div class="block lg:hidden  text-white left-3 top-3 rounded-lg px-3 py-4 " :style="{'background':course.bg_color}">
      <p class="font-medium  text-[16px]">{{course.title}}</p>
    </div>

    <NuxtLink v-for="level in course.levels"  :to="`/courses/${course.slug}/${level.slug}`" class="flex items-center gap-4 p-[10px] bg-white border border-[#18181b]/10 rounded-[20px]">

        <img :src="level.icon" alt="" class="">

      <div class="w-full flex flex-col ">
        <div class="flex items-center">
          <span class="font-bold text-[14px] leading-[130%] text-[#2c2c2c] uppercase">{{level.title}}</span>
<!--          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">-->
<!--            <path d="M6.52686 4.53165C6.32957 4.28341 6.23399 3.96946 6.25949 3.65339C6.28499 3.33732 6.42965 3.04275 6.66419 2.82935C6.89873 2.61595 7.20561 2.49965 7.52268 2.50403C7.83974 2.5084 8.1433 2.63311 8.37186 2.8529L8.47811 2.96915L13.4781 9.21915C13.6384 9.41976 13.7331 9.66489 13.7492 9.92119C13.7653 10.1775 13.7021 10.4325 13.5681 10.6516L13.4781 10.7816L8.47811 17.0316C8.27978 17.2809 7.99378 17.445 7.67852 17.4905C7.36327 17.536 7.04253 17.4594 6.78183 17.2764C6.52113 17.0934 6.34012 16.8178 6.27578 16.5058C6.21143 16.1939 6.2686 15.8691 6.43561 15.5979L6.52561 15.4691L10.9019 10.0004L6.52686 4.53165Z" fill="#C4C4D4" />-->
<!--          </svg>-->
        </div>
        <div class="font-medium text-xs leading-[130%] text-[#778]">{{level.description}}</div>
<!--        <p class="font-normal text-xs leading-[130%] text-[#8f8fa3]">{{level.description}} </p>-->
        <div v-if="user">
          <UIPLine v-if="!user.is_pupil"
                   :value="level.progress"
                   :progress_bg_color="course.progress_bg_color"
                   :progress_color ="course.progress_color"
                   class="my-[5px]"/>
          <p v-if="!user.is_pupil" class="font-normal text-xs leading-[130%] text-[#8f8fa3]">{{level.done_lessons_count}} из {{level.lessons_count}} уроков пройдено</p>

        </div>
        <div v-else>
          <UIPLine  :value="0"
                    :progress_bg_color="course.progress_bg_color"
                    :progress_color ="course.progress_color"
                    class="my-[5px]"/>
          <p  class="font-normal text-xs leading-[130%] text-[#8f8fa3]">0 из {{level.lessons_count}} уроков пройдено</p>
        </div>
<!--        <UIPLine v-if="user && !user.is_pupil"  :value="level.progress" class="my-[5px]"/>-->
<!--        <p v-if="user && !user.is_pupil" class="font-normal text-xs leading-[130%] text-[#8f8fa3]">{{level.done_lessons_count}} из {{level.lessons_count}} уроков пройдено</p>-->

      </div>
    </NuxtLink>
  </div>
</template>
<script setup lang="ts">
const {level_slug, course_slug}  = useRoute().params
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
const showNotAuthModal = useState('showNotAuthModal')
interface Lesson {
  id: number
  title: string
  slug: string
  progress: number
  text: string
  completed: boolean
  pin: boolean
}

interface Props {
  lesson: Lesson
}

const props = defineProps<Props>()

const gotoLesson = () => {
  if (user.value){
    navigateTo(`/courses/${course_slug}/${level_slug}/${props.lesson.slug}`)
    return
  }
  if (props.lesson.is_free) {
    navigateTo(`/courses/${course_slug}/${level_slug}/${props.lesson.slug}`)
    return
  }

  showNotAuthModal.value = true

}
</script>

<template>
  <div @click="gotoLesson"
       class="bg-white border border-solid border-[rgba(24,24,27,0.1)] rounded-2xl p-[10px] flex flex-col gap-1  cursor-pointer">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
<!--        <img v-if="data.pin" src="~/assets/images/pin-icon.svg" alt="" class="shrink-0">-->
        <svg v-if="lesson.is_common" width="15" height="20" viewBox="0 0 15 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M13.1246 3.00005C13.1246 2.73483 13.0257 2.47977 12.8499 2.29223C12.6741 2.10493 12.4359 1.99926 12.1874 1.99926H2.81257C2.56392 1.99926 2.3248 2.10469 2.14898 2.29223C1.97316 2.47977 1.87431 2.73483 1.87431 3.00005V17.2761L7.03472 14.1319L7.14568 14.0745C7.41045 13.9592 7.71306 13.9782 7.96528 14.1319L13.1246 17.2761V3.00005ZM15 19C15 19.3564 14.8221 19.6859 14.5331 19.8648C14.244 20.0437 13.8872 20.0452 13.597 19.8683L7.49945 16.1511L1.40189 19.8683C1.11186 20.0449 0.755824 20.0435 0.46693 19.8648C0.177878 19.6859 1.4284e-07 19.3564 0 19V3.00005C0 2.20439 0.295437 1.44037 0.822896 0.87775C1.35036 0.315131 2.06663 0 2.81257 0H12.1874C12.9332 7.57631e-08 13.6486 0.315375 14.176 0.87775C14.7035 1.44037 15 2.20439 15 3.00005V19Z" fill="#7575F0"/>
          <path d="M13.1246 3.00005C13.1246 2.73483 13.0257 2.47977 12.8499 2.29223C12.6741 2.10493 12.4359 1.99926 12.1874 1.99926H2.81257C2.56392 1.99926 2.3248 2.10469 2.14898 2.29223C1.97316 2.47977 1.87431 2.73483 1.87431 3.00005V17.2761L7.03472 14.1319L7.14568 14.0745C7.41045 13.9592 7.71306 13.9782 7.96528 14.1319L13.1246 17.2761V3.00005Z" fill="#7575F0"/>
        </svg>



        <h3 class="font-medium text-lg leading-[130%] text-black">{{ lesson.title }}</h3>

      </div>

      <img v-if="lesson.completed" src="~/assets/images/check-circle.svg" alt="" class="shrink-0">
    </div>
    <p class="font-normal text-xs leading-[130%] text-[#8f8fa3]">{{lesson.short_description}} </p>
    <div class="flex flex-col gap-1">
      <p class="font-normal text-sm leading-[120%] text-[#8f8fa3]">{{ lesson.text }}</p>
      <UIPLine v-if="user && !user.is_pupil" :value="lesson.progress"/>
    </div>
  </div>
</template>
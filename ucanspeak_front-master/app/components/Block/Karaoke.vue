<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  data: {
    video_src: string
    phrases: {
      id: number
      start_time: string
      end_time: string
      text_en: string
      text_ru: string
      sound: string
    }[]
  }
}>()

/* DOM */
const playerEl = ref<HTMLElement | null>(null)
const videoEl = ref<HTMLVideoElement | null>(null)
const visible = ref<boolean>(false)

/* state */
const currentTime = ref(0)
const isFullscreen = ref(false)
const phrases = ref(props.data.phrases)

/* utils */
const parseTime = (time: string): number => {
  const [hh, mm, ss] = time.split('.').map(Number)
  return hh * 3600 + mm * 60 + ss
}

/* events */
const onTimeUpdate = () => {
  if (videoEl.value) currentTime.value = videoEl.value.currentTime
}

/* fullscreen */
const onFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

const toggleFullscreen = () => {
  if (!playerEl.value) return

  if (!document.fullscreenElement) {
    playerEl.value.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

onMounted(() => {
  document.addEventListener('fullscreenchange', onFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', onFullscreenChange)
})

/* computed */
const currentPhrase = computed(() =>
    phrases.value.find(p => {
      const start = parseTime(p.start_time)
      const end = parseTime(p.end_time)
      return currentTime.value >= start && currentTime.value <= end
    })
)

const visiblePhrases = computed(() =>
    phrases.value.filter(p =>
        parseTime(p.start_time) <= currentTime.value
    )
)

/* actions */
const jumpTo = (time: string) => {
  if (!videoEl.value) return
  videoEl.value.currentTime = parseTime(time)
  videoEl.value.play()
}

const playPhraseAudio = (file: string) => {
  new Audio(file).play()
}
</script>

<template>

  <img @click="visible = true" class="w-[120px] h-[90px] object-cover cursor-pointer" src="~assets/images/video_lesson.svg">
  <Dialog v-model:visible="visible" modal header="Видео урок" :show-header="false" class="w-[65%] video-modal">
  <div
      ref="playerEl"
      class="relative   rounded-xl overflow-hidden"
  >

    <!-- VIDEO -->
    <video
        ref="videoEl"
        controls
        controlsList="nofullscreen"
        class="w-full"
        @timeupdate="onTimeUpdate"
    >
      <source
          :src="data.file+'#t=0.1'"
          type="video/mp4"
      />
    </video>

    <p class="bg-white absolute left-3 top-3 py-1 px-2 rounded-lg font-medium">{{data.video_number}}</p>

    <!-- FULLSCREEN BUTTON -->
    <button
        class="absolute top-2 right-4 z-50 text-white bg-black/70 px-3 py-1 rounded"
        @click="visible=false"
    >
      <i class="pi pi-times"></i>
    </button>
    <button
        class="absolute top-10 right-4 z-50 text-white bg-black/70 px-3 py-1 rounded"
        @click="toggleFullscreen"
    >
      ⛶
    </button>

    <!-- SUBTITLES (ALWAYS OVER VIDEO) -->
    <transition name="fade">
      <div
          v-if="isFullscreen && currentPhrase"
          class="absolute bottom-10 left-1/2 -translate-x-1/2
               z-40 bg-black/70 px-6 py-3 rounded-xl
               text-center max-w-[90%]"
      >
        <div class="text-2xl text-white font-bold">
          {{ currentPhrase.text_en }}
        </div>
        <div class="text-lg text-yellow-300 mt-1">
          {{ currentPhrase.text_ru }}
        </div>
      </div>
    </transition>

    <!-- PHRASES LIST (HIDDEN IN FULLSCREEN) -->
    <transition-group
        v-if="!isFullscreen"
        name="fade"
        tag="div"
        class=" bottom-0 left-0 right-0
             p-4 space-y-2 flex flex-col
             "
    >
      <div
          v-for="p in visiblePhrases"
          :key="p.id"
          class="p-2 rounded-2xl flex gap-3 items-center justify-between"
          :class="{
      'bg-white ': currentPhrase?.id === p.id,
      'bg-[#F6F6FB]': currentPhrase?.id !== p.id
        }"
      >

          <svg @click.stop="playPhraseAudio(p.file)" width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="40" height="40" rx="20" fill="#EFEFF5"/>
            <path fill-rule="evenodd" clip-rule="evenodd" d="M17.8656 13.2C17.7171 13.0886 17.5404 13.0207 17.3554 13.004C17.1705 12.9874 16.9845 13.0225 16.8184 13.1056C16.6523 13.1886 16.5126 13.3163 16.415 13.4743C16.3173 13.6322 16.2656 13.8143 16.2656 14V26C16.2656 26.1857 16.3173 26.3678 16.415 26.5257C16.5126 26.6837 16.6523 26.8114 16.8184 26.8944C16.9845 26.9775 17.1705 27.0126 17.3554 26.996C17.5404 26.9793 17.7171 26.9114 17.8656 26.8L25.8656 20.8C25.9898 20.7069 26.0906 20.5861 26.1601 20.4472C26.2295 20.3084 26.2656 20.1552 26.2656 20C26.2656 19.8448 26.2295 19.6916 26.1601 19.5528C26.0906 19.4139 25.9898 19.2931 25.8656 19.2L17.8656 13.2Z" fill="#3333E8"/>
          </svg>


        <div @click="jumpTo(p.start_time)" class="flex-1 cursor-pointer">
          <div class="font-semibold">{{ p.text_en }}</div>
          <div class="text-sm text-gray-400">{{ p.text_ru }}</div>
        </div>


      </div>
    </transition-group>

  </div>
  </Dialog>
</template>

<style lang="scss">
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

</style>


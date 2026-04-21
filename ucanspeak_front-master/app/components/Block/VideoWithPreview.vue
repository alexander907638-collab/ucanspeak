<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
const config = useRuntimeConfig();

const props = defineProps<{
  showPreview: boolean;

  data: {
    video_src: string
    file: string
    phrases: {
      id: number
      start_time: string
      end_time: string
      text_en: string
      text_ru: string
      sound: string
    }[]
    watermarks: {
      start_time: string
      end_time: string
      text: string
    }[]
  }
}>()

/* DOM */
const playerEl = ref<HTMLElement | null>(null)
const videoEl = ref<HTMLVideoElement | null>(null)
const visible = ref<boolean>(false)
const firstFrame = ref<string | null>(null) // здесь будет base64 первого кадра

/* state */
const currentTime = ref(0)
const isFullscreen = ref(false)
const phrases = ref(props.data.phrases)
const isPaused = ref(false)
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

const onPlay = () => {
  isPaused.value = false
}

const onPause = () => {
  isPaused.value = true
}
const toggleFullscreen = () => {
  const video = videoEl.value as any
  if (video?.webkitEnterFullscreen) {
    video.webkitDisplayingFullscreen
        ? video.webkitExitFullscreen()
        : video.webkitEnterFullscreen()
    return
  }
  if (!playerEl.value) return
  isFullscreen.value = !isFullscreen.value
  !document.fullscreenElement
      ? playerEl.value.requestFullscreen()
      : document.exitFullscreen()
}
// const toggleFullscreen = () => {
//   if (!playerEl.value) return
//   isFullscreen.value = !isFullscreen.value
//   if (!document.fullscreenElement) {
//     playerEl.value.requestFullscreen()
//   } else {
//     document.exitFullscreen()
//   }
// }

onMounted(() => {
  if(!props.showPreview) return
  document.addEventListener('fullscreenchange', onFullscreenChange)

  const tempVideo = document.createElement('video')
  tempVideo.src = props.data.file
  tempVideo.crossOrigin = 'anonymous'
  tempVideo.muted = true
  tempVideo.preload = 'metadata' // добавьте это

  tempVideo.addEventListener('loadedmetadata', () => {
    // Устанавливаем currentTime ПОСЛЕ загрузки метаданных
    tempVideo.currentTime = 0.1 // небольшой offset, т.к. 0 может быть проблемным
  })

  tempVideo.addEventListener('seeked', () => {
    // Рисуем кадр ПОСЛЕ завершения перемотки
    const canvas = document.createElement('canvas')
    canvas.width = tempVideo.videoWidth
    canvas.height = tempVideo.videoHeight
    const ctx = canvas.getContext('2d')
    if (ctx) {
      ctx.drawImage(tempVideo, 0, 0, canvas.width, canvas.height)
      firstFrame.value = canvas.toDataURL('image/png')
    }
  })
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

const currentWatermark = computed(() =>
    (props.data.watermarks ?? []).find(w => {
      const start = parseTime(w.start_time)
      const end = parseTime(w.end_time)
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
const fav_loading = ref(false)
const openedId = ref<number | null>(null)
const handleToggleOpen = (id: number) => {
  openedId.value = openedId.value === id ? null : id
}

const {$api} = useNuxtApp()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const phrase_edit_visible = ref(false)
const phrase_being_edited = ref<any>(null)

const reorder_mode = ref(false)
const reorder_saving = ref(false)
const reorder_buffer = ref<any[]>([])

const openPhraseEdit = (phrase: any) => {
  phrase_being_edited.value = phrase
  phrase_edit_visible.value = true
}

const onPhraseSaved = () => {
}

const onPhraseDeleted = (id: number) => {
  phrases.value = phrases.value.filter(p => p.id !== id)
}

const startReorder = () => {
  reorder_buffer.value = [...phrases.value]
  reorder_mode.value = true
}

const cancelReorder = () => {
  reorder_mode.value = false
  reorder_buffer.value = []
}

const moveItem = (idx: number, direction: -1 | 1) => {
  const newIdx = idx + direction
  if (newIdx < 0 || newIdx >= reorder_buffer.value.length) return
  const arr = [...reorder_buffer.value]
  ;[arr[idx], arr[newIdx]] = [arr[newIdx], arr[idx]]
  reorder_buffer.value = arr
}

const saveReorder = async () => {
  reorder_saving.value = true
  try {
    const ids = reorder_buffer.value.map(p => p.id)
    const video_id = (props.data as any).id
    if (!video_id) {
      throw new Error('video_id не найден в data')
    }
    await $api.lessons.reorder_phrases(video_id, ids)
    phrases.value = [...reorder_buffer.value]
    reorder_mode.value = false
  } catch (e) {
    console.error('reorder error', e)
    alert('Не удалось сохранить порядок')
  } finally {
    reorder_saving.value = false
  }
}

const handleHide = () => {
  // phrases.value = []
  isPaused.value = false
}

watch(visible, (val) => {
  if (val) {
    nextTick(() => videoEl.value?.play())
  }
})

const close = () => {
  isFullscreen.value = false
  visible.value = false
}
</script>

<template>
  <div class="" v-if="!visible">
    <img
        v-if="showPreview && firstFrame"
        @click="visible = true"
        class="w-[220px] h-[140px] object-cover cursor-pointer"
        :src="firstFrame"
    />
    <img
        v-else
        @click="visible = true"
        class="w-[120px] h-[90px] object-cover cursor-pointer"
        src="~assets/images/lesson_video.png"
    />
  </div>


  <Dialog v-model:visible="visible" @hide="handleHide"  header="Видео урок" :show-header="false" class="video-modal relative">
<!--    <div class="block lg:hidden absolute bottom-2 right-2">-->
<!--      <button-->
<!--          class="z-50 text-[#CACACA] bg-black/40 px-3 py-1 rounded"-->
<!--          @click="visible=false"-->
<!--      >-->
<!--        <i class="pi pi-times"></i>-->
<!--      </button>-->
<!--    </div>-->
    <div class="px-4 py-2 flex justify-between">
      <p class="text-[12px] text-[#8F8FA3] font-medium p-1 border border-[#E0E0EB] rounded-md ">{{data.video_number}}</p>
      <div class="flex gap-2 cursor-pointer">
        <svg @click="toggleFullscreen" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="0.5" y="0.5" width="23" height="23" rx="3.5" stroke="#E0E0EB"/>
          <path d="M10.75 10.75L7 7M7 7V10.4375M7 7H10.4375" stroke="#8F8FA3" stroke-width="1.2" stroke-linecap="round"/>
          <path d="M13.25 13.25L17 17M17 17L17 13.5625M17 17L13.5625 17" stroke="#8F8FA3" stroke-width="1.2" stroke-linecap="round"/>
        </svg>
        <svg @click="close" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="0.5" y="0.5" width="23" height="23" rx="3.5" stroke="#E0E0EB"/>
          <path d="M8 16L16 8" stroke="#8F8FA3" stroke-width="1.2" stroke-linecap="round"/>
          <path d="M8 8L16 16" stroke="#8F8FA3" stroke-width="1.2" stroke-linecap="round"/>
        </svg>


      </div>

    </div>
    <div  ref="playerEl" class="relative  overflow-hidden">
      <!-- VIDEO -->
      <video
          ref="videoEl"
          controls
          preload="metadata"
          controlsList="nofullscreen"
          playsinline
          class="w-full"
          :class="isFullscreen ? 'h-svh' : ''"
          @timeupdate="onTimeUpdate"
          @play="onPlay"
          @pause="onPause"
      >

        <source :src="data.file" type="video/mp4" />
      </video>

      <p v-if="isFullscreen" class="bg-black/40 text-[#CACACA] absolute left-2 top-2 py-1 px-2 rounded-lg font-medium">{{data.video_number}}</p>
<!--      <transition name="fade">-->
<!--        <div-->
<!--            v-if="currentWatermark"-->
<!--            :class="isFullscreen ? 'bottom-20 right-5' : 'top-2 left-1/2 -translate-x-1/2'"-->
<!--            class="absolute   z-40-->
<!--           bg-black/30 px-4 py-2 rounded-xl text-center max-w-[90%]"-->
<!--        >-->
<!--          <p-->
<!--              v-for="(line, i) in currentWatermark.text.split(/\r?\n/)"-->
<!--              :key="i"-->
<!--              class="text-white/30 font-semibold"-->
<!--              :class="isFullscreen ? 'text-lg' : 'text-xs'"-->
<!--          >-->
<!--            {{ line }}-->
<!--          </p>-->
<!--        </div>-->
<!--      </transition>-->
      <!-- FULLSCREEN BUTTON -->

      <button
          v-if="isFullscreen"
          class="absolute top-2 right-2 z-50 text-[#CACACA] bg-black/40 px-3 py-1 rounded"
          @click="close"
      >
        <i class="pi pi-times"></i>
      </button>
      <button
          v-if="isFullscreen"
          class="absolute top-2 right-14 z-50 text-[#CACACA] bg-black/40 px-3 py-1 rounded"
          @click="toggleFullscreen"
      >
        ⛶
      </button>

      <!-- SUBTITLES (ALWAYS OVER VIDEO) -->
<!--      <transition name="fade">-->

<!--        <div-->
<!--            v-if="isFullscreen && currentPhrase"-->
<!--            class="absolute bottom-10 left-1/2 -translate-x-1/2-->
<!--               z-40 bg-black/70 px-6 py-3 rounded-xl-->
<!--               text-center max-w-[90%]"-->
<!--        >-->
<!--          <div class="text-2xl text-white font-bold">-->

<!--            {{ currentPhrase.text_en }}-->
<!--          </div>-->
<!--          <div class="text-lg text-yellow-300 mt-1">-->
<!--            {{ currentPhrase.text_ru }}-->
<!--          </div>-->
<!--        </div>-->
<!--      </transition>-->

      <!-- PHRASES LIST (HIDDEN IN FULLSCREEN) -->

        <div v-if="(isPaused || reorder_mode) && !isFullscreen" class="relative">
          <!-- админ-режим reorder -->
          <div v-if="reorder_mode" class="p-4 space-y-2">
            <div
                v-for="(item, idx) in reorder_buffer"
                :key="item.id"
                class="flex items-center gap-2 p-2 bg-[#F6F6FB] rounded-lg"
            >
              <div class="flex flex-col gap-1">
                <button
                    @click="moveItem(idx, -1)"
                    :disabled="idx === 0"
                    class="text-xs px-2 py-0.5 bg-white rounded disabled:opacity-30"
                >▲</button>
                <button
                    @click="moveItem(idx, 1)"
                    :disabled="idx === reorder_buffer.length - 1"
                    class="text-xs px-2 py-0.5 bg-white rounded disabled:opacity-30"
                >▼</button>
              </div>
              <div class="flex-1">
                <div class="text-sm font-medium">{{ item.text_en }}</div>
                <div class="text-xs text-gray-500">{{ item.text_ru }}</div>
                <div class="text-xs text-gray-400">{{ item.start_time }} → {{ item.end_time }}</div>
              </div>
            </div>
            <div class="flex gap-2 pt-2">
              <Button
                  label="Сохранить порядок"
                  severity="success"
                  :loading="reorder_saving"
                  @click="saveReorder"
              />
              <Button
                  label="Отмена"
                  severity="secondary"
                  text
                  @click="cancelReorder"
              />
            </div>
          </div>

          <!-- обычный режим просмотра фраз -->
          <transition-group v-else name="fade" tag="div" class="bottom-0 left-0 right-0 p-4 space-y-2 flex flex-col">
            <div
                v-for="item in visiblePhrases"
                :key="item.id"
                class="flex items-center gap-2"
            >
              <CardVoiceFile
                  :item="item"
                  :reverse="true"
                  :show_add_to_fav="false"
                  :opened="openedId === item.id"
                  :loading="fav_loading"
                  @toggle_open="handleToggleOpen"
                  class="flex-1"
              />
              <Button
                  v-if="user && user.is_superuser"
                  icon="pi pi-pencil"
                  severity="secondary"
                  outlined
                  size="small"
                  @click="openPhraseEdit(item)"
              />
            </div>
          </transition-group>

          <!-- кнопка переключения в режим reorder -->
          <div
              v-if="user && user.is_superuser && !reorder_mode && phrases.length > 1"
              class="px-4 pb-2"
          >
            <Button
                label="Изменить порядок"
                severity="secondary"
                outlined
                size="small"
                icon="pi pi-sort"
                @click="startReorder"
            />
          </div>
        </div>

        <ModalPhraseEditDialog
            v-model:visible="phrase_edit_visible"
            :phrase="phrase_being_edited"
            @saved="onPhraseSaved"
            @deleted="onPhraseDeleted"
        />

      <div class="w-full h-[200px]"></div>



    </div>
  </Dialog>


</template>
<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
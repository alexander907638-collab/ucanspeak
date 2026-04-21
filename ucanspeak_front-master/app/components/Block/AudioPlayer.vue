<template>
  <div class="audio-player w-full">

    <audio
        ref="audio"
        :src="src"
        preload="auto"
        @loadedmetadata="onLoaded"
        @timeupdate="onTimeUpdate"
        @ended="isPlaying = false"
    />
    <!-- Progress -->
    <div class="time">
      <span>{{ formatTime(currentTime) }}</span>
      <span>{{ formatTime(duration) }}</span>
    </div>
    <Slider
        v-model="progress"
        :max="duration"
        @change="seek"
        class="w-full"
    />
    <div class="flex justify-center">


      <button
          text
          outlined
          rounded
          severity="secondary"
          @click="togglePlay"
      >

        <svg v-if="!isPlaying" width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="64" height="64" rx="32" fill="#EFEFF5"/>
          <path fill-rule="evenodd" clip-rule="evenodd" d="M28.585 21.12C28.3473 20.9418 28.0646 20.8332 27.7687 20.8065C27.4727 20.7798 27.1752 20.8361 26.9095 20.969C26.6437 21.1019 26.4202 21.3061 26.264 21.5589C26.1077 21.8116 26.025 22.1029 26.025 22.4V41.6C26.025 41.8972 26.1077 42.1885 26.264 42.4412C26.4202 42.694 26.6437 42.8982 26.9095 43.0311C27.1752 43.164 27.4727 43.2203 27.7687 43.1936C28.0646 43.1669 28.3473 43.0583 28.585 42.88L41.385 33.2801C41.5837 33.131 41.745 32.9378 41.8561 32.7156C41.9672 32.4934 42.025 32.2484 42.025 32C42.025 31.7517 41.9672 31.5067 41.8561 31.2845C41.745 31.0623 41.5837 30.8691 41.385 30.72L28.585 21.12Z" fill="#3333E8"/>
        </svg>
        <svg v-else width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="64" height="64" rx="32" fill="#EFEFF5"/>
          <path d="M22.4 42.24V21.76C22.4 21.5054 22.5011 21.2613 22.6812 21.0812C22.8612 20.9012 23.1054 20.8 23.36 20.8H27.84C28.0946 20.8 28.3388 20.9012 28.5188 21.0812C28.6989 21.2613 28.8 21.5054 28.8 21.76V42.24C28.8 42.4947 28.6989 42.7388 28.5188 42.9189C28.3388 43.0989 28.0946 43.2 27.84 43.2H23.36C23.1054 43.2 22.8612 43.0989 22.6812 42.9189C22.5011 42.7388 22.4 42.4947 22.4 42.24ZM35.2 42.24V21.76C35.2 21.5054 35.3011 21.2613 35.4812 21.0812C35.6612 20.9012 35.9054 20.8 36.16 20.8H40.64C40.8946 20.8 41.1388 20.9012 41.3188 21.0812C41.4989 21.2613 41.6 21.5054 41.6 21.76V42.24C41.6 42.4947 41.4989 42.7388 41.3188 42.9189C41.1388 43.0989 40.8946 43.2 40.64 43.2H36.16C35.9054 43.2 35.6612 43.0989 35.4812 42.9189C35.3011 42.7388 35.2 42.4947 35.2 42.24Z" fill="#3333E8" stroke="#3333E8" stroke-width="2.4"/>
        </svg>
      </button>
    </div>

  </div>
</template>

<script setup>

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  play: {
    type: Boolean,
    default: false

  }
})

const audio = ref(null)
const isPlaying = ref(false)
const duration = ref(0)
const currentTime = ref(0)
const progress = ref(0)

watch(() => props.src, () => {
  if (audio.value) {
    audio.value.pause()
    audio.value.currentTime = 0
  }
  isPlaying.value = false
  currentTime.value = 0
  progress.value = 0
  duration.value = 0
})

// Автоплей — immediate чтобы сработало даже если play уже true при маунте
watch(() => props.play, async (newValue) => {
  await nextTick()
  if (!audio.value) return

  if (newValue) {
    try {
      audio.value.currentTime = 0  // всегда с начала при автоплее
      await audio.value.play()
      isPlaying.value = true
    } catch (error) {
      console.error('play error:', error)
    }
  } else {
    audio.value.pause()
    audio.value.currentTime = 0
    isPlaying.value = false
  }
}, { immediate: true })
// watch(() => props.play, async (newValue) => {
//   console.log('play changed:', newValue, 'audio:', audio.value)
//
//   await nextTick()
//
//   if (!audio.value) {
//     console.log('audio element not ready')
//     return
//   }
//
//   if (newValue && !isPlaying.value) {
//     try {
//       await audio.value.play()
//       isPlaying.value = true
//       console.log('started playing')
//     } catch (error) {
//       console.error('play error:', error)
//     }
//   } else if (!newValue && isPlaying.value) {
//     audio.value.pause()
//     audio.value.currentTime = 0
//     isPlaying.value = false
//     console.log('paused')
//   }
// })


const togglePlay = () => {
  if (!audio.value) return

  if (isPlaying.value) {
    audio.value.pause()
  } else {
    audio.value.play()
  }
  isPlaying.value = !isPlaying.value
}

const onLoaded = () => {
  if (!audio.value) return
  duration.value = audio.value.duration
}

const onTimeUpdate = () => {
  if (!audio.value) return
  currentTime.value = audio.value.currentTime
  progress.value = audio.value.currentTime
}

const seek = (value) => {
  audio.value.currentTime = value
}

const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

onBeforeUnmount(() => {
  if (audio.value) {
    audio.value.pause()
    audio.value.removeEventListener('timeupdate', onTimeUpdate)
    audio.value.removeEventListener('loadedmetadata', onLoaded)
  }
})
</script>

<style scoped>
.audio-player {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.time {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}
</style>

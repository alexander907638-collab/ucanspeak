<script setup lang="ts">
const audio = new Audio()
const config = useRuntimeConfig();
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
const { play, currentPlayingId, isPlaying } = useAudioPlayer()
const props = defineProps<{
  item: any
  loading: boolean
  opened: boolean
  show_add_to_fav: boolean
  reverse: boolean
}>()
const emits = defineEmits(['toggle_fav','toggle_open'])

audio.src = props.item.file
const isThisPlaying = computed(() =>
    currentPlayingId.value === props.item.id && isPlaying.value
)
const handlePlay = () => {
  play(props.item.id, props.item.file)
  emits('toggle_open')
}

</script>


<template>
<div >

  <div class="relative flex flex-col items-start gap-1 " >
<!--    <Button @click="play" icon="pi pi-play" outlined rounded/>-->
    <div class="flex gap-2">
      <div class="" @click="handlePlay">
        <svg v-if="!isThisPlaying" width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="40" height="40" rx="20" fill="#EFEFF5"/>
          <path fill-rule="evenodd" clip-rule="evenodd" d="M17.8656 13.2C17.7171 13.0886 17.5404 13.0207 17.3554 13.004C17.1705 12.9874 16.9845 13.0225 16.8184 13.1056C16.6523 13.1886 16.5126 13.3163 16.415 13.4743C16.3173 13.6322 16.2656 13.8143 16.2656 14V26C16.2656 26.1857 16.3173 26.3678 16.415 26.5257C16.5126 26.6837 16.6523 26.8114 16.8184 26.8944C16.9845 26.9775 17.1705 27.0126 17.3554 26.996C17.5404 26.9793 17.7171 26.9114 17.8656 26.8L25.8656 20.8C25.9898 20.7069 26.0906 20.5861 26.1601 20.4472C26.2295 20.3084 26.2656 20.1552 26.2656 20C26.2656 19.8448 26.2295 19.6916 26.1601 19.5528C26.0906 19.4139 25.9898 19.2931 25.8656 19.2L17.8656 13.2Z" fill="#3333E8"/>
        </svg>
        <svg v-else width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="40" height="40" rx="20" fill="#EFEFF5"/>
          <path d="M14 26.4V13.6C14 13.4409 14.0632 13.2883 14.1757 13.1757C14.2883 13.0632 14.4409 13 14.6 13H17.4C17.5591 13 17.7117 13.0632 17.8243 13.1757C17.9368 13.2883 18 13.4409 18 13.6V26.4C18 26.5591 17.9368 26.7117 17.8243 26.8243C17.7117 26.9368 17.5591 27 17.4 27H14.6C14.4409 27 14.2883 26.9368 14.1757 26.8243C14.0632 26.7117 14 26.5591 14 26.4ZM22 26.4V13.6C22 13.4409 22.0632 13.2883 22.1757 13.1757C22.2883 13.0632 22.4409 13 22.6 13H25.4C25.5591 13 25.7117 13.0632 25.8243 13.1757C25.9368 13.2883 26 13.4409 26 13.6V26.4C26 26.5591 25.9368 26.7117 25.8243 26.8243C25.7117 26.9368 25.5591 27 25.4 27H22.6C22.4409 27 22.2883 26.9368 22.1757 26.8243C22.0632 26.7117 22 26.5591 22 26.4Z" fill="#3333E8" stroke="#3333E8" stroke-width="1.5"/>
        </svg>
      </div>
      <div class="bg-[#EFEFF5] hover:bg-[#e9e9e9] overflow-hidden p-2.5 rounded-lg">
        <div @click="emits('toggle_open', item.id)"
             class="flex items-center gap-3 cursor-pointer">
          <div @click="handlePlay" class="flex items-center cursor-pointer">
            <div class="text-base leading-[130%]">
              <span v-if="opened">{{ reverse ? item.text_en : item.text_ru }}</span>
              <span v-else>{{ reverse ? item.text_en : item.text_ru }}</span>
            </div>
          </div>
          <UILikeBtn v-if="user && show_add_to_fav" :class="loading ? 'disabled opacity-50' : ''" @click.stop="emits('toggle_fav',item.id)" v-model:value="item.is_like" />
        </div>

      </div>
    </div>

    <div v-if="opened" class=" bottom-2 ml-20 bg-[#7575F0] p-2 rounded-lg inline-block ">
      <p  class="text-base leading-[130%] tracking-[-0.01em]  text-white">
        {{reverse ? item.text_ru : item.text_en}}
      </p>
    </div>
  </div>
</div>





</template>
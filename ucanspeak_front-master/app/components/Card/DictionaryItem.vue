<script setup lang="ts">
const audio = new Audio()
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
const props = defineProps(['item', 'loading','dictionary_direction','opened'])

const emits = defineEmits(['toggle_fav','toggle_open'])
const play = () => {
  audio.src = props.item.file
  audio.play()
}
</script>


<template>
  <div class="w-full">
    <div class="relative flex items-start gap-4 w-full" :class="opened ? 'min-h-[85px]' : ''">
      <div class="bg-[#EFEFF5] hover:bg-[#e9e9e9] overflow-hidden p-2.5 rounded-lg flex-1 min-w-0 max-w-full">
        <div @click="emits('toggle_open', item.id)" class="flex items-center select-none gap-3">
          <div @click="play" class="flex flex-grow items-center gap-[3px] cursor-pointer min-w-0">
            <div class="text-base leading-[130%] break-words min-w-0">
              <span v-if="opened">{{dictionary_direction === 'ruEN' ?  item.text_ru :item.text_en}}</span>
              <span v-else>{{dictionary_direction === 'ruEN' ?  item.text_ru :item.text_en}}</span>
            </div>
          </div>
          <UILikeBtn v-if="user" :class="loading ? 'disabled opacity-50' : ''" @click.stop="emits('toggle_fav',item.id)" v-model:value="item.is_favorite" class="shrink-0" />
        </div>
        <div v-if="opened" class="mt-2 bg-[#7575F0] p-2.5 rounded-lg w-full">
          <p class="text-base text-right leading-[130%] tracking-[-0.01em] text-white break-words">
            {{dictionary_direction === 'ruEN' ?  item.text_en :item.text_ru}}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
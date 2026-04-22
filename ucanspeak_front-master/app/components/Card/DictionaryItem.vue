<script setup lang="ts">
const audio = new Audio()
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)

const props = withDefaults(defineProps<{
  item: any
  loading?: boolean
  dictionary_direction?: string
  opened?: boolean
  show_checkbox?: boolean
}>(), {
  show_checkbox: false,
})

const checked = ref(false)

const emits = defineEmits(['toggle_fav', 'toggle_open'])

const play = () => {
  if (!props.item?.file) return
  audio.src = props.item.file
  audio.play().catch(() => {})
}

// Клик по пилюле раскрывает перевод И проигрывает аудио одновременно
const handlePillClick = () => {
  emits('toggle_open', props.item.id)
  play()
}
</script>

<template>
  <div class="flex items-start gap-3">
    <!-- Чекбокс: только если show_checkbox=true -->
    <input
        v-if="show_checkbox"
        type="checkbox"
        class="custom-checkbox mt-2.5"
        v-model="checked"
        @click.stop
    >

    <!-- Колонка: пилюля оригинала + пилюля перевода снизу со сдвигом вправо -->
    <div class="flex flex-col items-start gap-1 min-w-0 max-w-full">

      <!-- Пилюля оригинала (p-2.5 / rounded-lg / gap-3 — как CardVoiceFile) -->
      <div
          @click="handlePillClick"
          class="bg-[#EFEFF5] hover:bg-[#e9e9e9] overflow-hidden p-2.5 rounded-lg cursor-pointer select-none max-w-full"
      >
        <div class="flex items-center gap-3">
          <div class="text-base leading-[130%] break-words">
            {{ dictionary_direction === 'ruEN' ? item.text_ru : item.text_en }}
          </div>
          <UILikeBtn
              v-if="user"
              :class="loading ? 'disabled opacity-50' : ''"
              @click.stop="emits('toggle_fav', item.id)"
              v-model:value="item.is_favorite"
          />
        </div>
      </div>

      <!-- Пилюля перевода: сдвиг 32px вправо (ml-8), p-2 / rounded-lg -->
      <div
          v-if="opened"
          class="bg-[#7575F0] p-2 rounded-lg ml-8 inline-block max-w-[calc(100%-2rem)]"
      >
        <p class="text-base leading-[130%] tracking-[-0.01em] text-white break-words">
          {{ dictionary_direction === 'ruEN' ? item.text_en : item.text_ru }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-checkbox {
  appearance: none;
  -webkit-appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  border: 1.5px solid #D1D5DB;
  background: white;
  cursor: pointer;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  margin: 0;
}
.custom-checkbox:hover {
  border-color: #10B981;
}
.custom-checkbox:checked {
  background-color: #10B981;
  border-color: #10B981;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='white'%3E%3Cpath d='M13.854 3.146a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 9.793l6.646-6.647a.5.5 0 0 1 .708 0z'/%3E%3C/svg%3E");
  background-position: center;
  background-repeat: no-repeat;
  background-size: 14px 14px;
}
</style>
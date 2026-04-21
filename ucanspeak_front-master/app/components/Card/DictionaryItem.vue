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

const emits = defineEmits(['toggle_fav','toggle_open'])
const play = () => {
  audio.src = props.item.file
  audio.play()
}
</script>


<template>
  <div class="flex items-start gap-3 w-full">
    <!-- Чекбокс: только если show_checkbox=true -->
    <input
        v-if="show_checkbox"
        type="checkbox"
        class="custom-checkbox mt-1.5"
        v-model="checked"
        @click.stop
    >

    <!-- Колонка с двумя пилюлями (items-end прижимает перевод к правому краю оригинала) -->
    <div class="inline-flex flex-col items-end max-w-full min-w-0">

      <!-- Пилюля оригинала, ширина по контенту -->
      <div
          @click="emits('toggle_open', item.id)"
          class="inline-flex items-center gap-2 bg-[#EFEFF5] hover:bg-[#e9e9e9] cursor-pointer px-3 py-1.5 select-none max-w-full"
          style="border-radius: 10px;"
      >
        <span
            @click.stop="play"
            class="text-base leading-[130%] break-words cursor-pointer"
        >
          {{ dictionary_direction === 'ruEN' ? item.text_ru : item.text_en }}
        </span>
        <UILikeBtn
            v-if="user"
            :class="loading ? 'disabled opacity-50' : ''"
            @click.stop="emits('toggle_fav', item.id)"
            v-model:value="item.is_favorite"
            class="flex-shrink-0"
        />
      </div>

      <!-- Пилюля перевода (видна при opened) — прижата к правому краю оригинала через items-end родителя -->
      <div
          v-if="opened"
          class="bg-[#7575F0] px-3 py-1.5 max-w-full mt-1"
          style="border-radius: 10px;"
      >
        <p class="text-base text-white leading-[130%] break-words">
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
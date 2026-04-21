<script setup>
import {ref, computed, watch, nextTick} from 'vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})

// 🌍 Язык показа
const lang = ref('ru')
const showHint = ref(false)

// 👀 Что показываем
const showText = computed(() => {
  return lang.value === 'ru'
      ? props.item.ru_text
      : props.item.en_text
})

// 🎯 Что нужно ВВЕСТИ (противоположный язык)
const targetText = computed(() => {
  return lang.value === 'ru'
      ? props.item.en_text
      : props.item.ru_text
})

// 🎯 Правильные слова для проверки
const correctWords = computed(() => {
  return targetText.value.trim().split(/\s+/)
})

// ✏️ Инпуты
const inputs = ref([])

// 📦 Ссылки на DOM элементы инпутов
const inputRefs = ref([])

// 🧪 Результаты проверки
const result = ref([])

// 🔄 Нормализация
const normalize = (str) => {
  return str
      .toLowerCase()
      .replaceAll('ё', 'е')
      .replace(/[.,!?]/g, '')
      .trim()
}

// 🔄 Инициализация
const init = () => {
  inputs.value = correctWords.value.map(() => '')
  result.value = correctWords.value.map(() => null)
}

// 🔁 При смене фразы или языка
watch([targetText], init, {immediate: true})

// 🧪 Проверка
const check = () => {
  let allOk = true

  result.value = correctWords.value.map((word, index) => {
    const ok = normalize(inputs.value[index]) === normalize(word)
    if (!ok) allOk = false
    return ok
  })

  if (allOk) {
    console.log('✅ Всё правильно! Можно отправлять на сервер')
    // 👉 тут POST на сервер
  }
}

// 🔁 Сброс
const reset = () => {
  init()
  nextTick(() => {
    // Фокус на первое поле после сброса
    if (inputRefs.value[0]) {
      inputRefs.value[0].focus()
    }
  })
}

// 📏 Все ли заполнены
const isFull = computed(() => {
  return inputs.value.every(i => i.trim().length > 0)
})

// 🚀 Автопереход к следующему полю
const handleInput = (index) => {
  const currentInput = inputs.value[index]
  const maxLength = correctWords.value[index].length

  // Если текущее поле заполнено полностью
  if (currentInput.length === maxLength) {
    // Переходим к следующему полю
    const nextIndex = index + 1
    if (nextIndex < inputRefs.value.length && inputRefs.value[nextIndex]) {
      nextTick(() => {
        inputRefs.value[nextIndex].focus()
      })
    }
  }
}

// 🔙 Обработка Backspace для перехода назад
const handleKeydown = (event, index) => {
  // Если нажат Backspace и поле пустое
  if (event.key === 'Backspace' && inputs.value[index].length === 0) {
    const prevIndex = index - 1
    if (prevIndex >= 0 && inputRefs.value[prevIndex]) {
      event.preventDefault()
      nextTick(() => {
        inputRefs.value[prevIndex].focus()
        // Курсор в конец
        inputRefs.value[prevIndex].setSelectionRange(
            inputs.value[prevIndex].length,
            inputs.value[prevIndex].length
        )
      })
    }
  }
}
</script>

<template>
  <div class="p-6 rounded-xl border bg-white  space-y-4">

    <!-- Фраза для перевода -->
    <div class="grid grid-cols-12">
      <div class="col-span-11">
        <div class="text-xl font-medium">
          {{ showText }}
        </div>
      </div>
      <div class="col-span-1 cursor-pointer justify-end">
        <svg @click="reset" width="21" height="22" viewBox="0 0 21 22" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
              d="M0 21V14.333C0.000175712 13.7809 0.447824 13.333 1 13.333H7.66699C8.21902 13.3332 8.66682 13.781 8.66699 14.333C8.66699 14.8852 8.21913 15.3328 7.66699 15.333H3.24316C4.68909 17.6366 7.25078 19.167 10.167 19.167C14.6771 19.1668 18.333 15.5101 18.333 11C18.333 10.4478 18.7809 10.0002 19.333 10C19.8853 10 20.333 10.4477 20.333 11C20.333 16.6147 15.7816 21.1668 10.167 21.167C6.81995 21.167 3.8527 19.5481 2 17.0537V21C2 21.5523 1.55228 22 1 22C0.447715 22 2.57702e-07 21.5523 0 21ZM0 11C0 5.38522 4.55221 0.833008 10.167 0.833008C13.5135 0.833112 16.4807 2.45055 18.333 4.94434V1C18.333 0.447824 18.7809 0.000176355 19.333 0C19.8853 0 20.333 0.447715 20.333 1V7.66699C20.3328 8.21913 19.8852 8.66699 19.333 8.66699H12.667C12.1148 8.66699 11.6672 8.21913 11.667 7.66699C11.667 7.11471 12.1147 6.66699 12.667 6.66699H17.0908C15.6459 4.36329 13.0842 2.83312 10.167 2.83301C5.65678 2.83301 2 6.48979 2 11C2 11.5523 1.55228 12 1 12C0.447715 12 1.28851e-07 11.5523 0 11Z"
              fill="#C4C4D4"/>
        </svg>
      </div>
    </div>

    <!-- Инпуты для ВВОДА ПЕРЕВОДА -->
    <div class="flex flex-wrap gap-2">
      <div
          v-for="(word, index) in correctWords"
          :key="index"
          class="flex flex-col items-center"
      >
        <input
            :ref="el => inputRefs[index] = el"
            v-model="inputs[index]"
            @input="handleInput(index)"
            @keydown="handleKeydown($event, index)"
            :maxlength="word.length"
            :style="{width: `${word.length > 1 ? word.length * 20 : 30}px`}"
            class="border rounded py-1 text-center text-lg inpuut"
            :class="{
              'border-green-500 bg-green-50 text-green-700': result[index] === true,
              'border-red-500 bg-red-50 text-red-700': result[index] === false
            }"
            :placeholder="'_'.repeat(word.length)"
        />
      </div>
    </div>

    <div class="" v-if="showHint">
      {{ targetText }}
    </div>

    <!-- Кнопки -->
    <div class="flex flex-wrap gap-3 pt-2">
      <Button
          size="small"
          severity="secondary"
          :disabled="!isFull"
          @click="check"
          label="Проверить"
      />
      <Button
          size="small"
          outlined
          severity="warn"
          @click="showHint = !showHint"
          :label="showHint ? 'Скрыть фразу' :'Показать фразу'"
      />
    </div>

  </div>
</template>
<style>
.inpuut{
  caret-color: #ccc;
}

</style>
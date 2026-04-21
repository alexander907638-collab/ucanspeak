<script setup lang="ts">
const model = defineModel<String>()

const props = defineProps({
  id: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  fluid: {
    type: Boolean,
    default: false
  },
  type: {
    type: String as () => 'text' | 'password' | 'numeric' | 'textarea',
    default: 'text'
  },
  error: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div :class="fluid ? 'w-full' : ''">
    <IftaLabel>
      <InputNumber
          :id="id"
          v-if="type === 'numeric'"
          v-model="model"
          :placeholder="placeholder"
          :class="{ 'p-invalid': error }"
          class="w-full"
          mode="currency"
          currency="RUB"
          locale="ru-RU"
      />
      <InputText
          v-if="type === 'text'"
          :id="id"
          type="text"
          v-model="model"
          :placeholder="placeholder"
          :class="{ 'p-invalid': error }"
          class="w-full"
      />
      <Password
          v-if="type === 'password'"
          :id="id"
          v-model="model"
          fluid
          :placeholder="placeholder"
          :class="{ 'p-invalid': error }"
          class="w-full"
          :feedback="false"
          toggleMask
      />
      <Textarea
          v-if="type === 'textarea'"
          :id="id"
          v-model="model"
          :placeholder="placeholder"
          :class="{ 'p-invalid': error }"
          class="w-full"
      />
      <label :for="id">{{ label }}</label>
    </IftaLabel>
    <small v-if="error" class="text-red-400 text-xs">{{ error }}</small>
  </div>
</template>
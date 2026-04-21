<script setup lang="ts">
const config = useRuntimeConfig()
const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

const props = defineProps<{
  app: string         // 'lesson' | 'train' | 'user'
  model: string       // 'lesson' | 'topic' | 'video' и т.д.
  id: number | string
  label?: string      // если не передан — только иконка
  fluid?: boolean
}>()

const href = computed(() =>
  `${config.public.apiUrl}/admin/${props.app}/${props.model}/${props.id}/change/`
)
</script>

<template>
  <a
    v-if="user && user.is_superuser"
    :href="href"
    target="_blank"
    rel="noopener"
    @click.stop
  >
    <Button
      :fluid="fluid"
      outlined
      severity="secondary"
      icon="pi pi-pencil"
      :label="label"
    />
  </a>
</template>

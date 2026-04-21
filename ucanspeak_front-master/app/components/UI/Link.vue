<script setup lang="ts">
const props = defineProps({
  link: {
    type: String,
  },
  label: {
    type: String,
  },


})
</script>

<template>

  <nuxt-link class="text-primary border-b border-[#CCE1FF] " :to="link">
        {{label}}
  </nuxt-link>
</template>

<style scoped>

</style>
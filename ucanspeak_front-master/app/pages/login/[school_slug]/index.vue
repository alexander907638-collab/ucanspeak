<script setup lang="ts">

definePageMeta({
  guest: true,
  layout: 'authschool'
})
</script>

<template>
  <div class=" pt-20 md:pt-0 md:h-[100vh] flex flex-col items-start justify-center">
    <FormLogin :school_auth="true"/>
  </div>
</template>

<style scoped>

</style>
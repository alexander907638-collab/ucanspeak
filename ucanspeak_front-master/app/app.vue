<script setup>
useHead({
  meta: [
    {
      name: 'viewport',
      content: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no'
    }
  ]
})

</script>
<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <Toast position="bottom-right"/>
  <NuxtLoadingIndicator/>
</template>

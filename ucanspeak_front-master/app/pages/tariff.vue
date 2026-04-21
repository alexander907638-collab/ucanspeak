<script setup lang="ts">
const {$api} = useNuxtApp()
const {data:tariffs,pending} = useHttpRequest(await useAsyncData(()=>$api.lessons.tariffs()))
const authStore = useAuthStore()
const {user} = storeToRefs(authStore)
</script>

<template>


  <BlockCourseHeader title="Тарифы" />

  <div v-if="user" class="grid grid-cols-1 md:grid-cols-4 gap-4 pb-20">
    <CardTariff v-for="tariff in tariffs" :key="tariff.id" :tariff="tariff" />
  </div>
  <div v-else class="h-[70vh] flex flex-col items-center justify-center">
    <NuxtLink   to="/login">
      <Button  label="Вход / Регистрация"/>
    </NuxtLink>
  </div>


</template>

<style scoped>

</style>
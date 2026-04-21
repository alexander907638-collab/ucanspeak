<script setup lang="ts">
const props = defineProps(['tariff'])
</script>

<template>
<CardBase padding="sm"
          :class="tariff.is_decorated? 'bg-[url(\'/a_bg.png\')]' : ''"
          class="hover:border-primary transition-colors duration-200 overflow-hidden  bg-contain bg-top bg-no-repeat">

  <p :class="tariff.is_decorated ? 'bg-primary text-white' : 'bg-[#EFEFF5] text-primary'" class="inline-block p-3 rounded-lg mb-8">{{tariff.badge_text}}</p>
  <p><span class="text-[40px]">{{tariff.price}}₽</span><span class="text-[14px] text-gray-400">/месяц</span></p>
  <p class="text-[14px] text-gray-400 mb-8">{{tariff.price_text}}</p>
  <p :class="tariff.is_decorated ? 'bg-primary text-white' : 'bg-[#EFEFF5] text-primary'" class=" p-3 rounded-lg mb-8 text-center cursor-pointer">Приобрести доступ</p>
  <p class="mb-8" v-html="tariff.description"></p>
  
  <div class="space-y-6">
    <div class="grid grid-cols-12" v-for="item in tariff.tariff_items">
      <div class="col-span-1">
        <svg class="relative top-1" width="12" height="10" viewBox="0 0 12 10" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M1.00002 5.21053L3.4517 8.10092C3.85109 8.57178 4.57753 8.57178 4.97692 8.10092L11 1" stroke="#3333E8" stroke-width="2" stroke-linecap="round"/>
        </svg>

      </div>
      <div class="col-span-11 text-gray-400" v-html="item.text"></div>
    </div>
  </div>
</CardBase>
</template>

<style scoped>

</style>
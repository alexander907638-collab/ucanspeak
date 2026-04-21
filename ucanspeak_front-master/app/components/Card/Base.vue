<script setup lang="ts">
const props = defineProps({
  padding: {
    type: String as () => 'none' | 'xs' |'sm'| 'md'| 'lg_sm' | 'lg',
    default: 'xs'
  },
  extraClass: {
    type: String,
    default: ''
  },

})


const paddingClasses: Record<string, string> = {
  none: 'p-0',
  xs: 'p-2',
  sm: 'p-4',
  md: 'p-5',
  lg_sm: 'px-5 py-3',
  lg: 'px-5 py-10 md:p-[50px] ',
}
</script>

<template>
<div class="bg-white border border-[#e0e0eb] rounded-2xl" :class="[paddingClasses[props.padding],extraClass]">
  <slot/>
</div>
</template>

<style scoped>

</style>
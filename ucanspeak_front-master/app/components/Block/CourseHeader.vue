<script setup lang="ts">
interface Props {
  title?: string
  subtitle?: string
  count?: string | number
  prev_link?: string | null
  show_profile?: boolean
  is_fixed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  subtitle: '',
  prev_link: null,
  count: null,
  is_fixed: false,

})
</script>
<!--f6f6f9-->
<template>

  <div class=" mb-2 md:mb-4   flex flex-wrap items-center gap-4 md:gap-0 justify-between bg-[#f6f6f9]"
       :class="is_fixed ? 'sticky top-[80px] z-[1000]':''"
  >
    <div v-if="is_fixed" class="bg-[#f6f6f9] absolute z-[-1] top-[-17px] w-full h-[18px] mb:h-[20px]"></div>
    <div v-if="is_fixed" class="bg-[#f6f6f9] absolute bottom-[-6px] md:bottom-[-18px] w-full h-[10px] md:h-[22px]"></div>
    <div class="flex items-center gap-4">
      <UIBackBtn :link="prev_link"/>
      <TypingText48 :text="title" />
<!--      count-->
      <div v-if="false" class="w-8 sm:w-10 h-8 sm:h-10 flex items-center justify-center border border-[#d1d1e0]
      rounded-md sm:rounded-[10px] text-[#778] text-base sm:text-2xl leading-[110%] font-normal">{{ count }}
      </div>
    </div>
    <div class="flex items-center gap-4">
      <slot name="extra"></slot>

    </div>





  </div>

</template>

<style scoped>

</style>
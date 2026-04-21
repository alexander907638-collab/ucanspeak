<script setup lang="ts">
interface Props {
    value: number
    progress_bg_color: string
    progress_color: string

}

const props = withDefaults(defineProps<Props>(), {
    value: 10,
  progress_bg_color: '#DAEFE5',
  progress_color: '#1ab266',
})
</script>

<template>
    <div class="h-2 w-full  rounded-[2px] overflow-hidden relative" :style="{'background-color':props.progress_bg_color}">
        <span 
            class="absolute start-0 top-0 h-full rounded-[2px]"
            :style="{'width': props.value + '%','background-color':props.progress_color}"
        ></span>
    </div>
</template>
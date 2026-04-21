<script setup lang="ts">
type ViewMode = "module" | "videos" | "audio" | "trainer"

const emits = defineEmits(['mode_change'])

const handleClick = (mode) => {
  emits('mode_change',mode)
}
</script>

<template>

</template>

<style lang="sass">
.footer-link
  color: #777788
  p
    font-size: 11px
  svg
    path
      fill: #8F8FA3
  &.active
    color: #3333E8
    svg
      path
        fill: #3333E8
</style>
<template>
  <CardBase padding="sm" v-for="n in 3" :key="n">
    <!-- caption -->
    <Skeleton width="60%" height="1.5rem" />

    <!-- video / karaoke -->
    <div class="mt-3">
      <Skeleton width="40%" height="2.5rem" />
    </div>

    <!-- type3_content -->
    <div class="mt-3 space-y-2">
      <Skeleton width="100%" height="1rem" />
      <Skeleton width="90%" height="1rem" />
      <Skeleton width="95%" height="1rem" />
    </div>

    <!-- items -->
    <div class="space-y-3 mt-3">
      <Skeleton v-for="i in 2" :key="i" height="3rem" />
    </div>

    <!-- buttons -->
    <div class="flex gap-4 mt-3">
      <Skeleton width="100%" height="2.5rem" />

    </div>
  </CardBase>
</template>

<script setup lang="ts">
</script>
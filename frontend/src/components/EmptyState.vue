<script setup lang="ts">
defineProps<{ icon?: string; title: string; description?: string }>()
</script>

<template>
  <div class="flex flex-col items-center justify-center py-16 text-center">
    <span class="text-5xl mb-4">{{ icon || '📭' }}</span>
    <h3 class="text-lg font-semibold text-stone-700 mb-1">{{ title }}</h3>
    <p v-if="description" class="text-sm text-stone-400">{{ description }}</p>
  </div>
</template>

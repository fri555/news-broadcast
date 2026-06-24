<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>

<template>
  <div class="flex gap-3">
    <button v-for="t in themeStore.themes" :key="t.value" @click="themeStore.setTheme(t.value)"
      class="w-8 h-8 rounded-full border-2 transition-all"
      :class="[
        t.value === 'theme-warm' ? 'bg-gradient-to-br from-orange-100 to-orange-500' :
        t.value === 'theme-pro' ? 'bg-gradient-to-br from-blue-900 to-slate-900' :
        t.value === 'theme-mini' ? 'bg-gradient-to-br from-stone-50 to-stone-300' :
        'bg-gradient-to-br from-stone-800 to-black',
        themeStore.current === t.value ? 'border-app-accent shadow-[0_0_0_3px_rgba(249,115,22,0.2)]' : 'border-transparent',
      ]"
      :title="t.label"
    />
  </div>
</template>

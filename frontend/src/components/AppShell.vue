<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import MobileBottomTab from './MobileBottomTab.vue'
import DesktopSidebar from './DesktopSidebar.vue'
import FloatingAskButton from './FloatingAskButton.vue'
import AskDrawer from './AskDrawer.vue'

const route = useRoute()
const showAskDrawer = ref(false)
const mainClass = computed(() => {
  const compactRoutes = ['ask', 'podcast']
  return compactRoutes.includes(String(route.name)) ? 'pb-0' : 'pb-20'
})
function toggleDrawer() { showAskDrawer.value = !showAskDrawer.value }
onMounted(() => window.addEventListener('toggle-ask-drawer', toggleDrawer))
onUnmounted(() => window.removeEventListener('toggle-ask-drawer', toggleDrawer))
</script>

<template>
  <div class="min-h-screen bg-app-bg">
    <DesktopSidebar />

    <!-- 无 transition，用 :key 保证组件正确切换 -->
    <main class="lg:ml-[72px] min-h-screen" :class="mainClass">
      <router-view :key="route.fullPath" />
    </main>

    <MobileBottomTab />
    <FloatingAskButton />
    <AskDrawer v-if="showAskDrawer" @close="showAskDrawer = false" />
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { Newspaper, Podcast, MessageCircle, User } from 'lucide-vue-next'
import type { TabName } from '@/types'

const route = useRoute()
const router = useRouter()

const tabs = [
  { name: 'news' as TabName, icon: Newspaper, label: '新闻', path: '/news' },
  { name: 'podcast' as TabName, icon: Podcast, label: '播客', path: '/podcast' },
  { name: 'ask' as TabName, icon: MessageCircle, label: '追问', path: '/ask' },
  { name: 'me' as TabName, icon: User, label: '我的', path: '/me' },
]
const activeTab = computed<TabName>(() => (route.name as TabName) || 'news')
function go(tab: typeof tabs[0]) { router.push(tab.path) }
</script>

<template>
  <nav class="lg:hidden fixed bottom-0 left-0 right-0 z-40 flex justify-around items-center px-4 pt-2 bg-app-card border-t border-app-divider"
    style="padding-bottom: max(1.5rem, env(safe-area-inset-bottom));">
    <button v-for="tab in tabs" :key="tab.name" @click="go(tab)"
      class="flex flex-col items-center gap-1 px-3 py-1 transition-colors min-w-[48px]"
      :class="activeTab === tab.name ? 'text-app-accent' : 'text-app-muted'"
    >
      <component :is="tab.icon" class="w-6 h-6" :stroke-width="activeTab === tab.name ? 2.5 : 1.5" />
      <span class="text-[10px] font-medium">{{ tab.label }}</span>
    </button>
  </nav>
</template>

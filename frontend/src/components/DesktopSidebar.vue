<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { Newspaper, Podcast, MessageCircle, User } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const navItems = [
  { name: 'news', icon: Newspaper, label: '新闻', path: '/news' },
  { name: 'podcast', icon: Podcast, label: '播客', path: '/podcast' },
  { name: 'ask', icon: MessageCircle, label: '追问', path: '/ask' },
  { name: 'me', icon: User, label: '我的', path: '/me' },
]
const active = computed(() => route.name as string)
function go(item: typeof navItems[0]) { router.push(item.path) }
</script>

<template>
  <!-- 桌面侧栏：固定左栏 -->
  <aside class="hidden lg:flex flex-col items-center w-[72px] py-6 gap-2 fixed left-0 top-0 bottom-0 z-30 border-r"
    style="background-color: var(--app-card2); border-color: var(--app-divider);">
    <div class="text-2xl mb-6 font-bold cursor-pointer" style="color: var(--app-accent);" @click="router.push('/')">N</div>
    <button v-for="item in navItems" :key="item.name" @click="go(item)"
      class="w-12 h-12 rounded-2xl flex flex-col items-center justify-center gap-0.5 text-[10px] transition-all"
      :style="active === item.name
        ? { backgroundColor: 'var(--app-accent-light)', color: 'var(--app-accent)' }
        : { color: 'var(--app-muted)' }">
      <component :is="item.icon" class="w-5 h-5" />
      <span>{{ item.label }}</span>
    </button>
  </aside>
</template>

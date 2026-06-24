<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useNewsStore } from '@/stores/news'
import { usePreferencesStore } from '@/stores/preferences'
import CardStack from '@/components/CardStack.vue'
import { RefreshCw, Check } from 'lucide-vue-next'

const store = useNewsStore()
const prefs = usePreferencesStore()
const showTopicPicker = ref(false)

function toggleTopic(topic: string) {
  const idx = store.selectedTopics.indexOf(topic)
  if (idx >= 0 && store.selectedTopics.length > 1) {
    store.selectedTopics.splice(idx, 1)
    if (prefs.prefs.interests.includes(topic)) prefs.toggleInterest(topic)
  } else if (idx < 0) {
    store.selectedTopics.push(topic)
    if (!prefs.prefs.interests.includes(topic)) prefs.toggleInterest(topic)
  }
  store.fetchNews(true)
}

function refresh() {
  store.fetchNews(true)
}

onMounted(() => {
  store.fetchTopics().then(() => {
    store.fetchSources()
    const saved = prefs.prefs.interests.filter(t => store.availableTopics.includes(t))
    if (saved.length > 0) store.selectedTopics = saved
    store.selectedSources = [...prefs.prefs.newsSources]
    store.fetchNews()
  })
})
</script>

<template>
  <div class="pt-3 pb-4">
    <!-- 标题栏 -->
    <div class="flex justify-between items-center px-5 py-3">
      <h1 class="text-2xl font-bold text-app-text">今日新闻</h1>
      <div class="flex items-center gap-2">
        <span class="text-xs text-app-muted">{{ store.source || '实时聚合' }}</span>
        <button @click="refresh" class="p-1.5 rounded-full hover:bg-app-card2 transition-colors" :class="{ 'animate-spin': store.loading }">
          <RefreshCw class="w-4 h-4 text-app-muted" />
        </button>
      </div>
    </div>

    <!-- 领域筛选标签 -->
    <div class="px-5 pb-3 flex flex-wrap gap-1.5">
      <button
        v-for="t in store.availableTopics"
        :key="t"
        @click="toggleTopic(t)"
        class="px-3 py-1 rounded-full text-xs font-medium transition-all border"
        :class="store.selectedTopics.includes(t)
          ? 'bg-app-accent text-white border-app-accent'
          : 'bg-app-card2 text-app-muted border-app-border hover:text-app-text'"
      >
        {{ t }}
        <Check v-if="store.selectedTopics.includes(t)" class="inline w-3 h-3 ml-0.5" />
      </button>
    </div>

    <CardStack />
  </div>
</template>

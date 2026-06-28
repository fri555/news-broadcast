<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useNewsStore } from '@/stores/news'
import { usePreferencesStore } from '@/stores/preferences'
import NewsCard from './NewsCard.vue'
import NewsDetail from './NewsDetail.vue'
import { ChevronLeft, ChevronRight, Grid3X3, Columns, Volume2, RefreshCw } from 'lucide-vue-next'
import type { NewsItem } from '@/types'
import { ttsApi } from '@/api'
import { claimSpeech, isClaimedSpeech, stopSpeech } from '@/lib/audioChannel'

const store = useNewsStore()
const prefs = usePreferencesStore()
const showDetail = ref(false)
const detailItem = ref<NewsItem | null>(null)
const listMode = ref(false)
const speakingId = ref<string | null>(null)
let currentAudio: HTMLAudioElement | null = null
let speakRequestId = 0

function openDetail(item: NewsItem) { detailItem.value = item; showDetail.value = true }
function closeDetail() { showDetail.value = false; detailItem.value = null }

/** TTS 朗读单条新闻 */
async function speakNews(item: NewsItem) {
  if (speakingId.value === item.id && isClaimedSpeech(currentAudio, 'news-card')) {
    speakRequestId++
    stopSpeech('news-card')
    currentAudio = null
    speakingId.value = null
    return
  }
  speakRequestId++
  const requestId = speakRequestId
  stopSpeech()
  currentAudio = null
  speakingId.value = item.id
  try {
    const text = item.read_aloud || item.summary || item.title
    const rate = `${Math.round((prefs.prefs.companion.speed - 1) * 100) >= 0 ? '+' : ''}${Math.round((prefs.prefs.companion.speed - 1) * 100)}%`
    const audioUrl = await ttsApi.synthesize(text, prefs.prefs.companion.voiceId, rate, 'news')
    if (requestId !== speakRequestId || speakingId.value !== item.id) return
    const audio = new Audio(audioUrl)
    currentAudio = audio
    claimSpeech(audio, 'news-card')
    audio.onended = () => { if (requestId === speakRequestId) { speakingId.value = null; currentAudio = null } }
    audio.onerror = () => { if (requestId === speakRequestId) { speakingId.value = null; currentAudio = null } }
    await audio.play()
  } catch {
    if (requestId === speakRequestId) {
      speakingId.value = null
      currentAudio = null
    }
  }
}

/** 静默后台刷新（不显示 loading） */
async function silentRefresh() {
  try {
    await store.fetchNewsSilent()
  } catch { /* ignore */ }
}

onMounted(() => {
  if (store.items.length === 0) {
    store.fetchNews()
  } else {
    // 已有数据，后台静默刷新
    silentRefresh()
  }
})
</script>

<template>
  <!-- 加载中（仅首次无数据时显示） -->
  <div v-if="store.loading && store.items.length === 0" class="flex items-center justify-center py-32 text-app-muted">
    <div class="flex flex-col items-center gap-3">
      <div class="w-8 h-8 border-2 border-app-accent border-t-transparent rounded-full animate-spin" />
      <span class="text-sm">正在抓取最新新闻...</span>
    </div>
  </div>

  <div v-else-if="store.currentItem">
    <!-- 桌面端：网格模式 -->
    <div class="hidden lg:block px-5">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-2">
          <span class="text-xs text-app-muted">{{ store.totalCount }} 条新闻</span>
          <span v-if="store.refreshing" class="text-[10px] text-app-accent animate-pulse">更新中...</span>
        </div>
        <div class="flex items-center gap-2">
          <button @click="silentRefresh" class="p-1 rounded hover:bg-app-card2 transition-colors" :class="{ 'animate-spin': store.refreshing }">
            <RefreshCw class="w-3.5 h-3.5 text-app-muted" />
          </button>
          <button @click="listMode = !listMode" class="flex items-center gap-1 text-xs text-app-muted hover:text-app-text transition-colors">
            <Grid3X3 v-if="listMode" class="w-3.5 h-3.5" />
            <Columns v-else class="w-3.5 h-3.5" />
            {{ listMode ? '卡片' : '表格' }}
          </button>
        </div>
      </div>
      <div :class="listMode ? 'grid grid-cols-1 gap-3' : 'grid grid-cols-2 xl:grid-cols-3 gap-4'">
        <div v-for="(item, i) in store.items" :key="item.id"
          class="cursor-pointer transition-all hover:scale-[1.02] hover:shadow-lg relative group"
          :class="{ 'ring-2 ring-app-accent': i === store.currentIndex }"
          @click="store.currentIndex = i; openDetail(item)">
          <NewsCard :item="item" :compact="listMode" @detail="openDetail" />
          <button
            @click.stop="speakNews(item)"
            class="absolute top-3 right-3 w-8 h-8 rounded-full flex items-center justify-center transition-all shadow-md opacity-0 group-hover:opacity-100"
            :class="speakingId === item.id ? 'bg-red-500 text-white' : 'bg-white/90 text-app-accent hover:scale-110'"
          >
            <Volume2 class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- 移动端：单卡片+左右按钮 -->
    <div class="lg:hidden px-5">
      <div class="flex items-center gap-1.5 mb-3">
        <div v-for="(_, i) in store.items" :key="i"
          class="h-1 rounded-full transition-all"
          :class="i === store.currentIndex ? 'w-4 bg-app-accent' : i < store.currentIndex ? 'w-1 bg-app-accent/40' : 'w-1 bg-app-border'"
        />
        <span class="text-[10px] text-app-muted ml-auto">{{ store.currentIndex + 1 }}/{{ store.totalCount }}</span>
        <button @click="silentRefresh" class="p-0.5 ml-1" :class="{ 'animate-spin': store.refreshing }">
          <RefreshCw class="w-3 h-3 text-app-muted" />
        </button>
      </div>

      <div class="relative">
        <button v-if="store.currentIndex > 0" @click="store.previous()"
          class="absolute left-2 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-white/90 shadow-lg flex items-center justify-center active:scale-90">
          <ChevronLeft class="w-5 h-5 text-app-text" />
        </button>

        <NewsCard :item="store.currentItem" @detail="openDetail" />

        <button v-if="store.currentIndex < store.items.length - 1" @click="store.next()"
          class="absolute right-2 top-1/2 -translate-y-1/2 z-20 w-10 h-10 rounded-full bg-app-accent shadow-lg flex items-center justify-center active:scale-90">
          <ChevronRight class="w-5 h-5 text-white" />
        </button>
      </div>

      <!-- 移动端朗读按钮 -->
      <div class="flex justify-center mt-4">
        <button @click="speakNews(store.currentItem!)"
          class="flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium transition-all active:scale-95"
          :class="speakingId === store.currentItem?.id ? 'bg-red-500 text-white' : 'bg-app-accent-light text-app-accent'">
          <Volume2 class="w-4 h-4" />
          {{ speakingId === store.currentItem?.id ? '停止播报' : '一键播报' }}
        </button>
      </div>
    </div>
  </div>

  <div v-else class="flex items-center justify-center py-32 text-app-muted">
    <div class="text-center">
      <p class="text-4xl mb-3">📭</p>
      <p class="text-sm">暂无新闻</p>
      <button @click="store.fetchNews()" class="mt-2 text-sm text-app-accent underline">重试</button>
    </div>
  </div>

  <NewsDetail v-if="showDetail" :item="detailItem!" @close="closeDetail" />
</template>

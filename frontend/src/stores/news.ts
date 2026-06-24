import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { NewsItem } from '@/types'
import { newsApi } from '@/api'

const STORAGE_KEY = 'newscast_news_cache'
const MEMORY_CACHE_MS = 10 * 60 * 1000

function loadCachedNews(): { items: NewsItem[]; source: string; lastFetched: number } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { items: [], source: '', lastFetched: 0 }
    const parsed = JSON.parse(raw)
    return {
      items: Array.isArray(parsed.items) ? parsed.items : [],
      source: parsed.source || '',
      lastFetched: Number(parsed.lastFetched) || 0,
    }
  } catch {
    return { items: [], source: '', lastFetched: 0 }
  }
}

function saveCachedNews(items: NewsItem[], source: string, lastFetched: number) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    items: items.slice(0, 30),
    source,
    lastFetched,
  }))
}

export const useNewsStore = defineStore('news', () => {
  const cached = loadCachedNews()
  const items = ref<NewsItem[]>(cached.items)
  const currentIndex = ref(0)
  const readIds = ref<Set<string>>(new Set())
  const loading = ref(false)
  const refreshing = ref(false)     // 后台静默刷新
  const selectedTopics = ref<string[]>([])
  const selectedSources = ref<string[]>([])
  const availableTopics = ref<string[]>([])
  const availableSources = ref<{ id: string; label: string; kind: string; trust: string; topics: string[]; description: string }[]>([])
  const defaultTopics = ref<string[]>([])
  const source = ref<string>(cached.source)
  const lastFetched = ref<number>(cached.lastFetched)

  const currentItem = computed(() => items.value[currentIndex.value] ?? null)
  const totalCount = computed(() => items.value.length)
  const unreadCount = computed(() => items.value.filter(n => !readIds.value.has(n.id)).length)

  async function fetchTopics() {
    try {
      const res = await newsApi.topics()
      availableTopics.value = res.all
      defaultTopics.value = res.defaults
      if (selectedTopics.value.length === 0) {
        selectedTopics.value = [...res.defaults]
      }
    } catch { /* keep defaults */ }
  }

  async function fetchSources() {
    try {
      const res = await newsApi.sources()
      availableSources.value = res.sources
    } catch { /* keep defaults */ }
  }

  async function fetchNews(forceRefresh = false) {
    if (!forceRefresh && items.value.length > 0 && Date.now() - lastFetched.value < MEMORY_CACHE_MS) {
      fetchNewsSilent()
      return
    }
    loading.value = true
    try {
      const topics = selectedTopics.value.length > 0
        ? selectedTopics.value.join(',')
        : undefined
      const sources = selectedSources.value.length > 0
        ? selectedSources.value.join(',')
        : undefined
      const res = await newsApi.list({ topics, sources, refresh: forceRefresh })
      items.value = res.news.map(n => ({ ...n, isRead: false }))
      currentIndex.value = 0
      source.value = res.source
      readIds.value = new Set()
      lastFetched.value = Date.now()
      saveCachedNews(items.value, source.value, lastFetched.value)
    } catch {
      if (items.value.length === 0) items.value = []
    } finally {
      loading.value = false
    }
  }

  /** 后台静默刷新：不显示 loading，保留现有数据 */
  async function fetchNewsSilent() {
    if (refreshing.value) return
    refreshing.value = true
    try {
      const topics = selectedTopics.value.length > 0
        ? selectedTopics.value.join(',')
        : undefined
      const sources = selectedSources.value.length > 0
        ? selectedSources.value.join(',')
        : undefined
      const res = await newsApi.list({ topics, sources })
      // 合并新旧数据：去重后保留
      const existingIds = new Set(items.value.map(i => i.id))
      const newItems = res.news.filter(n => !existingIds.has(n.id))
      if (newItems.length > 0) {
        items.value = [...items.value, ...newItems].slice(0, 30)
        source.value = res.source
      }
      lastFetched.value = Date.now()
      saveCachedNews(items.value, source.value, lastFetched.value)
    } catch { /* silent fail */ }
    finally { refreshing.value = false }
  }

  function setTopics(topics: string[]) {
    selectedTopics.value = topics
    fetchNews(true)
  }

  function setSources(sources: string[]) {
    selectedSources.value = sources
    fetchNews(true)
  }

  function markRead(id: string) { readIds.value.add(id) }

  function next() {
    if (currentIndex.value < items.value.length - 1) {
      if (currentItem.value) markRead(currentItem.value.id)
      currentIndex.value++
    }
  }
  function previous() {
    if (currentIndex.value > 0) currentIndex.value--
  }

  return {
    items, currentIndex, readIds, currentItem, totalCount, unreadCount,
    loading, refreshing, selectedTopics, selectedSources, availableTopics, availableSources, defaultTopics, source, lastFetched,
    fetchNews, fetchNewsSilent, fetchTopics, fetchSources, setTopics, setSources, markRead, next, previous,
  }
})

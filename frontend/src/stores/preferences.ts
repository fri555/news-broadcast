import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { API_BASE, API_HEADERS } from '@/api'
import type { UserPreferences, CompanionSettings } from '@/types'

const STORAGE_KEY = 'newscast_prefs'
const USER_ID_KEY = 'newscast_user_id'

function generateUserId(): string {
  const existing = localStorage.getItem(USER_ID_KEY)
  if (existing) return existing
  const id = 'u_' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36)
  localStorage.setItem(USER_ID_KEY, id)
  return id
}

const DEFAULT_PREFS: UserPreferences = {
  interests: ['科技', '财经', '国际', 'AI', '创投'],
  newsSources: [],
  pushTimes: ['8:00', '18:00', '22:00'],
  theme: 'theme-warm',
  companion: {
    name: '小暖',
    personality: '亲和温暖',
    voiceId: 'mimo_default',
    voiceA: '茉莉',
    voiceB: 'Milo',
    speed: 1.0,
    addressAs: '朋友',
  },
}

const VALID_MIMO_VOICES = new Set(['mimo_default', '冰糖', '茉莉', '苏打', '白桦', 'Mia', 'Chloe', 'Milo', 'Dean'])

function normalizePrefs(input: any): UserPreferences {
  const merged = {
    ...DEFAULT_PREFS,
    ...(input || {}),
    companion: { ...DEFAULT_PREFS.companion, ...((input || {}).companion || {}) },
  } as UserPreferences
  if (!VALID_MIMO_VOICES.has(merged.companion.voiceId)) merged.companion.voiceId = DEFAULT_PREFS.companion.voiceId
  if (!VALID_MIMO_VOICES.has(merged.companion.voiceA)) merged.companion.voiceA = DEFAULT_PREFS.companion.voiceA
  if (!VALID_MIMO_VOICES.has(merged.companion.voiceB)) merged.companion.voiceB = DEFAULT_PREFS.companion.voiceB
  if (!Number.isFinite(merged.companion.speed)) merged.companion.speed = DEFAULT_PREFS.companion.speed
  if (!Array.isArray(merged.newsSources)) merged.newsSources = []
  return merged
}

function loadFromStorage(): UserPreferences {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      return normalizePrefs(parsed)
    }
  } catch (e) { /* corrupted data, use defaults */ }
  return normalizePrefs({})
}

export const usePreferencesStore = defineStore('preferences', () => {
  const userId = ref(generateUserId())
  const prefs = ref<UserPreferences>(loadFromStorage())

  // 本地持久化
  watch(prefs, (val) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(val))
  }, { deep: true })

  // 后端同步
  async function syncWithServer() {
    try {
      const resp = await fetch(`${API_BASE}/preferences/${userId.value}`, { headers: API_HEADERS })
      if (resp.ok) {
        const serverData = await resp.json()
        // 合并：服务器优先，但本地有更新的保留
        prefs.value = normalizePrefs(serverData)
        localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs.value))
      }
    } catch (e) { /* server unavailable, use local */ }
  }

  async function saveToServer() {
    try {
      await fetch(`${API_BASE}/preferences/${userId.value}`, {
        method: 'PUT',
        headers: API_HEADERS,
        body: JSON.stringify(prefs.value),
      })
    } catch (e) { /* server unavailable */ }
  }

  function updatePrefs(partial: Partial<UserPreferences>) {
    Object.assign(prefs.value, partial)
    saveToServer()
  }

  function updateCompanion(partial: Partial<CompanionSettings>) {
    Object.assign(prefs.value.companion, partial)
    saveToServer()
  }

  function toggleInterest(tag: string) {
    const i = prefs.value.interests.indexOf(tag)
    if (i === -1) prefs.value.interests.push(tag)
    else prefs.value.interests.splice(i, 1)
    saveToServer()
  }

  // 初始同步
  syncWithServer()

  return { userId, prefs, updatePrefs, updateCompanion, toggleInterest, syncWithServer, saveToServer }
})

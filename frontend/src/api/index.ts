import type { NewsItem, NewsListResponse, TopicsResponse, NewsSourcesResponse, BroadcastResult, BroadcastNewsItem, ChatMessage, TTSVoicesResponse } from '@/types'

export const API_BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')
export const API_HEADERS = {
  'Content-Type': 'application/json',
  'bypass-tunnel-reminder': 'true',
}

export function apiAssetUrl(path: string) {
  if (!path) return ''
  if (/^https?:\/\//.test(path) || path.startsWith('blob:')) return path
  const root = API_BASE.endsWith('/api') ? API_BASE.slice(0, -4) : API_BASE
  return `${root}${path.startsWith('/') ? path : `/${path}`}`
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: API_HEADERS,
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

// ── 新闻 ────────────────────────────────────────

export const newsApi = {
  /** 获取新闻列表（支持主题过滤） */
  list: (params?: { topics?: string; sources?: string; limit?: number; refresh?: boolean }) => {
    const qs = new URLSearchParams()
    if (params?.topics) qs.set('topics', params.topics)
    if (params?.sources) qs.set('sources', params.sources)
    if (params?.limit) qs.set('limit', String(params.limit))
    if (params?.refresh) qs.set('refresh', 'true')
    const q = qs.toString()
    return request<NewsListResponse>(`/news${q ? '?' + q : ''}`)
  },
  /** 获取可用领域 */
  topics: () => request<TopicsResponse>('/news/topics'),
  /** 获取可选信息源 */
  sources: () => request<NewsSourcesResponse>('/news/catalog'),
  get: (id: string) => request<NewsItem>(`/news/${id}`),
}

// ── TTS ─────────────────────────────────────────

export const ttsApi = {
  /** 获取可用声音 */
  voices: () => request<TTSVoicesResponse>('/tts/voices'),
  /** 获取合成音频 URL */
  synthesize: async (text: string, voice?: string, rate = '+4%', style = 'news') => {
    const res = await fetch(`${API_BASE}/tts`, {
      method: 'POST',
      headers: API_HEADERS,
      body: JSON.stringify({ text, voice, rate, style }),
    })
    if (!res.ok) throw new Error('TTS failed')
    const blob = await res.blob()
    return URL.createObjectURL(blob)
  },
  /** 流式 TTS */
  streamUrl: () => `${API_BASE}/tts/stream`,
}

// ── 播客 / 广播 ─────────────────────────────────

export const podcastApi = {
  latest: (userId = 'default') => request<any>(`/podcast/latest?user_id=${encodeURIComponent(userId)}`),
  /** 生成广播脚本 */
  broadcast: (news: BroadcastNewsItem[], userId = 'default') =>
    request<BroadcastResult>(`/podcast/broadcast?user_id=${encodeURIComponent(userId)}`, {
      method: 'POST',
      body: JSON.stringify({ news }),
    }),
  get: (id: string) => request<any>(`/podcast/${id}`),
  list: () => request<{ id: string; title: string; date: string }[]>('/podcast'),
}

// ── AI 追问 ─────────────────────────────────────

export const askApi = {
  send: (message: string, context?: Record<string, any>, history?: any[]) =>
    request<ChatMessage>('/ask', {
      method: 'POST',
      body: JSON.stringify({ message, context, history }),
    }),
  stream: async function* (message: string, context?: Record<string, any>) {
    const res = await fetch(`${API_BASE}/ask/stream`, {
      method: 'POST',
      headers: API_HEADERS,
      body: JSON.stringify({ message, context, history: [] }),
    })
    if (!res.ok) throw new Error('Stream failed')
    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') return
          try {
            const parsed = JSON.parse(data)
            if (parsed.content) yield parsed.content
          } catch { /* skip */ }
        }
      }
    }
  },
}

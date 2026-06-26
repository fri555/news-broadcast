export interface NewsItem {
  id: string
  title: string
  summary: string
  detail?: NewsDetail
  read_aloud: string         // 口语化播报文本（TTS 用）
  image?: string
  source: string
  sourceUrl: string
  topic: string              // 领域分类
  category: string           // 兼容旧字段
  publishedAt: string
  hot_value: string          // 热度值
  isRead: boolean
}

export interface NewsDetail {
  one_liner?: string
  key_facts?: string[]
  background?: string
  impact?: string
  source_notes?: string
  content_richness?: 'rich' | 'partial' | 'thin'
}

export interface NewsListResponse {
  news: NewsItem[]
  source: string
  topics: string[]
  cached?: boolean
  cache_time?: string
}

export interface TopicsResponse {
  all: string[]
  defaults: string[]
}

export interface NewsSourceOption {
  id: string
  label: string
  kind: string
  trust: string
  topics: string[]
  description: string
}

export interface NewsSourcesResponse {
  sources: NewsSourceOption[]
}

// ── 播客 / 广播脚本 ──────────────────────────────

export interface BroadcastScriptLine {
  speaker: 'A' | 'B'
  text: string
}

export interface BroadcastResult {
  script: BroadcastScriptLine[]
  voice_a: string
  voice_b: string
  total_chars: number
  estimated_minutes: number
  cached?: boolean
  cache_time?: string
}

export interface BroadcastNewsItem {
  title: string
  summary: string
  source: string
  topic: string
}

export interface PodcastEpisode {
  id: string
  title: string
  date: string
  duration: number
  hosts: { name: string; gender: 'female' | 'male'; voiceColor: string }[]
  chapters: PodcastChapter[]
  transcript: TranscriptLine[]
}

export interface PodcastChapter {
  id: string
  title: string
  startTime: number
}

export interface TranscriptLine {
  speaker: string
  text: string
  startTime: number
  endTime: number
  audioUrl?: string
}

// ── TTS ─────────────────────────────────────────

export interface TTSVoice {
  id: string
  name: string
}

export interface TTSVoicesResponse {
  provider: 'edge' | 'openai' | 'mimo' | 'local'
  voices: TTSVoice[]
  default: string
}

// ── 追问 ────────────────────────────────────────

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  context?: {
    type: 'news' | 'podcast'
    id: string
    title: string
    summary?: string
    sourceUrl?: string
  }
}

// ── 用户偏好 ────────────────────────────────────

export interface UserPreferences {
  interests: string[]
  newsSources: string[]
  pushTimes: string[]
  theme: 'theme-warm' | 'theme-pro' | 'theme-mini' | 'theme-dark'
  companion: CompanionSettings
}

export interface CompanionSettings {
  name: string
  personality: '亲和温暖' | '干练知性' | '幽默活泼' | '沉稳深度'
  voiceId: string
  voiceA: string
  voiceB: string
  speed: number
  addressAs: string
}

export type TabName = 'news' | 'podcast' | 'ask' | 'me'

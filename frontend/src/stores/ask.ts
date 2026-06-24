import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage, NewsDetail } from '@/types'
import { askApi } from '@/api'

interface AskSession {
  id: string
  title: string
  messages: ChatMessage[]
  updatedAt: number
}

const ASK_SESSIONS_KEY = 'newscast_ask_sessions'
const ASK_CURRENT_KEY = 'newscast_ask_current_session'

function createSessionId() {
  return `ask_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`
}

function loadSessions(): AskSession[] {
  try {
    const raw = localStorage.getItem(ASK_SESSIONS_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed) && parsed.length > 0) return parsed
    }
  } catch { /* ignore */ }
  return []
}

export const useAskStore = defineStore('ask', () => {
  const sessions = ref<AskSession[]>(loadSessions())
  const currentSessionId = ref(localStorage.getItem(ASK_CURRENT_KEY) || sessions.value[0]?.id || createSessionId())
  const messages = ref<ChatMessage[]>(sessions.value.find(s => s.id === currentSessionId.value)?.messages || [])
  const isTyping = ref(false)
  const currentContext = ref<Record<string, string> | null>(null)
  const error = ref<string | null>(null)

  function persistSessions() {
    localStorage.setItem(ASK_SESSIONS_KEY, JSON.stringify(sessions.value.slice(0, 20)))
    localStorage.setItem(ASK_CURRENT_KEY, currentSessionId.value)
  }

  function ensureCurrentSession() {
    let session = sessions.value.find(s => s.id === currentSessionId.value)
    if (!session) {
      session = { id: currentSessionId.value, title: '新的追问', messages: [], updatedAt: Date.now() }
      sessions.value.unshift(session)
    }
    return session
  }

  function syncCurrentSession() {
    const session = ensureCurrentSession()
    session.messages = messages.value
    session.updatedAt = Date.now()
    const firstUser = messages.value.find(m => m.role === 'user')
    if (firstUser) session.title = firstUser.content.slice(0, 18)
    persistSessions()
  }

  function addWelcome() {
    if (messages.value.length > 0) return
    messages.value.push({
      id: 'welcome',
      role: 'assistant',
      content: '你好！我是小暖，你的AI新闻助手 🎙️\n\n点击任意新闻卡片里的「追问」按钮，我就能基于那条新闻的完整内容为你深度解读。\n\n试试问我：\n• 「这条新闻的核心逻辑是什么？」\n• 「这个事件会带来什么影响？」\n• 「背后的技术原理是什么？」',
      timestamp: Date.now(),
    })
    syncCurrentSession()
  }

  function setNewsContext(item: { id: string; title: string; summary: string; detail?: NewsDetail; source: string; sourceUrl: string }) {
    currentContext.value = {
      type: 'news',
      id: item.id,
      title: item.title,
      summary: item.summary,
      detail: JSON.stringify(item.detail || {}),
      source: item.source,
      sourceUrl: item.sourceUrl,
    }
  }

  async function sendMessage(content: string) {
    error.value = null
    messages.value.push({
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: Date.now(),
    })
    syncCurrentSession()
    isTyping.value = true

    try {
      const reply = await askApi.send(content, currentContext.value || undefined)
      messages.value.push(reply)
    } catch (e: any) {
      messages.value.push({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '抱歉，暂时无法回答。请检查网络后重试。',
        timestamp: Date.now(),
      })
    } finally {
      isTyping.value = false
      syncCurrentSession()
    }
  }

  function newSession() {
    currentSessionId.value = createSessionId()
    messages.value = []
    addWelcome()
    persistSessions()
  }

  function switchSession(id: string) {
    const session = sessions.value.find(s => s.id === id)
    if (!session) return
    currentSessionId.value = id
    messages.value = session.messages
    persistSessions()
  }

  function clearMessages() {
    messages.value = []
    syncCurrentSession()
    addWelcome()
  }

  addWelcome()

  return {
    messages, sessions, currentSessionId, isTyping, currentContext, error,
    sendMessage, setNewsContext, clearMessages, newSession, switchSession,
  }
})

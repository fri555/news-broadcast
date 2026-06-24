<script setup lang="ts">
import type { NewsItem } from '@/types'
import { X, ChevronLeft, ExternalLink, Clock, Radio, Volume2 } from 'lucide-vue-next'
import { useAskStore } from '@/stores/ask'
import { usePreferencesStore } from '@/stores/preferences'
import { computed, ref } from 'vue'
import { ttsApi } from '@/api'

const props = defineProps<{ item: NewsItem }>()
const emit = defineEmits<{ close: [] }>()
const askStore = useAskStore()
const prefs = usePreferencesStore()

const speaking = ref(false)
let currentAudio: HTMLAudioElement | null = null

const detail = computed(() => props.item.detail || {})
const keyFacts = computed(() => detail.value.key_facts?.filter(Boolean) || [])
const richnessLabel = computed(() => {
  if (detail.value.content_richness === 'rich') return '信息较完整'
  if (detail.value.content_richness === 'partial') return '信息部分完整'
  return '信息较少'
})
const richnessClass = computed(() => {
  if (detail.value.content_richness === 'rich') return 'bg-emerald-50 text-emerald-700 border-emerald-200'
  if (detail.value.content_richness === 'partial') return 'bg-amber-50 text-amber-700 border-amber-200'
  return 'bg-rose-50 text-rose-700 border-rose-200'
})

function goBack() { emit('close') }

function askAbout() {
  askStore.setNewsContext({
    id: props.item.id,
    title: props.item.title,
    summary: props.item.summary,
    detail: props.item.detail,
    source: props.item.source,
    sourceUrl: props.item.sourceUrl,
  })
  window.dispatchEvent(new CustomEvent('toggle-ask-drawer'))
}

function openOriginal() {
  if (props.item.sourceUrl && props.item.sourceUrl !== '#') {
    window.open(props.item.sourceUrl, '_blank', 'noopener,noreferrer')
  }
}

/** TTS 朗读全文 */
async function speakFull() {
  if (speaking.value && currentAudio) {
    currentAudio.pause(); currentAudio = null; speaking.value = false; return
  }
  // 停止旧的
  if (currentAudio) { currentAudio.pause(); currentAudio = null }
  speaking.value = true
  try {
    const text = props.item.read_aloud || props.item.summary
    const speedPercent = Math.round((prefs.prefs.companion.speed - 1) * 100)
    const rate = `${speedPercent >= 0 ? '+' : ''}${speedPercent}%`
    const audioUrl = await ttsApi.synthesize(text, prefs.prefs.companion.voiceId, rate, 'news')
    currentAudio = new Audio(audioUrl)
    currentAudio.onended = () => { speaking.value = false; currentAudio = null }
    currentAudio.onerror = () => { speaking.value = false; currentAudio = null }
    await currentAudio.play()
  } catch { speaking.value = false; currentAudio = null }
}

const emojiMap: Record<string, string> = {
  '科技': '🧠', '财经': '📈', '体育': '⚽', '国际': '🌍',
  '健康': '💊', '娱乐': '🎮', 'AI': '🤖', '数码': '💻', '综合': '📋',
  '游戏': '🎮', '时政': '🏛️', '社会': '👥', '生活': '🏠', '创业': '🚀',
}
function getEmoji(cat: string) {
  for (const [k,v] of Object.entries(emojiMap)) if (cat.includes(k)) return v
  return '📰'
}
function getGrad(topic: string) {
  if (topic.includes('科技') || topic.includes('AI')) return 'from-blue-600 to-cyan-500'
  if (topic.includes('财经')) return 'from-emerald-600 to-green-500'
  if (topic.includes('时政') || topic.includes('国际')) return 'from-indigo-600 to-blue-500'
  if (topic.includes('娱乐') || topic.includes('游戏')) return 'from-pink-600 to-purple-500'
  return 'from-orange-500 to-amber-500'
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex flex-col bg-app-bg overflow-y-auto" style="animation: detailIn 0.2s ease;">
      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-3 border-b border-app-divider shrink-0 sticky top-0 bg-app-bg/95 backdrop-blur-sm z-10">
        <button @click="goBack" class="flex items-center gap-1 text-app-sub hover:text-app-text transition-colors">
          <ChevronLeft class="w-5 h-5" />
          <span class="text-sm">返回</span>
        </button>
        <span class="text-xs text-app-muted">{{ item.source }}</span>
        <button @click="goBack" class="p-2 text-app-muted hover:text-app-text"><X class="w-5 h-5" /></button>
      </div>

      <div class="px-5 py-6">
        <!-- 标签 -->
        <div class="flex items-center gap-2 mb-4">
          <span class="bg-app-accent-light text-app-accent text-xs font-bold px-3 py-1 rounded-full">
            {{ item.category || item.topic || '综合' }}
          </span>
          <span v-if="item.hot_value" class="text-[10px] text-app-muted">
            🔥 {{ item.hot_value }}
          </span>
        </div>

        <!-- 标题 -->
        <h1 class="text-2xl font-bold leading-relaxed text-app-text mb-3 break-words">{{ item.title }}</h1>

        <!-- 来源 · 时间 -->
        <div class="flex items-center gap-3 text-sm text-app-muted mb-5">
          <span class="font-semibold text-app-accent">{{ item.source }}</span>
          <span>·</span>
          <span class="flex items-center gap-1"><Clock class="w-3 h-3" />{{ item.publishedAt }}</span>
        </div>

        <!-- 封面图区域（渐变背景 + emoji + 来源） -->
        <div
          class="w-full h-52 rounded-2xl flex items-center justify-center mb-6 relative overflow-hidden shadow-lg"
          :class="`bg-gradient-to-br ${getGrad(item.topic || item.category)}`"
        >
          <span class="text-7xl drop-shadow-lg">{{ getEmoji(item.topic || item.category) }}</span>
          <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
            <p class="text-white text-sm font-semibold">{{ item.source }} 报道</p>
            <p class="text-white/60 text-xs mt-0.5">{{ item.publishedAt }}</p>
          </div>
        </div>

        <!-- 一句话结论 -->
        <div v-if="detail.one_liner" class="mb-5">
          <div class="flex items-center justify-between gap-3 mb-3">
            <h3 class="text-lg font-semibold text-app-text">一句话看懂</h3>
            <span class="text-[11px] px-2 py-1 rounded-full border" :class="richnessClass">
              {{ richnessLabel }}
            </span>
          </div>
          <div class="bg-app-card rounded-2xl p-5 border border-app-divider">
            <p class="text-app-text leading-relaxed text-base font-medium break-words">{{ detail.one_liner }}</p>
          </div>
        </div>

        <!-- AI 摘要：保留为卡片摘要的完整版本 -->
        <div class="mb-5">
          <h3 class="text-lg font-semibold text-app-text mb-3">卡片摘要</h3>
          <div class="bg-app-card rounded-2xl p-5 border border-app-divider">
            <p class="text-app-sub leading-relaxed text-base break-words">{{ item.summary }}</p>
          </div>
        </div>

        <!-- 深度解读 -->
        <div class="mb-5">
          <h3 class="text-lg font-semibold text-app-text mb-3">深度解读</h3>
          <div class="bg-app-card rounded-2xl p-5 border border-app-divider space-y-5">
            <div v-if="keyFacts.length">
              <h4 class="text-sm font-semibold text-app-text mb-2">关键事实</h4>
              <ul class="space-y-2">
                <li v-for="fact in keyFacts" :key="fact" class="flex gap-2 text-sm leading-relaxed text-app-sub">
                  <span class="mt-2 w-1.5 h-1.5 rounded-full bg-app-accent shrink-0" />
                  <span>{{ fact }}</span>
                </li>
              </ul>
            </div>

            <div v-if="detail.background">
              <h4 class="text-sm font-semibold text-app-text mb-2">背景</h4>
              <p class="text-sm leading-relaxed text-app-sub break-words">{{ detail.background }}</p>
            </div>

            <div v-if="detail.impact">
              <h4 class="text-sm font-semibold text-app-text mb-2">影响与后续</h4>
              <p class="text-sm leading-relaxed text-app-sub break-words">{{ detail.impact }}</p>
            </div>

            <div v-if="detail.source_notes" class="pt-4 border-t border-app-divider">
              <h4 class="text-sm font-semibold text-app-text mb-2">来源说明</h4>
              <p class="text-xs leading-relaxed text-app-muted break-words">{{ detail.source_notes }}</p>
            </div>
          </div>
        </div>

        <!-- 播报文本 -->
        <div v-if="item.read_aloud" class="mb-5">
          <h3 class="text-lg font-semibold text-app-text mb-3">语音播报文本</h3>
          <div class="bg-app-card rounded-2xl p-5 border border-app-divider">
            <p class="text-app-sub leading-relaxed text-base break-words">{{ item.read_aloud }}</p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex flex-col gap-3 pb-8">
          <!-- 语音朗读 -->
          <button @click="speakFull"
            class="flex items-center justify-center gap-2 w-full py-3.5 rounded-2xl font-semibold text-base transition-all active:scale-[0.98]"
            :class="speaking ? 'bg-red-500 text-white' : 'bg-app-accent-light text-app-accent border border-app-accent/20'">
            <Volume2 class="w-5 h-5" />
            {{ speaking ? '停止朗读' : '🔊 AI 语音朗读全文' }}
          </button>

          <!-- 追问 AI -->
          <button @click="askAbout"
            class="flex items-center justify-center gap-2 w-full py-3.5 rounded-2xl font-semibold text-base active:scale-[0.98] transition-all"
            style="background: linear-gradient(135deg, #f97316, #ef4444); color: #fff;">
            <Radio class="w-5 h-5" />
            追问小暖 · AI 深度解读
          </button>

          <!-- 查看原文 -->
          <button @click="openOriginal"
            class="flex items-center justify-center gap-2 w-full py-3.5 bg-app-card border border-app-divider rounded-2xl font-medium text-sm hover:bg-app-card2 transition-colors">
            <ExternalLink class="w-5 h-5" />
            在新标签页查看原文
          </button>

          <button @click="goBack" class="w-full py-2 text-app-muted text-sm hover:text-app-sub transition-colors">
            返回新闻列表
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style>
@keyframes detailIn { from { transform: translateY(12px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
</style>

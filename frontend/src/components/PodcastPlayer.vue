<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { usePodcastStore } from '@/stores/podcast'
import { useNewsStore } from '@/stores/news'
import { usePreferencesStore } from '@/stores/preferences'
import { useRouter } from 'vue-router'
import { apiAssetUrl, ttsApi } from '@/api'
import { Play, Pause, SkipBack, SkipForward, Mic, ChevronDown, Sparkles, RefreshCw } from 'lucide-vue-next'
import { claimSpeech, stopSpeech } from '@/lib/audioChannel'

const router = useRouter()
const podcastStore = usePodcastStore()
const newsStore = useNewsStore()
const prefs = usePreferencesStore()

const isPlaying = ref(false)
const speaking = ref(false)
const playbackSpeed = ref(1)
const currentTime = ref(0)
const currentLineIndex = ref(0)
const subtitleContainer = ref<HTMLElement | null>(null)
let timer: ReturnType<typeof setInterval> | null = null
let currentAudio: HTMLAudioElement | null = null
let bgmAudio: HTMLAudioElement | null = null
let playGeneration = 0
const lineAudioCache = new Map<number, Promise<string>>()
const BGM_URL = 'https://freepd.com/music/City%20Sunshine.mp3'
const BGM_IDLE_VOLUME = 0.12
const BGM_SPEAKING_VOLUME = 0.025

const episode = computed(() => podcastStore.episode)
const effectivePlaybackRate = computed(() => prefs.prefs.companion.speed * playbackSpeed.value)
const duration = computed(() => {
  const base = episode.value?.duration ?? 720
  return Math.max(1, Math.round(base / effectivePlaybackRate.value))
})
const currentDisplayTime = computed(() => currentTime.value / effectivePlaybackRate.value)

function toggle() {
  if (!episode.value || episode.value.transcript.length === 0) return
  if (isPlaying.value) {
    isPlaying.value = false
    stopPlayback()
  } else {
    isPlaying.value = true
    const generation = ++playGeneration
    startBgm()
    void playLine(currentLineIndex.value, generation)
  }
}

function speedToRate() {
  const speed = prefs.prefs.companion.speed
  const percent = Math.round((speed - 1) * 100)
  return `${percent >= 0 ? '+' : ''}${percent}%`
}

function stopLineAudio() {
  if (currentAudio) {
    stopSpeech('podcast')
    currentAudio = null
  }
  speaking.value = false
  setBgmDucked(false)
}

function stopPlayback() {
  playGeneration++
  stopTimer()
  stopLineAudio()
  stopBgm()
}

function stopTimer() {
  if (timer) { clearInterval(timer); timer = null }
}

function startBgm() {
  if (!bgmAudio) {
    bgmAudio = new Audio(BGM_URL)
    bgmAudio.loop = true
    bgmAudio.volume = BGM_IDLE_VOLUME
  }
  bgmAudio.play().catch(() => { /* browser may block until user gesture settles */ })
}

function setBgmDucked(ducked: boolean) {
  if (!bgmAudio) return
  bgmAudio.volume = ducked ? BGM_SPEAKING_VOLUME : BGM_IDLE_VOLUME
}

function stopBgm() {
  if (!bgmAudio) return
  bgmAudio.pause()
  bgmAudio.currentTime = 0
}

function setLineByTime(time: number) {
  if (!episode.value) return
  const idx = episode.value.transcript.findIndex((line, i) =>
    time >= line.startTime &&
    time < (episode.value!.transcript[i + 1]?.startTime ?? line.endTime)
  )
  if (idx >= 0) currentLineIndex.value = idx
  else currentLineIndex.value = time >= episode.value.transcript[episode.value.transcript.length - 1].endTime
    ? episode.value.transcript.length - 1
    : 0
  currentTime.value = time
}

function seekToDisplayTime(displayTime: number) {
  const baseTime = displayTime * effectivePlaybackRate.value
  setLineByTime(baseTime)
  if (isPlaying.value) {
    const generation = ++playGeneration
    stopTimer()
    stopLineAudio()
    void playLine(currentLineIndex.value, generation)
  }
}

function seekByDisplayDelta(delta: number) {
  seekToDisplayTime(Math.max(0, currentDisplayTime.value + delta))
}

function seekFromProgress(event: MouseEvent) {
  const target = event.currentTarget as HTMLElement | null
  if (!target) return
  const rect = target.getBoundingClientRect()
  const ratio = rect.width > 0 ? Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)) : 0
  seekToDisplayTime(Math.round(ratio * duration.value))
}

// 自动滚动到当前字幕行
watch(currentLineIndex, () => {
  if (!isPlaying.value || !subtitleContainer.value) return
  const activeEl = subtitleContainer.value.querySelector('.subtitle-active')
  if (activeEl) {
    activeEl.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}, { flush: 'post' })

onUnmounted(() => { stopPlayback() })

const progress = computed(() => {
  if (duration.value <= 0) return 0
  return Math.max(0, Math.min(100, (currentDisplayTime.value / duration.value) * 100))
})
const mmss = (s: number) => `${Math.floor(s / 60).toString().padStart(2, '0')}:${Math.floor(s % 60).toString().padStart(2, '0')}`

const activeLineIndex = computed(() => {
  return episode.value ? currentLineIndex.value : -1
})

function getLineVoice(idx: number) {
  const line = episode.value?.transcript[idx]
  if (!line) return null
  return {
    text: line.text,
    voice: line.speaker === '小暖' ? prefs.prefs.companion.voiceA : prefs.prefs.companion.voiceB,
    style: line.speaker === '小暖' ? 'hostA' : 'hostB',
  }
}

function ensureLineAudio(idx: number) {
  if (lineAudioCache.has(idx)) return lineAudioCache.get(idx)!
  const lineVoice = getLineVoice(idx)
  if (!lineVoice) return Promise.reject(new Error('Line not found'))
  const line = episode.value?.transcript[idx]
  const promise = line?.audioUrl
    ? Promise.resolve(apiAssetUrl(line.audioUrl))
    : ttsApi.synthesize(lineVoice.text, lineVoice.voice, speedToRate(), lineVoice.style)
  lineAudioCache.set(idx, promise)
  return promise
}

function warmupUpcomingLines(idx: number) {
  ensureLineAudio(idx + 1).catch(() => lineAudioCache.delete(idx + 1))
  ensureLineAudio(idx + 2).catch(() => lineAudioCache.delete(idx + 2))
}

async function playLine(idx: number, generation = playGeneration) {
  if (!episode.value || !isPlaying.value || generation !== playGeneration) return
  const line = episode.value.transcript[idx]
  if (!line) {
    isPlaying.value = false
    stopPlayback()
    return
  }

  currentLineIndex.value = idx
  currentTime.value = line.startTime
  stopTimer()
  stopLineAudio()
  setBgmDucked(false)

  try {
    const audioUrl = await ensureLineAudio(idx)
    if (!isPlaying.value || currentLineIndex.value !== idx || generation !== playGeneration) return
    const audio = new Audio(audioUrl)
    currentAudio = audio
    audio.playbackRate = playbackSpeed.value
    claimSpeech(audio, 'podcast')
    warmupUpcomingLines(idx)
    audio.onended = () => {
      if (generation !== playGeneration) return
      speaking.value = false
      setBgmDucked(false)
      currentAudio = null
      currentTime.value = line.endTime
      void playLine(idx + 1, generation)
    }
    audio.onerror = () => {
      if (generation !== playGeneration) return
      speaking.value = false
      setBgmDucked(false)
      currentAudio = null
      void playLine(idx + 1, generation)
    }
    timer = setInterval(() => {
      if (currentAudio === audio && generation === playGeneration) {
        currentTime.value = Math.min(line.endTime, line.startTime + audio.currentTime)
      }
    }, 250)
    await audio.play()
    if (generation !== playGeneration) {
      audio.pause()
      return
    }
    speaking.value = true
    setBgmDucked(true)
  } catch {
    if (generation !== playGeneration) return
    speaking.value = false
    setBgmDucked(false)
    currentAudio = null
    void playLine(idx + 1, generation)
  }
}

function setPlaybackSpeed(speed: number) {
  playbackSpeed.value = speed
  if (currentAudio) currentAudio.playbackRate = speed
}

function voiceInterrupt() {
  window.dispatchEvent(new CustomEvent('toggle-ask-drawer'))
}

async function generate() {
  if (newsStore.items.length === 0) await newsStore.fetchNews()
  const news = newsStore.items.slice(0, 10).map(n => ({
    title: n.title,
    summary: n.summary,
    source: n.source,
    topic: n.topic || n.category || '综合',
  }))
  currentTime.value = 0; isPlaying.value = false
  currentLineIndex.value = 0
  stopPlayback()
  lineAudioCache.clear()
  await podcastStore.generateBroadcast(news, prefs.userId)
}

onMounted(async () => {
  await podcastStore.fetchLatest(prefs.userId)
  if (!podcastStore.episode && newsStore.items.length > 0) await generate()
  ensureLineAudio(0).catch(() => lineAudioCache.delete(0))
  warmupUpcomingLines(0)
})

watch(() => [
  prefs.prefs.companion.voiceA,
  prefs.prefs.companion.voiceB,
  prefs.prefs.companion.speed,
], () => {
  lineAudioCache.clear()
})
</script>

<template>
  <!-- 加载中 -->
  <div v-if="podcastStore.loading" class="flex items-center justify-center h-96 text-app-muted">
    <div class="flex flex-col items-center gap-3">
      <div class="w-8 h-8 border-2 border-app-accent border-t-transparent rounded-full animate-spin" />
      <span class="text-sm">AI 正在生成播客脚本...</span>
    </div>
  </div>

  <!-- 有内容时 -->
  <div v-else-if="episode && episode.transcript.length > 0"
    class="flex flex-col" style="height: calc(100vh - 85px); background: linear-gradient(180deg, #3d3226 0%, #29221a 35%, #1c1814 100%); color: #fff;">

    <!-- 顶部信息 -->
    <div class="flex items-center justify-between px-5 py-3 shrink-0">
      <ChevronDown class="w-6 h-6 text-white/60 cursor-pointer lg:hidden" @click="router.back()" />
      <div class="text-center flex-1">
        <p class="text-[10px] text-orange-400 font-bold tracking-widest uppercase">{{ episode.date }} · AI 播客</p>
        <p class="text-sm font-semibold mt-0.5">{{ episode.title }}</p>
      </div>
      <button @click="generate" class="text-[10px] text-orange-400/70 hover:text-orange-400 flex items-center gap-0.5">
        <RefreshCw class="w-3 h-3" /> 重新生成
      </button>
    </div>

    <!-- 字幕自动滚动区（填满剩余空间） -->
    <div ref="subtitleContainer" class="podcast-scrollbar flex-1 overflow-y-auto px-5 lg:px-16 min-h-0"
      style="scroll-behavior: smooth; mask-image: linear-gradient(to bottom, transparent 0%, black 8%, black 92%, transparent 100%); -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 8%, black 92%, transparent 100%);">
      <!-- 上方留白 -->
      <div class="h-[40vh]" />
      <!-- 字幕行 -->
      <div v-for="(line, i) in episode.transcript" :key="i"
        class="text-center py-5 transition-all duration-300 cursor-pointer"
        @click="seekToDisplayTime(line.startTime / effectivePlaybackRate)"
        :class="i === activeLineIndex ? 'subtitle-active' : ''">
        <p class="text-[11px] font-bold tracking-widest uppercase mb-2"
          :class="i === activeLineIndex ? 'opacity-100' : 'opacity-0'"
          :style="{ color: line.speaker === '小暖' ? '#f97316' : '#3b82f6' }">
          🎙️ {{ line.speaker }}
        </p>
        <p class="leading-relaxed transition-all duration-300"
          :class="i === activeLineIndex
            ? 'text-white font-semibold text-[22px] lg:text-[26px] leading-snug'
            : i < activeLineIndex ? 'text-white/40 text-[16px]' : 'text-white/20 text-[15px]'">
          {{ line.text }}
        </p>
      </div>
      <!-- 下方留白 -->
      <div class="h-[40vh]" />
    </div>

    <!-- 底部固定控制栏 -->
    <div class="shrink-0 px-5 pb-4 pt-2"
      style="background: linear-gradient(to top, rgba(28,24,20,1) 0%, rgba(28,24,20,0.9) 60%, transparent 100%);">
      <!-- 进度条 -->
      <div class="flex items-center gap-3 mb-3">
        <span class="text-xs text-white/40 w-9 text-right">{{ mmss(currentDisplayTime) }}</span>
        <div class="flex-1 h-1.5 bg-white/10 rounded-full relative cursor-pointer"
          @click="seekFromProgress">
          <div class="h-full bg-orange-500 rounded-full transition-all duration-300" :style="{ width: progress + '%' }" />
        </div>
        <span class="text-xs text-white/40 w-9">{{ mmss(duration) }}</span>
      </div>

      <!-- 播放控制 -->
      <div class="flex justify-center items-center gap-6">
        <select
          :value="playbackSpeed"
          class="bg-transparent text-xs font-bold text-white/60 outline-none"
          @change="setPlaybackSpeed(parseFloat(($event.target as HTMLSelectElement).value))"
        >
          <option :value="0.75">0.75x</option>
          <option :value="1">1.0x</option>
          <option :value="1.25">1.25x</option>
          <option :value="1.5">1.5x</option>
          <option :value="1.75">1.75x</option>
          <option :value="2">2.0x</option>
        </select>
        <button class="p-1.5 text-white/50 hover:text-white" @click="seekByDisplayDelta(-15)">
          <SkipBack class="w-5 h-5" />
        </button>
        <button class="w-14 h-14 rounded-full bg-orange-500 flex items-center justify-center shadow-lg shadow-orange-500/30 active:scale-95 hover:scale-105 transition-transform"
          @click="toggle">
          <Pause v-if="isPlaying" class="w-7 h-7" /><Play v-else class="w-7 h-7 ml-0.5" />
        </button>
        <button class="p-1.5 text-white/50 hover:text-white" @click="seekByDisplayDelta(15)">
          <SkipForward class="w-5 h-5" />
        </button>
        <button class="text-xs font-bold text-white/40 hover:text-white/70" @click="setPlaybackSpeed(1)">重置</button>
      </div>

      <!-- 底部按钮 -->
      <div class="flex justify-around mt-4">
        <button @click="voiceInterrupt" class="flex items-center gap-1 text-xs text-white/40 hover:text-white/70">
          <Mic class="w-3.5 h-3.5" />语音打断
        </button>
        <span v-if="speaking" class="text-[10px] text-green-400/60">🔊 播放中</span>
        <span v-else class="text-[10px] text-white/20">🎙️ {{ episode.hosts[0]?.name }} · {{ episode.hosts[1]?.name }}</span>
      </div>
    </div>
  </div>

  <!-- 空状态 -->
  <div v-else class="flex items-center justify-center flex-col gap-4" style="height: calc(100vh - 85px);">
    <p class="text-5xl">🎧</p>
    <p class="text-sm text-app-muted text-center max-w-xs">AI 将基于今日最新新闻<br>自动生成双主播对话播客</p>
    <button @click="generate"
      class="px-6 py-3 bg-app-accent text-white rounded-full text-sm font-medium active:scale-95 flex items-center gap-2 shadow-lg shadow-app-accent/30">
      <Sparkles class="w-4 h-4" /> 生成今日播客
    </button>
  </div>
</template>

<style scoped>
.podcast-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(249, 115, 22, 0.45) rgba(255, 255, 255, 0.04);
}

.podcast-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.podcast-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.04);
}

.podcast-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(249, 115, 22, 0.42);
  border-radius: 999px;
}
</style>

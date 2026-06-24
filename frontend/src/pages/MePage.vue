<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { usePreferencesStore } from '@/stores/preferences'
import { useNewsStore } from '@/stores/news'
import { useThemeStore } from '@/stores/theme'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'
import { ttsApi } from '@/api'
import { Loader2, Volume2 } from 'lucide-vue-next'

const prefs = usePreferencesStore()
const newsStore = useNewsStore()
const themeStore = useThemeStore()

const personalities = ['亲和温暖', '干练知性', '幽默活泼', '沉稳深度']
const voices = [
  { id: 'mimo_default', label: 'MiMo 默认' },
  { id: '冰糖', label: '冰糖' },
  { id: '茉莉', label: '茉莉' },
  { id: '苏打', label: '苏打' },
  { id: '白桦', label: '白桦' },
  { id: 'Mia', label: 'Mia' },
  { id: 'Chloe', label: 'Chloe' },
  { id: 'Milo', label: 'Milo' },
  { id: 'Dean', label: 'Dean' },
]
const speeds = [
  { value: 0.75, label: '0.75x' },
  { value: 0.85, label: '0.85x' },
  { value: 1.0, label: '1.0x' },
  { value: 1.15, label: '1.15x' },
  { value: 1.25, label: '1.25x' },
  { value: 1.5, label: '1.5x' },
]
const allInterests = ['科技', '财经', '体育', '国际', '娱乐', 'AI', '健康', '创投', '教育', '汽车', '游戏', '科学']
const previewing = ref<string | null>(null)
let previewAudio: HTMLAudioElement | null = null

const sourceGroups = computed(() => {
  const items = newsStore.availableSources
  return [
    { title: '权威 / 深度', items: items.filter(s => s.trust === '高') },
    { title: '综合热榜', items: items.filter(s => s.kind === '热榜' && s.trust !== '高') },
    { title: 'RSS 订阅', items: items.filter(s => s.kind === 'RSS') },
  ].filter(group => group.items.length > 0)
})

function toggleSource(sourceId: string) {
  const next = prefs.prefs.newsSources.includes(sourceId)
    ? prefs.prefs.newsSources.filter(id => id !== sourceId)
    : [...prefs.prefs.newsSources, sourceId]
  prefs.updatePrefs({ newsSources: next })
}

function clearSources() {
  prefs.updatePrefs({ newsSources: [] })
}

function speedToRate() {
  const speed = prefs.prefs.companion.speed
  const percent = Math.round((speed - 1) * 100)
  return `${percent >= 0 ? '+' : ''}${percent}%`
}

async function previewVoice(kind: 'news' | 'hostA' | 'hostB') {
  const voice = kind === 'hostA'
    ? prefs.prefs.companion.voiceA
    : kind === 'hostB'
      ? prefs.prefs.companion.voiceB
      : prefs.prefs.companion.voiceId
  const text = kind === 'hostA'
    ? '大家好，我是主播小暖，今天我们聊聊最值得关注的新闻。'
    : kind === 'hostB'
      ? '我是云希，我会补充背景信息和不同角度的观察。'
      : '这是一段新闻播报试听，帮你判断这个音色是否自然耐听。'

  previewAudio?.pause()
  previewing.value = kind
  try {
    const url = await ttsApi.synthesize(text, voice, speedToRate(), kind)
    previewAudio = new Audio(url)
    previewAudio.onended = () => { previewing.value = null }
    previewAudio.onerror = () => { previewing.value = null }
    await previewAudio.play()
  } catch {
    previewing.value = null
  }
}

onMounted(() => {
  newsStore.fetchSources()
})
</script>

<template>
  <div class="min-h-full pb-8">
    <h1 class="text-2xl font-bold px-5 py-4 text-app-text">我的</h1>

    <!-- 陪伴助手 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold uppercase tracking-widest px-5 mb-2 text-app-muted">🤖 陪伴助手人格</h2>
      <div class="mx-4 bg-app-card2 rounded-2xl divide-y divide-app-divider overflow-hidden border border-app-border">
        <div class="flex justify-between items-center px-4 py-3.5"><span class="text-sm text-app-text">助手名称</span><span class="text-sm text-app-sub">{{ prefs.prefs.companion.name }}</span></div>
        <div class="flex justify-between items-center px-4 py-3.5"><span class="text-sm text-app-text">播客角色</span><span class="text-sm text-app-sub">{{ prefs.prefs.companion.name }} / 云希</span></div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm text-app-text">性格风格</span>
          <select :value="prefs.prefs.companion.personality" @change="prefs.updateCompanion({ personality: ($event.target as HTMLSelectElement).value as any })"
            class="settings-select">
            <option v-for="p in personalities" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm text-app-text">新闻/追问音色</span>
          <div class="voice-control">
            <select :value="prefs.prefs.companion.voiceId" @change="prefs.updateCompanion({ voiceId: ($event.target as HTMLSelectElement).value })"
              class="settings-select">
              <option v-for="v in voices" :key="v.id" :value="v.id">{{ v.label }}</option>
            </select>
            <button class="preview-btn" @click="previewVoice('news')" aria-label="试听新闻音色">
              <Loader2 v-if="previewing === 'news'" class="w-3.5 h-3.5 animate-spin" />
              <Volume2 v-else class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm text-app-text">主播A音色</span>
          <div class="voice-control">
            <select :value="prefs.prefs.companion.voiceA" @change="prefs.updateCompanion({ voiceA: ($event.target as HTMLSelectElement).value })"
              class="settings-select">
              <option v-for="v in voices" :key="v.id" :value="v.id">{{ v.label }}</option>
            </select>
            <button class="preview-btn" @click="previewVoice('hostA')" aria-label="试听主播A音色">
              <Loader2 v-if="previewing === 'hostA'" class="w-3.5 h-3.5 animate-spin" />
              <Volume2 v-else class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm text-app-text">主播B音色</span>
          <div class="voice-control">
            <select :value="prefs.prefs.companion.voiceB" @change="prefs.updateCompanion({ voiceB: ($event.target as HTMLSelectElement).value })"
              class="settings-select">
              <option v-for="v in voices" :key="v.id" :value="v.id">{{ v.label }}</option>
            </select>
            <button class="preview-btn" @click="previewVoice('hostB')" aria-label="试听主播B音色">
              <Loader2 v-if="previewing === 'hostB'" class="w-3.5 h-3.5 animate-spin" />
              <Volume2 v-else class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm text-app-text">全局语速</span>
          <select :value="prefs.prefs.companion.speed" @change="prefs.updateCompanion({ speed: parseFloat(($event.target as HTMLSelectElement).value) })"
            class="settings-select">
            <option v-for="s in speeds" :key="s.value" :value="s.value">{{ s.label }}</option>
          </select>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5"><span class="text-sm text-app-text">称呼方式</span><span class="text-sm text-app-sub">{{ prefs.prefs.companion.addressAs }}</span></div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm text-app-muted">🎭 VTube虚拟形象</span>
          <span class="text-xs text-app-accent">Cubism 4 / .model3.json</span>
        </div>
      </div>
    </section>

    <!-- 主题 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold uppercase tracking-widest px-5 mb-2 text-app-muted">🎨 主题外观</h2>
      <div class="mx-4 bg-app-card2 rounded-2xl divide-y divide-app-divider overflow-hidden border border-app-border">
        <div class="flex justify-between items-center px-4 py-3.5"><span class="text-sm text-app-text">当前主题</span><ThemeSwitcher /></div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm text-app-text">{{ themeStore.themes.find(t => t.value === themeStore.current)?.label }}</span>
          <span class="text-sm text-app-accent">● 当前</span>
        </div>
      </div>
    </section>

    <!-- 兴趣 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold uppercase tracking-widest px-5 mb-2 text-app-muted">📋 兴趣偏好</h2>
      <div class="mx-4 bg-app-card2 rounded-2xl p-4 border border-app-border">
        <div class="flex flex-wrap gap-2">
          <button v-for="tag in allInterests" :key="tag" @click="prefs.toggleInterest(tag)"
            class="px-3 py-1.5 rounded-full text-xs border transition-all"
            :class="prefs.prefs.interests.includes(tag)
              ? 'bg-app-accent-light border-app-accent text-app-accent font-semibold'
              : 'bg-app-card border-app-divider text-app-muted'"
          >{{ tag }}</button>
        </div>
      </div>
    </section>

    <!-- 信息源 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold uppercase tracking-widest px-5 mb-2 text-app-muted">🧭 信息源</h2>
      <div class="mx-4 bg-app-card2 rounded-2xl p-4 border border-app-border space-y-4">
        <div class="flex items-center justify-between">
          <p class="text-sm text-app-sub">选中的来源会优先进入新闻列表；不选则自动聚合。</p>
          <button class="text-xs text-app-accent" @click="clearSources">自动</button>
        </div>

        <div v-for="group in sourceGroups" :key="group.title" class="space-y-2">
          <p class="text-[11px] font-bold uppercase tracking-widest text-app-muted">{{ group.title }}</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="source in group.items"
              :key="source.id"
              @click="toggleSource(source.id)"
              class="px-3 py-1.5 rounded-full text-xs border transition-all flex items-center gap-1"
              :class="prefs.prefs.newsSources.includes(source.id)
                ? 'bg-app-accent-light border-app-accent text-app-accent font-semibold'
                : 'bg-app-card border-app-divider text-app-muted'"
            >
              <span>{{ source.label }}</span>
              <span class="opacity-60">{{ source.trust }}</span>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 推送 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold uppercase tracking-widest px-5 mb-2 text-app-muted">⏰ 推送时间</h2>
      <div class="mx-4 bg-app-card2 rounded-2xl divide-y divide-app-divider overflow-hidden border border-app-border">
        <div v-for="t in prefs.prefs.pushTimes" :key="t" class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm text-app-text">{{ t === '8:00' ? '早间推送' : t === '18:00' ? '晚间推送' : '夜间推送' }}</span>
          <span class="text-sm text-app-sub">{{ t }} ✓</span>
        </div>
      </div>
    </section>

    <!-- 关于 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold uppercase tracking-widest px-5 mb-2 text-app-muted">ℹ️ 关于</h2>
      <div class="mx-4 bg-app-card2 rounded-2xl divide-y divide-app-divider overflow-hidden border border-app-border">
        <div class="flex justify-between items-center px-4 py-3.5"><span class="text-sm text-app-text">版本</span><span class="text-sm text-app-sub">v0.1 MVP</span></div>
        <div class="flex justify-between items-center px-4 py-3.5"><span class="text-sm text-app-text">技术栈</span><span class="text-sm text-app-sub">Vue3 + FastAPI</span></div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.settings-select {
  min-width: 132px;
  max-width: 190px;
  appearance: none;
  border: 1px solid var(--app-divider);
  border-radius: 999px;
  background: var(--app-card);
  color: var(--app-sub);
  padding: 7px 28px 7px 12px;
  font-size: 13px;
  line-height: 1;
  text-align: right;
  outline: none;
  background-image:
    linear-gradient(45deg, transparent 50%, var(--app-muted) 50%),
    linear-gradient(135deg, var(--app-muted) 50%, transparent 50%);
  background-position:
    calc(100% - 15px) 50%,
    calc(100% - 10px) 50%;
  background-size: 5px 5px, 5px 5px;
  background-repeat: no-repeat;
}

.settings-select:focus {
  border-color: var(--app-accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--app-accent) 18%, transparent);
}

.voice-control {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.preview-btn {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  border: 1px solid var(--app-divider);
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-accent) 10%, var(--app-card));
  color: var(--app-accent);
  transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}

.preview-btn:active {
  transform: scale(0.95);
}

.preview-btn:hover {
  border-color: var(--app-accent);
  background: var(--app-accent-light);
}
</style>

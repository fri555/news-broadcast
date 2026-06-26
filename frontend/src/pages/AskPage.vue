<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useAskStore } from '@/stores/ask'
import ChatBubble from '@/components/ChatBubble.vue'
import Live2DAssistant from '@/components/Live2DAssistant.vue'
import { useSpeechRecognition } from '@/composables/useSpeechRecognition'
import { Send, Mic, MicOff, AlertCircle, Plus } from 'lucide-vue-next'

const askStore = useAskStore()
const input = ref('')
const {
  isListening, finalText, interimText,
  error: voiceError, supported: voiceSupported,
  start, stop,
} = useSpeechRecognition('zh-CN')

const avatarState = computed(() => {
  if (isListening.value) return 'listening'
  if (askStore.isTyping) return 'thinking'
  return 'idle'
})

// 语音识别完成 → 自动发送
watch(finalText, (t) => { if (t) { input.value = t; send() } })

function send() {
  if (!input.value.trim()) return
  askStore.sendMessage(input.value)
  input.value = ''
}

function handleVoice() {
  if (isListening.value) stop()
  else start({ continuous: true })
}
</script>

<template>
  <div class="flex flex-col" style="height: calc(100vh - 75px);">
    <!-- 顶部标题 + 上下文 -->
    <div class="flex items-center justify-between px-5 py-4 shrink-0">
      <h1 class="text-2xl font-bold text-app-text">AI 追问</h1>
      <button
        class="w-9 h-9 rounded-full bg-app-accent-light text-app-accent flex items-center justify-center"
        @click="askStore.newSession()"
        aria-label="新建追问"
      >
        <Plus class="w-4 h-4" />
      </button>
    </div>

    <div class="px-5 pb-3 shrink-0">
      <Live2DAssistant :state="avatarState" :label="askStore.currentContext ? '追问助手' : '小暖'"/>
    </div>

    <div class="px-5 pb-2 flex items-center gap-2 shrink-0">
      <select
        :value="askStore.currentSessionId"
        class="flex-1 min-w-0 bg-app-card2 border border-app-divider rounded-full px-3 py-2 text-xs text-app-sub outline-none"
        @change="askStore.switchSession(($event.target as HTMLSelectElement).value)"
      >
        <option v-for="s in askStore.sessions" :key="s.id" :value="s.id">
          {{ s.title }} · {{ new Date(s.updatedAt).toLocaleString() }}
        </option>
      </select>
      <span
        v-if="askStore.currentContext"
        class="text-[10px] bg-app-accent-light text-app-accent px-2 py-1 rounded-full max-w-[130px] truncate"
      >
        {{ askStore.currentContext.title?.slice(0, 12) }}...
      </span>
    </div>

    <!-- 微信式语音实时文字 -->
    <div v-if="isListening" class="mx-5 mb-2 px-4 py-2 bg-app-accent-light rounded-2xl text-center animate-pulse">
      <p v-if="interimText" class="text-app-text text-sm">{{ interimText }}</p>
      <p v-else class="text-app-muted text-sm">正在聆听...</p>
    </div>

    <!-- 消息列表 -->
    <div class="flex-1 overflow-y-auto px-5 flex flex-col gap-2 pb-4 min-h-0">
      <ChatBubble v-for="msg in askStore.messages" :key="msg.id" :message="msg" />
      <div v-if="askStore.isTyping" class="flex gap-1.5 px-4 py-3">
        <span class="w-2 h-2 rounded-full bg-app-muted animate-bounce" />
        <span class="w-2 h-2 rounded-full bg-app-muted animate-bounce" style="animation-delay:0.15s" />
        <span class="w-2 h-2 rounded-full bg-app-muted animate-bounce" style="animation-delay:0.3s" />
      </div>
    </div>

    <!-- 语音错误提示 -->
    <p v-if="voiceError" class="flex items-center gap-1 px-5 pb-1 text-[10px] text-amber-500">
      <AlertCircle class="w-3 h-3" />{{ voiceError }}
    </p>

    <!-- 底部输入栏 -->
    <div class="flex items-center gap-2 px-4 py-3 border-t border-app-divider bg-app-card shrink-0">
      <input
        v-model="input"
        type="text"
        :placeholder="voiceSupported ? '输入文字或开启连续聆听...' : '输入追问...'"
        class="flex-1 px-4 py-2.5 bg-app-card2 border border-app-divider rounded-full text-sm outline-none focus:border-app-accent text-app-text placeholder:text-app-muted"
        @keydown.enter="send"
      />
      <button
        v-if="voiceSupported"
        @click="handleVoice"
        class="w-10 h-10 rounded-full flex items-center justify-center shrink-0 transition-all"
        :class="isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-app-accent-light text-app-accent'"
      >
        <MicOff v-if="isListening" class="w-5 h-5" /><Mic v-else class="w-5 h-5" />
      </button>
      <button
        v-else
        class="w-10 h-10 rounded-full bg-app-card2 text-app-muted flex items-center justify-center shrink-0"
        disabled
        title="当前浏览器不支持语音识别"
      >
        <Mic class="w-5 h-5" />
      </button>
      <button
        class="w-10 h-10 rounded-full bg-app-accent text-app-accent-text flex items-center justify-center disabled:opacity-40 shrink-0"
        :disabled="!input.trim()"
        @click="send"
      ><Send class="w-4 h-4" /></button>
    </div>
  </div>
</template>

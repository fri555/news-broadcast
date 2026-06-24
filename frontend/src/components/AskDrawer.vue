<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useAskStore } from '@/stores/ask'
import ChatBubble from './ChatBubble.vue'
import AskAvatar from './AskAvatar.vue'
import { useSpeechRecognition } from '@/composables/useSpeechRecognition'
import { Send, Mic, MicOff } from 'lucide-vue-next'

defineEmits<{ close: [] }>()
const askStore = useAskStore()
const input = ref('')
const { isListening, finalText, interimText, supported: voiceSupported, start, stop } = useSpeechRecognition('zh-CN')

const avatarState = computed(() => {
  if (isListening.value) return 'listening'
  if (askStore.isTyping) return 'thinking'
  return 'idle'
})

watch(finalText, (t) => { if (t) { input.value = t; send() } })

function send() {
  if (!input.value.trim()) return
  askStore.sendMessage(input.value)
  input.value = ''
}

function handleVoice() { isListening.value ? stop() : start({ continuous: true }) }
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex flex-col justify-end lg:hidden">
      <div class="bg-black/30 absolute inset-0" @click="$emit('close')" />
      <div class="relative bg-app-card rounded-t-3xl shadow-2xl max-h-[65%] flex flex-col" style="animation: drawerUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);">
        <div class="flex justify-center pt-3 pb-1">
          <div class="w-9 h-1 bg-app-muted rounded-full cursor-pointer" @click="$emit('close')" />
        </div>
        <div class="px-5 pb-3">
          <AskAvatar :state="avatarState" :label="askStore.currentContext ? '追问助手' : '小暖'" />
        </div>
        <div v-if="askStore.currentContext" class="mx-5 mb-2 px-3 py-1.5 bg-app-accent-light text-app-accent text-xs rounded-lg text-center truncate">
          📰 {{ askStore.currentContext.title?.slice(0, 30) }}...
        </div>
        <div v-if="isListening" class="mx-5 mb-2 px-4 py-2 bg-app-accent-light rounded-2xl text-center">
          <p v-if="interimText" class="text-app-text text-sm">{{ interimText }}</p>
          <p v-else class="text-app-muted text-sm">正在聆听...</p>
        </div>
        <div class="flex-1 overflow-y-auto px-5 flex flex-col gap-2 pb-4 max-h-80 scrollbar-hide">
          <ChatBubble v-for="msg in askStore.messages" :key="msg.id" :message="msg" />
          <div v-if="askStore.isTyping" class="flex gap-1.5 px-4 py-3">
            <span class="w-2 h-2 rounded-full bg-app-muted animate-bounce" />
            <span class="w-2 h-2 rounded-full bg-app-muted animate-bounce" style="animation-delay:0.15s" />
            <span class="w-2 h-2 rounded-full bg-app-muted animate-bounce" style="animation-delay:0.3s" />
          </div>
        </div>
        <div class="flex items-center gap-2 px-4 py-3 border-t border-app-divider">
          <input v-model="input" type="text" placeholder="输入追问..."
            class="flex-1 px-4 py-2.5 bg-app-card2 border border-app-divider rounded-full text-sm outline-none focus:border-app-accent text-app-text"
            @keydown.enter="send" />
          <button v-if="voiceSupported" @click="handleVoice"
            class="w-10 h-10 rounded-full flex items-center justify-center shrink-0"
            :class="isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-app-accent-light text-app-accent'">
            <MicOff v-if="isListening" class="w-5 h-5" /><Mic v-else class="w-5 h-5" />
          </button>
          <button v-else disabled title="当前浏览器不支持语音识别"
            class="w-10 h-10 rounded-full bg-app-card2 text-app-muted flex items-center justify-center shrink-0">
            <Mic class="w-5 h-5" />
          </button>
          <button class="w-10 h-10 rounded-full bg-app-accent text-app-accent-text flex items-center justify-center disabled:opacity-40 shrink-0"
            :disabled="!input.trim()" @click="send"><Send class="w-4 h-4" /></button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style>@keyframes drawerUp { from { transform: translateY(100%); } to { transform: translateY(0); } }</style>

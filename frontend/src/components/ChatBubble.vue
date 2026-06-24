<script setup lang="ts">
import type { ChatMessage } from '@/types'

defineProps<{ message: ChatMessage }>()
</script>

<template>
  <div class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
    <div
      class="max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed"
      :class="message.role === 'user'
        ? 'bg-app-accent text-app-accent-text rounded-br-md'
        : 'bg-app-card2 text-app-text rounded-bl-md border border-app-divider'"
    >
      <p v-if="message.role === 'assistant'" class="text-[10px] font-bold opacity-50 mb-1 tracking-wide">🤖 NewsCast AI</p>
      <p v-else class="text-[10px] font-bold opacity-50 mb-1 tracking-wide">我</p>
      <div v-html="message.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>')" />
    </div>
  </div>
</template>

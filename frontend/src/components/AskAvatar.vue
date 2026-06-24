<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  state: 'idle' | 'listening' | 'thinking' | 'speaking'
  label: string
}>()

const moodText = computed(() => {
  if (props.state === 'listening') return '正在听你说'
  if (props.state === 'thinking') return '正在理解'
  if (props.state === 'speaking') return '正在回答'
  return '在线待命'
})
</script>

<template>
  <div class="ask-avatar" :class="`ask-avatar--${state}`">
    <div class="ask-avatar-ring" />
    <div class="ask-avatar-face">
      <div class="eyes">
        <span />
        <span />
      </div>
      <div class="mouth" />
    </div>
    <div class="ask-avatar-caption">
      <p class="ask-avatar-label">{{ label }}</p>
      <p class="ask-avatar-state">{{ moodText }}</p>
    </div>
  </div>
</template>

<style scoped>
.ask-avatar {
  position: relative;
  display: grid;
  place-items: center;
  gap: 10px;
  width: 100%;
  padding: 14px 16px 16px;
  border-radius: 24px;
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--app-accent) 12%, transparent), transparent),
    var(--app-card);
  border: 1px solid var(--app-divider);
  overflow: hidden;
}

.ask-avatar-ring {
  position: absolute;
  inset: 10px;
  border-radius: 20px;
  border: 1px solid color-mix(in srgb, var(--app-accent) 20%, transparent);
  pointer-events: none;
}

.ask-avatar-face {
  width: 124px;
  height: 124px;
  border-radius: 36% 36% 42% 42%;
  background:
    radial-gradient(circle at 50% 28%, rgba(255,255,255,.92), rgba(255,255,255,.72) 34%, rgba(255,255,255,.42) 60%, rgba(255,255,255,.12)),
    linear-gradient(160deg, color-mix(in srgb, var(--app-accent) 22%, white), color-mix(in srgb, var(--app-accent) 10%, white));
  box-shadow: inset 0 -10px 20px rgba(0,0,0,.05), 0 16px 32px rgba(15, 23, 42, .08);
  position: relative;
  display: grid;
  place-items: center;
}

.eyes {
  position: absolute;
  top: 44px;
  display: flex;
  gap: 20px;
}

.eyes span {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: var(--app-text);
  transform-origin: center;
}

.mouth {
  position: absolute;
  top: 72px;
  width: 30px;
  height: 12px;
  border-bottom: 4px solid color-mix(in srgb, var(--app-accent) 80%, black);
  border-radius: 0 0 24px 24px;
}

.ask-avatar-caption {
  display: grid;
  gap: 4px;
  text-align: center;
}

.ask-avatar-label {
  font-size: 15px;
  font-weight: 800;
  color: var(--app-text);
}

.ask-avatar-state {
  font-size: 12px;
  color: var(--app-muted);
}

.ask-avatar--idle .ask-avatar-face {
  opacity: .92;
}

.ask-avatar--thinking .ask-avatar-face {
  animation: float 2.5s ease-in-out infinite;
}

.ask-avatar--listening .ask-avatar-face {
  animation: pulse 1.2s ease-in-out infinite;
}

.ask-avatar--speaking .ask-avatar-face {
  animation: pulse 0.9s ease-in-out infinite;
}

.ask-avatar--thinking .eyes span,
.ask-avatar--speaking .eyes span {
  width: 14px;
  height: 14px;
}

.ask-avatar--listening .mouth {
  width: 38px;
  height: 14px;
  border-bottom-width: 5px;
}

.ask-avatar--speaking .mouth {
  width: 42px;
  height: 18px;
  border-bottom-width: 6px;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}
</style>

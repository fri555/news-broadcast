<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { MessageCircle } from 'lucide-vue-next'

const BUTTON_SIZE = 48
const VISIBLE_EDGE = 28
const SAFE_TOP = 80
const SAFE_BOTTOM = 120
const TAP_SLOP = 6

const btnRef = ref<HTMLElement | null>(null)
const x = ref(window.innerWidth - VISIBLE_EDGE)
const y = ref(window.innerHeight - 160)
const dragging = ref(false)
const didDrag = ref(false)
const dragStart = ref({ x: 0, y: 0, btnX: 0, btnY: 0, pointerId: 0 })

function clampY(value: number) {
  return Math.max(SAFE_TOP, Math.min(window.innerHeight - SAFE_BOTTOM, value))
}

function clampX(value: number) {
  return Math.max(-BUTTON_SIZE + VISIBLE_EDGE, Math.min(window.innerWidth - VISIBLE_EDGE, value))
}

function dockToEdge() {
  const center = x.value + BUTTON_SIZE / 2
  x.value = center < window.innerWidth / 2 ? -BUTTON_SIZE + VISIBLE_EDGE : window.innerWidth - VISIBLE_EDGE
  y.value = clampY(y.value)
}

function updatePosition(clientX: number, clientY: number) {
  const dx = clientX - dragStart.value.x
  const dy = clientY - dragStart.value.y
  if (Math.hypot(dx, dy) > TAP_SLOP) didDrag.value = true
  x.value = clampX(dragStart.value.btnX + dx)
  y.value = clampY(dragStart.value.btnY + dy)
}

function onPointerDown(e: PointerEvent) {
  dragging.value = true
  didDrag.value = false
  dragStart.value = {
    x: e.clientX,
    y: e.clientY,
    btnX: x.value,
    btnY: y.value,
    pointerId: e.pointerId,
  }
  btnRef.value?.setPointerCapture(e.pointerId)
}

function onPointerMove(e: PointerEvent) {
  if (!dragging.value || e.pointerId !== dragStart.value.pointerId) return
  updatePosition(e.clientX, e.clientY)
}

function onPointerUp(e: PointerEvent) {
  if (e.pointerId !== dragStart.value.pointerId) return
  dragging.value = false
  btnRef.value?.releasePointerCapture(e.pointerId)
  dockToEdge()
}

function onResize() {
  x.value = clampX(x.value)
  y.value = clampY(y.value)
  dockToEdge()
}

function toggle() {
  if (didDrag.value) {
    setTimeout(() => { didDrag.value = false }, 0)
    return
  }
  window.dispatchEvent(new CustomEvent('toggle-ask-drawer'))
}

onMounted(() => {
  dockToEdge()
  window.addEventListener('resize', onResize)
})

onUnmounted(() => window.removeEventListener('resize', onResize))
</script>

<template>
  <Teleport to="body">
    <button
      ref="btnRef"
      class="fixed z-50 w-12 h-12 rounded-full bg-app-accent text-white flex items-center justify-center shadow-lg hover:shadow-xl active:scale-95 select-none touch-none will-change-transform"
      :class="dragging ? 'cursor-grabbing scale-110 shadow-2xl transition-none' : 'cursor-grab opacity-80 hover:opacity-100 transition-all duration-200'"
      :style="{ left: x + 'px', top: y + 'px' }"
      aria-label="打开追问"
      @pointerdown.prevent="onPointerDown"
      @pointermove.prevent="onPointerMove"
      @pointerup.prevent="onPointerUp"
      @pointercancel.prevent="onPointerUp"
      @click="toggle"
    >
      <MessageCircle class="w-5 h-5" />
    </button>
  </Teleport>
</template>

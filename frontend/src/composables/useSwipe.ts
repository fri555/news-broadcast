import { ref, onMounted, onUnmounted } from 'vue'

export function useSwipe(onLeft: () => void, onRight: () => void, threshold = 80) {
  const translateX = ref(0)
  const isDragging = ref(false)
  const element = ref<HTMLElement | null>(null)

  let startX = 0
  let startY = 0
  let isHorizontal: boolean | null = null
  let hasMoved = false

  function handleTouchStart(e: TouchEvent) {
    if (e.touches.length !== 1) return
    startX = e.touches[0].clientX
    startY = e.touches[0].clientY
    isDragging.value = true
    isHorizontal = null
    hasMoved = false
  }

  function handleTouchMove(e: TouchEvent) {
    if (!isDragging.value || e.touches.length !== 1) return
    const dx = e.touches[0].clientX - startX
    const dy = e.touches[0].clientY - startY

    if (isHorizontal === null) {
      if (Math.abs(dx) > 8 || Math.abs(dy) > 8) {
        isHorizontal = Math.abs(dx) > Math.abs(dy)
      }
    }

    if (isHorizontal) {
      e.preventDefault()
      hasMoved = true
    }

    translateX.value = isHorizontal ? dx : 0
  }

  function handleTouchEnd() {
    if (!isDragging.value) return
    if (isHorizontal && hasMoved) {
      if (translateX.value < -threshold) onLeft()
      else if (translateX.value > threshold) onRight()
    }
    // 关键：全部重置
    translateX.value = 0
    isDragging.value = false
    isHorizontal = null
    hasMoved = false
  }

  function onKeyDown(e: KeyboardEvent) {
    if (e.key === 'ArrowLeft') onLeft()
    if (e.key === 'ArrowRight') onRight()
  }

  function attach(el: HTMLElement) {
    element.value = el
    // 关键：用 addEventListener + { passive: false } 绕过浏览器被动事件限制
    el.addEventListener('touchstart', handleTouchStart, { passive: true })
    el.addEventListener('touchmove', handleTouchMove, { passive: false })
    el.addEventListener('touchend', handleTouchEnd, { passive: true })
    el.addEventListener('touchcancel', handleTouchEnd, { passive: true })
    window.addEventListener('keydown', onKeyDown)
  }

  function detach() {
    window.removeEventListener('keydown', onKeyDown)
    if (element.value) {
      element.value.removeEventListener('touchstart', handleTouchStart)
      element.value.removeEventListener('touchmove', handleTouchMove)
      element.value.removeEventListener('touchend', handleTouchEnd)
      element.value.removeEventListener('touchcancel', handleTouchEnd)
      element.value = null
    }
  }

  onUnmounted(detach)

  return { translateX, isDragging, attach, detach }
}

import { ref, onUnmounted } from 'vue'

export function useAudio(durationSec = 720) {
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(durationSec)
  const playbackRate = ref(1.0)
  let timer: ReturnType<typeof setInterval> | null = null

  function toggle() {
    isPlaying.value = !isPlaying.value
    if (isPlaying.value) {
      timer = setInterval(() => {
        if (currentTime.value < duration.value) currentTime.value += 1
        else { isPlaying.value = false; currentTime.value = 0 }
      }, 1000)
    } else {
      if (timer) { clearInterval(timer); timer = null }
    }
  }

  function seek(time: number) { currentTime.value = Math.max(0, Math.min(time, duration.value)) }
  function skip(seconds: number) { seek(currentTime.value + seconds) }
  function setSpeed(speed: number) { playbackRate.value = speed }

  onUnmounted(() => { if (timer) clearInterval(timer) })

  return { isPlaying, currentTime, duration, playbackRate, toggle, seek, skip, setSpeed }
}

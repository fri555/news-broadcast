import { ref, onUnmounted } from 'vue'

/**
 * 播客 TTS：使用浏览器内置 SpeechSynthesis 朗读字幕
 * 自动切换男/女声音
 */
export function useSpeechSynthesis() {
  const speaking = ref(false)
  const supported = ref(false)

  const synth = typeof window !== 'undefined' ? window.speechSynthesis : null
  supported.value = !!synth

  let pending = false

  function getVoice(gender: 'female' | 'male'): SpeechSynthesisVoice | null {
    if (!synth) return null
    const voices = synth.getVoices()
    // 优选中文女声/男声
    const femaleVoice = voices.find(v => v.lang.startsWith('zh') && (v.name.includes('Tingting') || v.name.includes('Meijia') || v.name.includes('Female') || v.name.includes('Yating')))
    const maleVoice = voices.find(v => v.lang.startsWith('zh') && (v.name.includes('Male') || v.name.includes('Qiang')))
    if (gender === 'female') return femaleVoice || voices.find(v => v.lang.startsWith('zh')) || null
    return maleVoice || femaleVoice || voices.find(v => v.lang.startsWith('zh')) || null
  }

  function speak(text: string, gender: 'female' | 'male' = 'female', rate = 1.0) {
    if (!synth) return
    synth.cancel()
    speaking.value = false
    pending = true

    // 等 voices 加载完
    const doSpeak = () => {
      if (!synth) return
      const voices = synth.getVoices()
      if (voices.length === 0) {
        setTimeout(doSpeak, 100)
        return
      }
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.voice = getVoice(gender)
      utterance.rate = rate
      utterance.pitch = gender === 'female' ? 1.2 : 0.9
      utterance.lang = 'zh-CN'
      utterance.onstart = () => { speaking.value = true; pending = false }
      utterance.onend = () => { speaking.value = false }
      utterance.onerror = () => { speaking.value = false }
      synth.speak(utterance)
    }

    doSpeak()
  }

  function stop() {
    synth?.cancel()
    speaking.value = false
    pending = false
  }

  onUnmounted(() => stop())

  return { speaking, supported, speak, stop }
}

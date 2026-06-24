import { ref, onUnmounted } from 'vue'

/**
 * 微信式语音识别：讲话时实时跳出文字（interimResults）
 */
export function useSpeechRecognition(lang = 'zh-CN') {
  const isListening = ref(false)
  const continuousMode = ref(false)
  const finalText = ref('')
  const interimText = ref('')  // 实时显示的中间结果
  const error = ref<string | null>(null)
  const supported = ref(false)

  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  supported.value = !!SpeechRecognition

  let recognition: any = null
  let manuallyStopped = false

  async function start(options?: { continuous?: boolean }) {
    if (!SpeechRecognition) {
      error.value = '当前浏览器不支持语音识别，请用 Chrome'
      return
    }
    try {
      if (navigator.mediaDevices?.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        stream.getTracks().forEach(track => track.stop())
      }
    } catch {
      error.value = '麦克风权限被拦截了，请允许当前页面使用麦克风。'
      isListening.value = false
      return
    }
    recognition?.abort()
    continuousMode.value = !!options?.continuous
    manuallyStopped = false
    error.value = null
    finalText.value = ''
    interimText.value = ''
    isListening.value = true

    recognition = new SpeechRecognition()
    recognition.continuous = continuousMode.value
    recognition.interimResults = true   // 微信式：实时返回中间结果
    recognition.lang = lang

    recognition.onresult = (event: any) => {
      let interim = ''
      let final = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i]
        if (result.isFinal) {
          final += result[0].transcript
        } else {
          interim += result[0].transcript
        }
      }
      interimText.value = interim
      if (final) {
        finalText.value = ''
        requestAnimationFrame(() => { finalText.value = final.trim() })
        interimText.value = ''
        if (!continuousMode.value) isListening.value = false
      }
    }

    recognition.onerror = (event: any) => {
      if (event.error === 'network') {
        error.value = '浏览器语音服务连不上。内置浏览器经常会这样，可以先用文字输入，或用 Chrome 打开本地页面再试。'
      } else if (event.error === 'not-allowed') {
        error.value = '麦克风权限被拦截了，请允许当前页面使用麦克风。'
      } else if (event.error === 'no-speech') {
        error.value = '没有听到清晰语音，请靠近一点再试。'
      } else {
        error.value = `语音识别失败：${event.error}`
      }
      isListening.value = false
      continuousMode.value = false
      manuallyStopped = true
    }

    recognition.onend = () => {
      if (continuousMode.value && !manuallyStopped) {
        try {
          recognition.start()
          isListening.value = true
          return
        } catch { /* restart can fail while browser is settling */ }
      }
      isListening.value = false
    }

    try {
      recognition.start()
    } catch {
      error.value = '语音识别启动失败，请检查麦克风权限'
      isListening.value = false
      continuousMode.value = false
    }
  }

  function stop() {
    manuallyStopped = true
    continuousMode.value = false
    recognition?.abort()
    isListening.value = false
  }

  onUnmounted(() => { recognition?.abort() })

  return { isListening, continuousMode, finalText, interimText, error, supported, start, stop }
}

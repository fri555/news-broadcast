let activeSpeech: HTMLAudioElement | null = null
let activeOwner = ''

export function stopSpeech(owner?: string) {
  if (!activeSpeech) return
  if (owner && owner !== activeOwner) return
  activeSpeech.pause()
  activeSpeech.currentTime = 0
  activeSpeech = null
  activeOwner = ''
}

export function claimSpeech(audio: HTMLAudioElement, owner: string) {
  stopSpeech()
  activeSpeech = audio
  activeOwner = owner

  const clear = () => {
    if (activeSpeech === audio) {
      activeSpeech = null
      activeOwner = ''
    }
  }

  audio.addEventListener('ended', clear, { once: true })
  audio.addEventListener('error', clear, { once: true })
  audio.addEventListener('pause', () => {
    if (audio.currentTime === 0 || audio.ended) clear()
  }, { once: true })
}

export function isClaimedSpeech(audio: HTMLAudioElement | null, owner: string) {
  return !!audio && activeSpeech === audio && activeOwner === owner
}

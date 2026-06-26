<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import AskAvatar from './AskAvatar.vue'

const props = defineProps<{
  state: 'idle' | 'listening' | 'thinking' | 'speaking'
  label?: string
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const ready = ref(false)
const failed = ref(false)
let app: any = null
let model: any = null

const moodText = computed(() => {
  if (props.state === 'listening') return '听你说话'
  if (props.state === 'thinking') return '正在思考'
  if (props.state === 'speaking') return '正在回答'
  return '随时追问'
})

function loadScript(src: string) {
  return new Promise<void>((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = src
    script.async = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error(`Failed to load ${src}`))
    document.head.appendChild(script)
  })
}

async function initLive2D() {
  if (!canvasRef.value || ready.value || failed.value) return
  try {
    await loadScript('https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js')
    await loadScript('https://cdn.jsdelivr.net/npm/pixi.js@6.5.10/dist/browser/pixi.min.js')
    await loadScript('https://cdn.jsdelivr.net/npm/pixi-live2d-display@0.4.0/dist/index.min.js')

    const PIXI = (window as any).PIXI
    const Live2DModel = (window as any).PIXI?.live2d?.Live2DModel
    if (!PIXI || !Live2DModel) throw new Error('Live2D runtime unavailable')

    app = new PIXI.Application({
      view: canvasRef.value,
      width: 220,
      height: 180,
      transparent: true,
      autoStart: true,
    })

    const modelUrl = import.meta.env.VITE_LIVE2D_MODEL_URL
      || 'https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/haru/haru.model3.json'
    model = await Live2DModel.from(modelUrl)
    model.scale.set(0.16)
    model.x = 100
    model.y = 20
    app.stage.addChild(model)
    ready.value = true
  } catch {
    failed.value = true
  }
}

watch(() => props.state, (state) => {
  if (!model) return
  model.internalModel.motionManager.expressionManager?.setExpression(
    state === 'listening' ? 1 : state === 'thinking' ? 2 : 0,
  )
})

onMounted(initLive2D)
onUnmounted(() => {
  try { app?.destroy(true) } catch { /* ignore */ }
  app = null
  model = null
})
</script>

<template>
  <div v-if="!failed" class="live2d-shell">
    <canvas ref="canvasRef" class="live2d-canvas" />
    <div class="live2d-caption">
      <p class="live2d-label">{{ label || '小暖' }}</p>
      <p class="live2d-state">{{ ready ? moodText : '加载形象中' }}</p>
    </div>
  </div>
  <AskAvatar v-else :state="state" :label="label || '小暖'" />
</template>

<style scoped>
.live2d-shell {
  position: relative;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 18px;
  background:
    radial-gradient(circle at 50% 20%, color-mix(in srgb, var(--app-accent) 16%, transparent), transparent 42%),
    var(--app-card2);
  border: 1px solid var(--app-border);
}

.live2d-canvas {
  width: 220px;
  height: 180px;
  max-width: 100%;
}

.live2d-caption {
  position: absolute;
  right: 12px;
  bottom: 10px;
  text-align: right;
}

.live2d-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--app-text);
}

.live2d-state {
  font-size: 10px;
  color: var(--app-muted);
}
</style>

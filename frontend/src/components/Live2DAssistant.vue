<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps<{
  state: 'idle' | 'listening' | 'thinking' | 'speaking'
  label?: string
}>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
const ready = ref(false)
const failed = ref(false)
const loadingText = ref('加载形象中')
const pointerX = ref(0)
const pointerY = ref(0)
let app: any = null
let model: any = null

const MODEL_CANDIDATES = [
  import.meta.env.VITE_LIVE2D_MODEL_URL,
  'https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/haru/haru_greeter_t03.model3.json',
  'https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/haru/haru.model3.json',
  'https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/shizuku/shizuku.model.json',
].filter(Boolean)

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
    loadingText.value = '加载运行时'
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

    loadingText.value = '加载模型'
    let loadedModel: any = null
    for (const modelUrl of MODEL_CANDIDATES) {
      try {
        loadedModel = await Live2DModel.from(modelUrl)
        break
      } catch { /* try next model */ }
    }
    if (!loadedModel) throw new Error('No Live2D model loaded')

    model = loadedModel
    const bounds = model.getBounds?.()
    const scale = bounds?.width ? Math.min(0.28, 140 / bounds.width) : 0.16
    model.scale.set(scale)
    model.x = 110
    model.y = 12
    app.stage.addChild(model)
    ready.value = true
  } catch {
    failed.value = true
    loadingText.value = '模型不可用'
  }
}

function setParameter(id: string, value: number) {
  try {
    model?.internalModel?.coreModel?.setParameterValueById(id, value)
  } catch { /* unsupported model/runtime */ }
}

function handlePointer(event: PointerEvent) {
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const x = ((event.clientX - rect.left) / rect.width - 0.5) * 2
  const y = ((event.clientY - rect.top) / rect.height - 0.5) * 2
  pointerX.value = x
  pointerY.value = y
  if (model) {
    setParameter('ParamAngleX', x * 22)
    setParameter('ParamAngleY', -y * 14)
    setParameter('ParamBodyAngleX', x * 8)
  }
}

function triggerMotion() {
  if (!model) return
  try {
    const expressions = model.internalModel.motionManager.expressionManager
    expressions?.setRandomExpression?.()
    model.motion?.('TapBody')
  } catch { /* optional interaction */ }
}

watch(() => props.state, (state) => {
  if (!model) return
  try {
    model.internalModel.motionManager.expressionManager?.setExpression(
      state === 'listening' ? 1 : state === 'thinking' ? 2 : 0,
    )
  } catch { /* expression index may not exist */ }
})

onMounted(initLive2D)
onUnmounted(() => {
  try { app?.destroy(true) } catch { /* ignore */ }
  app = null
  model = null
})
</script>

<template>
  <div
    class="live2d-shell"
    :class="{ 'live2d-shell--fallback': failed, 'live2d-shell--ready': ready }"
    @pointermove="handlePointer"
    @click="triggerMotion"
  >
    <canvas v-show="!failed" ref="canvasRef" class="live2d-canvas" />
    <div v-if="failed" class="fallback-model" :class="`fallback-model--${state}`">
      <div class="fallback-hair" />
      <div class="fallback-head" :style="{ transform: `rotate(${pointerX * 8}deg) translate(${pointerX * 4}px, ${pointerY * 3}px)` }">
        <span class="fallback-eye fallback-eye-left" />
        <span class="fallback-eye fallback-eye-right" />
        <span class="fallback-mouth" />
      </div>
      <div class="fallback-body" />
    </div>
    <div class="live2d-caption">
      <p class="live2d-label">{{ label || '小暖' }}</p>
      <p class="live2d-state">{{ ready ? moodText : failed ? '互动形象' : loadingText }}</p>
    </div>
  </div>
</template>

<style scoped>
.live2d-shell {
  position: relative;
  min-height: 178px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border-radius: 18px;
  background:
    radial-gradient(circle at 50% 20%, color-mix(in srgb, var(--app-accent) 16%, transparent), transparent 42%),
    var(--app-card2);
  border: 1px solid var(--app-border);
  cursor: pointer;
  isolation: isolate;
}

.live2d-canvas {
  width: 240px;
  height: 190px;
  max-width: 100%;
}

.live2d-shell--ready {
  background:
    radial-gradient(circle at 50% 16%, color-mix(in srgb, var(--app-accent) 20%, transparent), transparent 44%),
    linear-gradient(180deg, color-mix(in srgb, var(--app-card2) 90%, white), var(--app-card2));
}

.fallback-model {
  position: relative;
  width: 132px;
  height: 150px;
  animation: idleFloat 3.4s ease-in-out infinite;
}

.fallback-head {
  position: absolute;
  left: 28px;
  top: 22px;
  width: 78px;
  height: 88px;
  border-radius: 42% 42% 48% 48%;
  background: linear-gradient(180deg, #ffe2cf, #ffc8b4);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.14);
  transition: transform 0.18s ease;
  z-index: 2;
}

.fallback-hair {
  position: absolute;
  left: 18px;
  top: 8px;
  width: 98px;
  height: 92px;
  border-radius: 48% 48% 36% 36%;
  background: linear-gradient(145deg, #6b3b2a, #2f1b18);
  z-index: 1;
}

.fallback-body {
  position: absolute;
  left: 24px;
  bottom: 0;
  width: 86px;
  height: 58px;
  border-radius: 34px 34px 18px 18px;
  background: linear-gradient(145deg, var(--app-accent), #ef4444);
  z-index: 0;
}

.fallback-eye {
  position: absolute;
  top: 38px;
  width: 8px;
  height: 12px;
  border-radius: 999px;
  background: #3b241f;
  animation: blink 4.2s infinite;
}

.fallback-eye-left { left: 23px; }
.fallback-eye-right { right: 23px; }

.fallback-mouth {
  position: absolute;
  left: 33px;
  top: 61px;
  width: 14px;
  height: 7px;
  border-bottom: 3px solid #9f4f45;
  border-radius: 0 0 999px 999px;
}

.fallback-model--listening .fallback-eye {
  background: var(--app-accent);
}

.fallback-model--thinking {
  animation-duration: 1.7s;
}

.fallback-model--speaking .fallback-mouth {
  height: 12px;
  border: 0;
  background: #9f4f45;
  border-radius: 999px;
  animation: speakMouth 0.36s infinite alternate;
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

@keyframes idleFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

@keyframes blink {
  0%, 92%, 100% { transform: scaleY(1); }
  95% { transform: scaleY(0.1); }
}

@keyframes speakMouth {
  from { transform: scaleY(0.7); }
  to { transform: scaleY(1.35); }
}
</style>

<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import type { PodcastEpisode } from '@/types'

const props = defineProps<{ episode: PodcastEpisode; currentTime: number }>()
const scrollContainer = ref<HTMLElement>()

const activeIndex = computed(() =>
  props.episode.transcript.findIndex(
    (line, i) => props.currentTime >= line.startTime &&
      props.currentTime < (props.episode.transcript[i + 1]?.startTime ?? line.endTime)
  )
)

watch(activeIndex, async () => {
  await nextTick()
  if (scrollContainer.value) {
    const el = scrollContainer.value.querySelector('.lyric-active') as HTMLElement
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
})
</script>

<template>
  <div ref="scrollContainer"
    class="flex-1 overflow-y-auto scrollbar-hide py-8 px-7 min-h-0"
    style="mask-image: linear-gradient(to bottom, transparent 0%, black 12%, black 88%, transparent 100%); -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 12%, black 88%, transparent 100%);"
  >
    <div class="h-[40vh]" />
    <div
      v-for="(line, i) in episode.transcript" :key="i"
      class="text-center py-4 transition-all duration-500 cursor-pointer"
      :class="{ 'lyric-active': i === activeIndex, 'opacity-30': i < activeIndex - 1 }"
    >
      <p
        class="text-[10px] font-bold tracking-widest uppercase mb-1 transition-all duration-500"
        :class="i === activeIndex ? 'opacity-100' : 'opacity-0'"
        :style="{ color: line.speaker === episode.hosts[0].name ? episode.hosts[0].voiceColor : episode.hosts[1].voiceColor }"
      >🎙️ {{ line.speaker }}</p>
      <p
        class="leading-relaxed transition-all duration-500"
        :class="[
          i === activeIndex ? '!text-white !font-semibold text-[22px] leading-snug' : 'text-white/30',
          i < activeIndex && i >= activeIndex - 2 ? '!text-white/45' : '',
          i !== activeIndex ? 'text-[17px]' : '',
        ]"
      >{{ line.text }}</p>
    </div>
    <div class="h-[40vh]" />
  </div>
</template>

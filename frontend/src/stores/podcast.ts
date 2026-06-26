import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PodcastEpisode, BroadcastResult, TranscriptLine, PodcastChapter } from '@/types'
import { podcastApi } from '@/api'

export const usePodcastStore = defineStore('podcast', () => {
  const episode = ref<PodcastEpisode | null>(null)
  const broadcast = ref<BroadcastResult | null>(null)
  const loading = ref(false)

  const currentTranscript = computed<TranscriptLine | null>(() => null)

  async function fetchLatest(userId = 'default') {
    loading.value = true
    try {
      const data = await podcastApi.latest(userId)
      if (data.message) {
        // Backend says "generate first"
        episode.value = null
      } else {
        episode.value = data as PodcastEpisode
      }
    } catch {
      episode.value = null
    } finally {
      loading.value = false
    }
  }

  /**
   * 从新闻列表生成广播脚本
   */
  async function generateBroadcast(news: { title: string; summary: string; source: string; topic: string }[], userId = 'default') {
    loading.value = true
    try {
      const result = await podcastApi.broadcast(news, userId)
      broadcast.value = result
      await fetchLatest(userId)
      if (episode.value) return

      // 将 BroadcastResult 转换为 PodcastEpisode 格式
      const script = result.script
      const charsPerSec = 3
      let elapsed = 0
      const transcript: TranscriptLine[] = []
      const chapters: PodcastChapter[] = []
      let chapterIdx = 0

      for (let i = 0; i < script.length; i++) {
        const line = script[i]
        const lineSecs = Math.max(2, Math.ceil(line.text.length / charsPerSec))
        const speakerName = line.speaker === 'A' ? '小暖' : '小明'

        if (i === 0 || i % 5 === 0) {
          chapterIdx++
          chapters.push({
            id: `ch${chapterIdx}`,
            title: line.text.slice(0, 24) + '...',
            startTime: Math.round(elapsed),
          })
        }

        transcript.push({
          speaker: speakerName,
          text: line.text,
          startTime: Math.round(elapsed),
          endTime: Math.round(elapsed + lineSecs),
        })
        elapsed += lineSecs
      }

      episode.value = {
        id: `ep-${new Date().toISOString().slice(0, 10)}-${new Date().getHours()}`,
        title: 'NewsCast 今日新闻播报',
        date: new Date().toISOString().slice(0, 10),
        duration: Math.max(900, Math.round(elapsed), Math.round(result.estimated_minutes * 60)),
        hosts: [
          { name: '小暖', gender: 'female', voiceColor: '#f97316' },
          { name: '小明', gender: 'male', voiceColor: '#3b82f6' },
        ],
        chapters: chapters.slice(0, 20),
        transcript,
      }
    } catch (e) {
      console.error('Broadcast generation failed:', e)
    } finally {
      loading.value = false
    }
  }

  return { episode, broadcast, loading, currentTranscript, fetchLatest, generateBroadcast }
})

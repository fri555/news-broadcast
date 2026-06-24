<script setup lang="ts">
import type { NewsItem } from '@/types'
import { ExternalLink, TrendingUp } from 'lucide-vue-next'
import NewsCover from './NewsCover.vue'

const props = defineProps<{ item: NewsItem; compact?: boolean }>()
const emit = defineEmits<{ detail: [item: NewsItem] }>()

function cardSummary(item: NewsItem) {
  const parts = [
    item.summary,
    item.detail?.one_liner,
    item.detail?.background,
    item.detail?.impact,
  ].filter(Boolean)
  const merged = Array.from(new Set(parts)).join(' ')
  const limit = props.compact ? 120 : 160
  return merged.length > limit ? `${merged.slice(0, limit)}...` : merged
}

function shortTitle(title: string) {
  const clean = title
    .replace(/\s+/g, ' ')
    .replace(/[｜\-—|]/g, ' ')
    .trim()
  const parts = clean.split(/[：:，,。．·]/).map(s => s.trim()).filter(Boolean)
  const stripped = parts
    .map(part => part.replace(/^(消息称|据悉|快讯|突发|最新|关注|报道|发布|宣布|回应|提醒|提示|看点|盘前|盘后|今晚|今日)/, ''))
    .filter(Boolean)
  const primary = stripped.find(p => Array.from(p).length >= 4) || parts.find(p => Array.from(p).length >= 4) || clean
  const chars = Array.from(primary)
  const limit = props.compact ? 7 : 8
  return chars.length > limit ? `${chars.slice(0, limit).join('')}…` : primary
}
</script>

<template>
  <div
    class="news-card bg-app-card rounded-card p-4 shadow-md border border-app-border cursor-pointer active:scale-[0.98] transition-transform overflow-hidden"
    :class="compact ? 'news-card--compact flex items-start gap-3' : 'news-card--regular flex flex-col'"
    @click="emit('detail', item)"
  >
    <div class="news-card-media" :class="compact ? 'w-[112px] shrink-0' : 'mb-3'">
      <NewsCover :item="item" :compact="compact" />
    </div>

    <div class="news-card-body min-w-0 flex-1 flex flex-col" :class="compact ? 'pt-0.5' : ''">
      <!-- 标签：领域 + 热度 -->
      <div class="flex items-center gap-2 mb-2.5 shrink-0">
        <span class="bg-app-accent-light text-app-accent text-xs font-bold px-3 py-1 rounded-full tracking-wide">
          {{ item.category || item.topic || '综合' }}
        </span>
        <span v-if="item.hot_value" class="flex items-center gap-0.5 text-[10px] text-app-muted">
          <TrendingUp class="w-3 h-3" /> {{ item.hot_value.slice(0, 6) }}
        </span>
      </div>

      <!-- 来源 + 时间 -->
      <div class="flex items-center gap-2 mb-2 text-[13px] shrink-0">
        <span class="font-semibold text-app-accent">{{ item.source }}</span>
        <span class="text-app-muted">· {{ item.publishedAt }}</span>
      </div>

      <!-- 标题 -->
      <h3 class="news-card-title text-app-text font-bold leading-relaxed mb-2 min-h-0" :class="compact ? 'text-[15px] line-clamp-2' : 'text-lg line-clamp-2'">
        {{ shortTitle(item.title) }}
      </h3>

      <!-- AI 摘要 -->
      <p class="news-card-summary text-sm text-app-sub leading-relaxed min-h-0" :class="compact ? 'news-card-summary--compact' : 'news-card-summary--regular'">
        {{ cardSummary(item) }}
      </p>

      <!-- 底部 -->
      <div class="flex justify-between mt-auto pt-2.5 border-t border-app-divider text-[11px] leading-none shrink-0">
        <span class="text-app-muted">点击查看详情</span>
        <span class="text-app-accent font-medium flex items-center gap-1 whitespace-nowrap">
          详情 <ExternalLink class="w-3 h-3" />
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.news-card {
  height: clamp(355px, calc(100vh - 295px), 430px);
}

.news-card--compact {
  height: auto;
  min-height: 148px;
}

.news-card-media {
  width: 100%;
}

.news-card--compact .news-card-media {
  margin-bottom: 0;
}

.news-card--compact .news-card-body {
  padding-top: 2px;
}

.news-card-body {
  min-height: 0;
}

.news-card-summary {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
}

.news-card-summary--regular {
  -webkit-line-clamp: 4;
}

.news-card-summary--compact {
  -webkit-line-clamp: 3;
}

@media (min-width: 1024px) {
  .news-card {
    height: 340px;
  }
}
</style>

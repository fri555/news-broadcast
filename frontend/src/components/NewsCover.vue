<script setup lang="ts">
import type { NewsItem } from '@/types'

const props = defineProps<{ item: NewsItem; compact?: boolean }>()

function hashText(text: string) {
  let hash = 0
  for (let i = 0; i < text.length; i++) hash = (hash * 31 + text.charCodeAt(i)) >>> 0
  return hash
}

function category() {
  const topic = `${props.item.topic || ''} ${props.item.category || ''} ${props.item.title}`
  if (/财经|股|市场|金融|基金|债|A股|港股|美股|投资/.test(topic)) return 'market'
  if (/AI|科技|芯片|模型|手机|互联网|数码|机器人|OpenAI/.test(topic)) return 'tech'
  if (/国际|时政|外交|美国|欧洲|日本|总统|政策|政府/.test(topic)) return 'world'
  if (/娱乐|电影|游戏|音乐|综艺|明星|票房|B站/.test(topic)) return 'culture'
  return 'general'
}

function topicCode() {
  const map: Record<string, string> = {
    market: 'MARKET',
    tech: 'TECH / AI',
    world: 'WORLD',
    culture: 'CULTURE',
    general: 'NEWS',
  }
  return map[category()]
}

function keywords() {
  const text = `${props.item.title} ${props.item.summary} ${props.item.detail?.one_liner || ''}`
    .replace(/[，。、“”‘’：《》？?！!（）()【】]/g, ' ')
  const stop = new Set(['一个', '这个', '以及', '今日', '新闻', '最新', '相关', '表示', '发布', '当前'])
  const tokens = text
    .split(/\s+/)
    .map(t => t.trim())
    .filter(t => t.length >= 2 && t.length <= 8 && !stop.has(t))
  return Array.from(new Set(tokens)).slice(0, 3)
}

function coverCopy() {
  const titleTokens = keywordsFrom(props.item.title)
  const contextTokens = keywords()
  const distinct = contextTokens.filter(t => !titleTokens.includes(t))
  const primaryPool = distinct.length > 0 ? distinct : contextTokens
  const lead = sliceText(primaryPool[0] || topicCode(), 8) || topicCode()
  const support = sliceText(primaryPool.slice(1, 3).join(' · ') || titleTokens[0] || props.item.source, 14)
  return { lead, support }
}

function keywordsFrom(text: string) {
  const stop = new Set(['一个', '这个', '以及', '今日', '新闻', '最新', '相关', '表示', '发布', '当前'])
  return Array.from(new Set(
    text
      .replace(/[，。、“”‘’：《》？?！!（）()【】｜\-—|]/g, ' ')
      .split(/\s+/)
      .map(t => t.trim())
      .filter(t => t.length >= 2 && t.length <= 8 && !stop.has(t)),
  ))
}

function sliceText(text: string, maxChars: number) {
  const chars = Array.from(text)
  return chars.length > maxChars ? `${chars.slice(0, maxChars).join('')}…` : text
}

function titleStyle() {
  const len = Array.from(coverCopy().lead).length
  const familyMap: Record<string, string> = {
    market: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif',
    tech: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace',
    world: 'ui-serif, "Songti SC", "STSong", serif',
    culture: 'ui-serif, "STKaiti", "KaiTi", serif',
    general: 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif',
  }
  return {
    fontFamily: familyMap[category()],
    fontSize: len > 10 ? '13px' : len > 8 ? '14px' : '15px',
  }
}

function coverStyle() {
  const hash = hashText(`${props.item.title}${props.item.source}`)
  const hue = hash % 360
  const palette: Record<string, string> = {
    market: `linear-gradient(135deg, hsl(155, 65%, 88%), hsl(195, 72%, 76%))`,
    tech: `linear-gradient(135deg, hsl(${hue}, 76%, 90%), hsl(${(hue + 54) % 360}, 82%, 74%))`,
    world: `linear-gradient(135deg, hsl(218, 68%, 88%), hsl(32, 76%, 78%))`,
    culture: `linear-gradient(135deg, hsl(332, 76%, 89%), hsl(42, 88%, 76%))`,
    general: `linear-gradient(135deg, hsl(${hue}, 66%, 90%), hsl(${(hue + 110) % 360}, 72%, 78%))`,
  }
  const image = (props.item.image || '').trim()
  if (image) {
    return {
      backgroundImage:
        `linear-gradient(180deg, rgba(255,255,255,.28), rgba(0,0,0,.16)), ` +
        `linear-gradient(135deg, rgba(255,255,255,.18), rgba(0,0,0,.06)), url(${image})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundBlendMode: 'overlay, soft-light, normal',
    }
  }
  return {
    background:
      `radial-gradient(circle at ${22 + hash % 58}% ${18 + hash % 46}%, rgba(255,255,255,.62), transparent 35%), ` +
      palette[category()],
  }
}

function coverToneClass() {
  return {
    market: 'cover-tone-market',
    tech: 'cover-tone-tech',
    world: 'cover-tone-world',
    culture: 'cover-tone-culture',
    general: 'cover-tone-general',
  }[category()]
}
</script>

<template>
  <div class="news-cover" :class="[ `cover-${category()}`, compact ? 'news-cover--compact' : '' ]" :style="coverStyle()">
    <template v-if="category() === 'market'">
      <div class="cover-top">
        <span>{{ topicCode() }}</span>
        <b>{{ item.source }}</b>
      </div>
      <div class="market-chart" aria-hidden="true">
        <i style="height: 38%" /><i style="height: 64%" /><i style="height: 48%" /><i style="height: 76%" /><i style="height: 58%" />
      </div>
      <div class="cover-copy" :class="coverToneClass()">
        <p class="cover-lead" :style="titleStyle()">{{ coverCopy().lead }}</p>
        <p class="cover-support">{{ coverCopy().support }}</p>
      </div>
      <div v-if="!compact" class="cover-tags"><span v-for="kw in keywords()" :key="kw">{{ kw }}</span></div>
    </template>

    <template v-else-if="category() === 'tech'">
      <div class="cover-top">
        <span>{{ topicCode() }}</span>
        <b>{{ item.source }}</b>
      </div>
      <div class="tech-grid" aria-hidden="true">
        <i /><i /><i /><i /><i /><i />
      </div>
      <div class="cover-copy" :class="coverToneClass()">
        <p class="cover-lead" :style="titleStyle()">{{ coverCopy().lead }}</p>
        <p class="cover-support">{{ coverCopy().support }}</p>
      </div>
      <div v-if="!compact" class="cover-tags"><span v-for="kw in keywords()" :key="kw">{{ kw }}</span></div>
    </template>

    <template v-else-if="category() === 'world'">
      <div class="cover-top">
        <span>{{ topicCode() }}</span>
        <b>{{ item.source }}</b>
      </div>
      <div class="world-map" aria-hidden="true">
        <i /><i /><i />
      </div>
      <div class="cover-copy" :class="coverToneClass()">
        <p class="cover-lead" :style="titleStyle()">{{ coverCopy().lead }}</p>
        <p class="cover-support">{{ coverCopy().support }}</p>
      </div>
      <div v-if="!compact" class="cover-tags"><span v-for="kw in keywords()" :key="kw">{{ kw }}</span></div>
    </template>

    <template v-else-if="category() === 'culture'">
      <div class="cover-top">
        <span>{{ topicCode() }}</span>
        <b>{{ item.source }}</b>
      </div>
      <p class="magazine-mark">CAST</p>
      <div class="cover-copy" :class="coverToneClass()">
        <p class="cover-lead" :style="titleStyle()">{{ coverCopy().lead }}</p>
        <p class="cover-support">{{ coverCopy().support }}</p>
      </div>
      <div v-if="!compact" class="cover-tags"><span v-for="kw in keywords()" :key="kw">{{ kw }}</span></div>
    </template>

    <template v-else>
      <div class="cover-top">
        <span>{{ topicCode() }}</span>
        <b>{{ item.source }}</b>
      </div>
      <div class="general-lines" aria-hidden="true">
        <i /><i /><i />
      </div>
      <div class="cover-copy" :class="coverToneClass()">
        <p class="cover-lead" :style="titleStyle()">{{ coverCopy().lead }}</p>
        <p class="cover-support">{{ coverCopy().support }}</p>
      </div>
      <div v-if="!compact" class="cover-tags"><span v-for="kw in keywords()" :key="kw">{{ kw }}</span></div>
    </template>
  </div>
</template>

<style scoped>
.news-cover {
  position: relative;
  height: 120px;
  border-radius: 12px;
  overflow: hidden;
  padding: 12px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  isolation: isolate;
}

.news-cover--compact {
  height: 96px;
  padding: 10px;
}

.news-cover::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,.12), rgba(0,0,0,.12));
  z-index: -1;
}

.cover-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
  font-size: 10px;
  color: rgba(0,0,0,.68);
}

.cover-top span,
.cover-top b,
.cover-tags span {
  border-radius: 999px;
  background: rgba(255,255,255,.45);
  backdrop-filter: blur(8px);
  padding: 4px 8px;
  white-space: nowrap;
}

.cover-top b {
  max-width: 108px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cover-copy {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 72%;
}

.cover-lead {
  position: relative;
  color: rgba(0,0,0,.78);
  font-size: 17px;
  line-height: 1.05;
  font-weight: 900;
  text-shadow: 0 1px 0 rgba(255,255,255,.35);
}

.news-cover--compact .cover-lead {
  font-size: 14px;
}

.cover-support {
  font-size: 11px;
  line-height: 1.2;
  font-weight: 700;
  color: rgba(0,0,0,.58);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.cover-tone-tech .cover-lead { letter-spacing: .2px; }
.cover-tone-world .cover-lead { font-style: italic; }
.cover-tone-culture .cover-lead { transform: rotate(-1deg); }
.cover-tone-market .cover-lead { letter-spacing: -0.2px; }

.cover-tags {
  display: flex;
  gap: 5px;
  overflow: hidden;
}

.cover-tags span {
  font-size: 10px;
  color: rgba(0,0,0,.62);
  font-weight: 700;
  max-width: 86px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.market-chart {
  position: absolute;
  right: 12px;
  bottom: 28px;
  display: flex;
  gap: 5px;
  align-items: end;
  height: 56px;
  opacity: .48;
}

.market-chart i {
  width: 8px;
  border-radius: 999px 999px 0 0;
  background: rgba(0, 80, 60, .45);
}

.tech-grid {
  position: absolute;
  right: 12px;
  top: 38px;
  display: grid;
  grid-template-columns: repeat(3, 18px);
  gap: 6px;
  opacity: .42;
}

.tech-grid i {
  width: 18px;
  height: 18px;
  border: 1px solid rgba(0,0,0,.22);
  border-radius: 5px;
  background: rgba(255,255,255,.2);
}

.world-map {
  position: absolute;
  right: -10px;
  bottom: 20px;
  width: 118px;
  height: 70px;
  opacity: .35;
}

.world-map i {
  position: absolute;
  border-radius: 42% 58% 54% 46%;
  background: rgba(0,0,0,.28);
}

.world-map i:nth-child(1) { width: 54px; height: 32px; left: 8px; top: 6px; }
.world-map i:nth-child(2) { width: 42px; height: 28px; left: 58px; top: 22px; }
.world-map i:nth-child(3) { width: 28px; height: 18px; left: 34px; top: 45px; }

.magazine-mark {
  position: absolute;
  right: 10px;
  bottom: 22px;
  color: rgba(0,0,0,.16);
  font-weight: 950;
  font-size: 38px;
  letter-spacing: 1px;
}

.general-lines {
  position: absolute;
  right: 12px;
  bottom: 30px;
  display: grid;
  gap: 7px;
  width: 92px;
  opacity: .4;
}

.general-lines i {
  height: 8px;
  border-radius: 999px;
  background: rgba(0,0,0,.24);
}

.general-lines i:nth-child(2) { width: 72%; margin-left: auto; }
.general-lines i:nth-child(3) { width: 52%; margin-left: 20%; }
</style>

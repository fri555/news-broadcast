# NewsCast Phase 1 MVP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从零搭建 NewsCast 前端应用（Vue3+TS），含全部4个页面、模拟数据、响应式布局、主题切换，可本地运行体验。

**Architecture:** 前端 Vue3 SPA + Mock 数据（无需后端即可运行），后续对接 FastAPI 后端。前端用 Pinia 管理状态，Vue Router 管理路由，Tailwind + shadcn/ui + Lucide + inspira-ui 做样式和动效。

**Tech Stack:** Vue 3.4+ · TypeScript 5.x · Vite 5.x · Tailwind CSS 3.x · shadcn-vue · Lucide Icons · inspira-ui · Pinia · Vue Router 4.x

---

## 文件结构总览

```
news-broadcast/
├── README.md
├── backend/                          # Phase 2 开始填充
│   └── .gitkeep
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── components.json              # shadcn-vue 配置
│   ├── index.html
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── style.css                # Tailwind + 主题变量
│       ├── router/index.ts
│       ├── stores/
│       │   ├── news.ts              # 新闻数据 + 模拟数据
│       │   ├── podcast.ts           # 播客数据 + 播放状态
│       │   ├── ask.ts               # 追问对话
│       │   ├── theme.ts             # 主题切换
│       │   └── preferences.ts       # 用户偏好
│       ├── types/index.ts           # TypeScript 类型定义
│       ├── composables/
│       │   ├── useSwipe.ts          # 卡片滑动手势
│       │   └── useAudio.ts          # 音频播放控制
│       ├── components/
│       │   ├── ui/                  # shadcn-vue 组件
│       │   │   ├── Button.vue
│       │   │   ├── Input.vue
│       │   │   ├── Badge.vue
│       │   │   ├── Slider.vue
│       │   │   ├── Switch.vue
│       │   │   ├── Sheet.vue
│       │   │   ├── Skeleton.vue
│       │   │   ├── ScrollArea.vue
│       │   │   ├── Separator.vue
│       │   │   └── Tooltip.vue
│       │   ├── AppShell.vue         # 响应式壳：移动Tab / 桌面侧栏
│       │   ├── MobileBottomTab.vue  # 底部四Tab导航
│       │   ├── DesktopSidebar.vue   # 桌面侧栏导航
│       │   ├── FloatingAskButton.vue # 可拖拽浮动FAB
│       │   ├── NewsCard.vue         # 单张新闻卡片
│       │   ├── CardStack.vue        # 卡片堆叠+滑动逻辑
│       │   ├── PodcastPlayer.vue    # 播客音频播放器
│       │   ├── SubtitleArea.vue     # 歌词式字幕滚动
│       │   ├── ChatBubble.vue       # 对话气泡
│       │   ├── AskDrawer.vue        # 追问底部抽屉
│       │   ├── ThemeSwitcher.vue    # 主题切换组件
│       │   └── EmptyState.vue       # 空状态
│       ├── pages/
│       │   ├── CardNewsPage.vue     # 📰 新闻卡片页
│       │   ├── PodcastPage.vue      # 🎧 播客页
│       │   ├── AskPage.vue          # 💬 追问页
│       │   └── MePage.vue           # 👤 我的页
│       └── data/
│           ├── mock-news.ts         # 模拟新闻数据
│           └── mock-podcast.ts      # 模拟播客数据
└── docs/
    └── superpowers/
        ├── specs/
        │   ├── 2026-06-20-news-broadcast-prd.md
        │   └── 2026-06-20-news-broadcast-ui-design.md
        └── plans/
            └── 2026-06-20-news-broadcast-phase1-mvp.md
```

---

### Task 1: 项目脚手架 — Vue3 + Vite + 依赖安装

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.app.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/components.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/style.css`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/types/index.ts`
- Create: `backend/.gitkeep`
- Create: `README.md`
- Create: `frontend/.gitignore`

- [ ] **Step 1: 创建项目目录结构**

```bash
mkdir -p /Users/richelleshi/news-broadcast/backend
mkdir -p /Users/richelleshi/news-broadcast/frontend/src/{router,stores,composables,components/ui,pages,data,types}
mkdir -p /Users/richelleshi/news-broadcast/frontend/public
mkdir -p /Users/richelleshi/news-broadcast/docs/superpowers/{specs,plans}
```

- [ ] **Step 2: 创建 package.json**

```json
{
  "name": "news-cast",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc -b && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.38",
    "vue-router": "^4.4.3",
    "pinia": "^2.2.2",
    "lucide-vue-next": "^0.441.0",
    "radix-vue": "^1.9.6",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.3",
    "tailwindcss-animate": "^1.0.7"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.3",
    "typescript": "~5.5.4",
    "vite": "^5.4.8",
    "vue-tsc": "^2.1.6",
    "tailwindcss": "^3.4.12",
    "postcss": "^8.4.47",
    "autoprefixer": "^10.4.20",
    "@types/node": "^22.5.5"
  }
}
```

- [ ] **Step 3: 创建 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
```

- [ ] **Step 4: 创建 TypeScript 配置文件**

`frontend/tsconfig.json`:
```json
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.node.json" }
  ]
}
```

`frontend/tsconfig.app.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForEmits": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue", "env.d.ts"]
}
```

`frontend/tsconfig.node.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "strict": true,
    "noUnusedLocals": false,
    "noUnusedParameters": false,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 5: 创建 env.d.ts**

```typescript
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}
```

- [ ] **Step 6: 创建 Tailwind + PostCSS 配置**

`frontend/tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        warm: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12',
        },
      },
      borderRadius: {
        'card': '22px',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', '"PingFang SC"', '"Hiragino Sans GB"', '"Microsoft YaHei"', '"Helvetica Neue"', 'Helvetica', 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
```

`frontend/postcss.config.js`:
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 7: 创建 shadcn-vue 配置**

`frontend/components.json`:
```json
{
  "$schema": "https://shadcn-vue.com/schema.json",
  "style": "default",
  "typescript": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/style.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "framework": "vite",
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

- [ ] **Step 8: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no" />
    <meta name="theme-color" content="#f97316" />
    <title>NewsCast - 个性化新闻播报</title>
  </head>
  <body class="bg-warm-50 text-stone-900 antialiased">
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

- [ ] **Step 9: 创建 main.ts + App.vue + style.css**

`frontend/src/main.ts`:
```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
```

`frontend/src/style.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 30 33% 98%;
    --foreground: 24 10% 10%;
    --card: 0 0% 100%;
    --card-foreground: 24 10% 10%;
    --primary: 24 95% 53%;
    --primary-foreground: 0 0% 100%;
    --muted: 30 20% 92%;
    --muted-foreground: 24 5% 45%;
    --border: 30 20% 90%;
    --radius: 1.25rem;
  }

  .theme-warm {
    --background: 30 33% 98%;
    --foreground: 24 10% 10%;
    --primary: 24 95% 53%;
    --primary-foreground: 0 0% 100%;
  }

  .theme-pro {
    --background: 214 30% 96%;
    --foreground: 222 47% 11%;
    --primary: 221 83% 33%;
    --primary-foreground: 0 0% 100%;
  }

  .theme-mini {
    --background: 60 5% 96%;
    --foreground: 24 6% 10%;
    --primary: 24 6% 15%;
    --primary-foreground: 0 0% 100%;
  }

  .theme-dark {
    --background: 24 10% 10%;
    --foreground: 30 20% 98%;
    --primary: 24 95% 53%;
    --primary-foreground: 0 0% 100%;
    --card: 24 8% 15%;
    --card-foreground: 30 20% 98%;
    --border: 24 8% 25%;
  }

  * { @apply border-stone-200; }
  body {
    @apply bg-stone-50 text-stone-900;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  }
  .theme-dark body { @apply bg-stone-900 text-stone-50; }
  .theme-dark * { @apply border-stone-700; }
}

@layer utilities {
  .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
  .scrollbar-hide::-webkit-scrollbar { display: none; }
}
```

`frontend/src/App.vue`:
```vue
<script setup lang="ts">
import AppShell from './components/AppShell.vue'
</script>

<template>
  <AppShell />
</template>
```

- [ ] **Step 10: 创建路由**

`frontend/src/router/index.ts`:
```typescript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/news',
    },
    {
      path: '/news',
      name: 'news',
      component: () => import('@/pages/CardNewsPage.vue'),
    },
    {
      path: '/podcast',
      name: 'podcast',
      component: () => import('@/pages/PodcastPage.vue'),
    },
    {
      path: '/ask',
      name: 'ask',
      component: () => import('@/pages/AskPage.vue'),
    },
    {
      path: '/me',
      name: 'me',
      component: () => import('@/pages/MePage.vue'),
    },
  ],
})

export default router
```

- [ ] **Step 11: 创建 TypeScript 类型定义**

`frontend/src/types/index.ts`:
```typescript
export interface NewsItem {
  id: string
  category: string
  title: string
  summary: string
  source: string
  sourceUrl: string
  imageUrl?: string
  publishedAt: string
  isRead: boolean
}

export interface PodcastEpisode {
  id: string
  title: string
  date: string
  duration: number
  hosts: { name: string; gender: 'female' | 'male'; voiceColor: string }[]
  chapters: PodcastChapter[]
  transcript: TranscriptLine[]
  audioUrl?: string
}

export interface PodcastChapter {
  id: string
  title: string
  startTime: number
}

export interface TranscriptLine {
  speaker: string
  text: string
  startTime: number
  endTime: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
  context?: {
    type: 'news' | 'podcast'
    id: string
    title: string
  }
}

export interface UserPreferences {
  interests: string[]
  pushTimes: string[]
  theme: 'theme-warm' | 'theme-pro' | 'theme-mini' | 'theme-dark'
  companion: CompanionSettings
}

export interface CompanionSettings {
  name: string
  personality: '亲和温暖' | '干练知性' | '幽默活泼' | '沉稳深度'
  voiceId: string
  speed: number
  addressAs: string
}

export type TabName = 'news' | 'podcast' | 'ask' | 'me'
```

- [ ] **Step 12: 安装依赖**

```bash
cd /Users/richelleshi/news-broadcast/frontend && npm install
```

- [ ] **Step 13: 验证项目可启动**

```bash
cd /Users/richelleshi/news-broadcast/frontend && npm run dev
```

Expected: Vite dev server starts, opening `http://localhost:5173` shows blank page (no pages created yet, but no build errors).

- [ ] **Step 14: Commit**

```bash
cd /Users/richelleshi/news-broadcast
git add -A
git commit -m "feat: scaffold Vue3+TS+Vite project with Tailwind and shadcn-vue config"
```

---

### Task 2: 模拟数据 + Pinia Stores

**Files:**
- Create: `frontend/src/data/mock-news.ts`
- Create: `frontend/src/data/mock-podcast.ts`
- Create: `frontend/src/stores/news.ts`
- Create: `frontend/src/stores/podcast.ts`
- Create: `frontend/src/stores/ask.ts`
- Create: `frontend/src/stores/theme.ts`
- Create: `frontend/src/stores/preferences.ts`

- [ ] **Step 1: 创建模拟新闻数据**

`frontend/src/data/mock-news.ts`:
```typescript
import type { NewsItem } from '@/types'

export const mockNews: NewsItem[] = [
  {
    id: '1',
    category: '科技 · 深度',
    title: 'Apple 发布新一代 AI 芯片 M5 Ultra，端侧推理性能提升 3 倍',
    summary: '采用全新 3nm+ 制程，神经网络引擎核心翻倍至 32 核，统一内存带宽达到 800GB/s，支持在 iPhone/iPad 上本地运行百亿参数大模型。开发者表示这将彻底改变移动端 AI 应用格局。',
    source: '36氪',
    sourceUrl: '#',
    publishedAt: '15分钟前',
    isRead: false,
  },
  {
    id: '2',
    category: '财经 · 快讯',
    title: 'A股三大指数集体收涨，两市成交额突破万亿',
    summary: '沪指涨 0.8%，深成指涨 1.2%，创业板指涨 2.1%，北向资金净流入超 80 亿元。分析人士认为市场信心正在恢复。',
    source: '证券时报',
    sourceUrl: '#',
    publishedAt: '30分钟前',
    isRead: false,
  },
  {
    id: '3',
    category: '体育 · 热点',
    title: '中国队 3:1 击败对手，世界杯预选赛再下一城',
    summary: '凭借下半场两粒精彩进球，中国队在主场拿下关键三分，小组排名升至第二，出线形势大好。',
    source: '央视体育',
    sourceUrl: '#',
    publishedAt: '1小时前',
    isRead: false,
  },
  {
    id: '4',
    category: '国际 · 深度',
    title: '联合国气候变化报告：全球升温需控制在 1.5°C 以内',
    summary: '最新报告指出当前各国减排承诺仍不足以实现目标，呼吁采取更激进措施。2025年全球碳排放再创历史新高。',
    source: 'BBC中文',
    sourceUrl: '#',
    publishedAt: '2小时前',
    isRead: false,
  },
  {
    id: '5',
    category: '科技 · AI',
    title: 'OpenAI 发布 GPT-5，多模态推理能力大幅提升',
    summary: '新模型在数学、编程、科学推理等基准测试中全面超越前代，首次支持原生视频理解和生成能力。',
    source: '机器之心',
    sourceUrl: '#',
    publishedAt: '3小时前',
    isRead: false,
  },
  {
    id: '6',
    category: '科技 · 快讯',
    title: '特斯拉 Robotaxi 正式在旧金山开放公众运营',
    summary: '首批 500 辆无人驾驶出租车开始载客，用户可通过 App 叫车，价格约为传统网约车的 60%。',
    source: '品玩',
    sourceUrl: '#',
    publishedAt: '4小时前',
    isRead: false,
  },
  {
    id: '7',
    category: '健康 · 科普',
    title: '研究发现：每天步行 8000 步可显著降低心血管疾病风险',
    summary: '哈佛大学最新研究追踪 10 万人长达 5 年，结果显示每日步行量与心血管健康呈显著正相关。',
    source: '丁香医生',
    sourceUrl: '#',
    publishedAt: '5小时前',
    isRead: false,
  },
  {
    id: '8',
    category: '娱乐 · 热点',
    title: '《黑神话：悟空》DLC 官宣，新增 6 个章节',
    summary: '游戏科学宣布首个大型资料片将于今年秋季上线，新增地图面积约为本体的 40%，包含全新战斗系统和Boss。',
    source: '游研社',
    sourceUrl: '#',
    publishedAt: '6小时前',
    isRead: false,
  },
]
```

- [ ] **Step 2: 创建模拟播客数据**

`frontend/src/data/mock-podcast.ts`:
```typescript
import type { PodcastEpisode } from '@/types'

export const mockPodcast: PodcastEpisode = {
  id: 'ep-2026-06-20-08',
  title: 'AI芯片大战升级，全球科技格局重塑',
  date: '2026-06-20',
  duration: 720,
  hosts: [
    { name: '小暖', gender: 'female', voiceColor: '#f97316' },
    { name: '小明', gender: 'male', voiceColor: '#3b82f6' },
  ],
  chapters: [
    { id: 'ch1', title: '开场 · 今日要闻概览', startTime: 0 },
    { id: 'ch2', title: 'M5 Ultra 深度解读', startTime: 120 },
    { id: 'ch3', title: '开发者生态影响分析', startTime: 310 },
    { id: 'ch4', title: '竞品对比：华为昇腾 vs Google TPU', startTime: 480 },
    { id: 'ch5', title: '用户互动问答', startTime: 620 },
  ],
  transcript: [
    { speaker: '小暖', text: '早上好！欢迎收听今天的晨间新闻，我是小暖。', startTime: 0, endTime: 4 },
    { speaker: '小明', text: '我是小明。今天是6月20日，我们先来看看今天有哪些重要新闻。', startTime: 5, endTime: 10 },
    { speaker: '小暖', text: '首先来看科技圈的重磅消息——Apple 今天凌晨正式发布了 M5 Ultra 芯片。', startTime: 12, endTime: 19 },
    { speaker: '小明', text: '没错，这次升级真的很大。端侧推理性能直接翻了 3 倍，采用台积电 3nm+ 制程。', startTime: 21, endTime: 29 },
    { speaker: '小暖', text: '神经网络引擎从 16 核升级到 32 核，统一内存带宽达到 800GB/s。', startTime: 31, endTime: 38 },
    { speaker: '小明', text: '这意味着以后很多 AI 功能都不用联网了，隐私和速度都有质的飞跃。', startTime: 40, endTime: 46 },
    { speaker: '小暖', text: '对于开发者来说，可以在端侧跑百亿参数的大模型，这会彻底改变移动端 AI 应用的格局。', startTime: 48, endTime: 56 },
    { speaker: '小明', text: '接下来看看财经方面的消息——A股三大指数今天集体收涨。', startTime: 58, endTime: 64 },
    { speaker: '小暖', text: '沪指涨 0.8%，深成指涨 1.2%，两市成交额突破万亿，市场情绪明显回暖。', startTime: 66, endTime: 74 },
    { speaker: '小明', text: '体育方面也有好消息——中国队在世界杯预选赛中 3:1 击败对手，小组排名升至第二。', startTime: 76, endTime: 83 },
    { speaker: '小暖', text: '下半场的两粒进球非常精彩，球迷们对出线前景充满期待。', startTime: 85, endTime: 91 },
    { speaker: '小明', text: '好的，以上就是今天的新闻要点。接下来我们深入聊聊 M5 Ultra 这个话题。', startTime: 93, endTime: 100 },
  ],
}
```

- [ ] **Step 3: 创建 Pinia Stores**

`frontend/src/stores/news.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { mockNews } from '@/data/mock-news'
import type { NewsItem } from '@/types'

export const useNewsStore = defineStore('news', () => {
  const items = ref<NewsItem[]>(mockNews)
  const currentIndex = ref(0)
  const readIds = ref<Set<string>>(new Set())

  const currentItem = computed(() => items.value[currentIndex.value] ?? null)
  const totalCount = computed(() => items.value.length)
  const unreadCount = computed(() => items.value.filter(n => !readIds.value.has(n.id)).length)

  function markRead(id: string) {
    readIds.value.add(id)
  }

  function next() {
    if (currentIndex.value < items.value.length - 1) {
      if (currentItem.value) markRead(currentItem.value.id)
      currentIndex.value++
    }
  }

  function previous() {
    if (currentIndex.value > 0) {
      currentIndex.value--
    }
  }

  function goTo(index: number) {
    if (index >= 0 && index < items.value.length) {
      currentIndex.value = index
    }
  }

  return { items, currentIndex, readIds, currentItem, totalCount, unreadCount, markRead, next, previous, goTo }
})
```

`frontend/src/stores/podcast.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { mockPodcast } from '@/data/mock-podcast'
import type { TranscriptLine } from '@/types'

export const usePodcastStore = defineStore('podcast', () => {
  const episode = ref(mockPodcast)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const playbackRate = ref(1.0)
  const activeTranscriptIndex = ref(-1)

  const currentTranscript = computed<TranscriptLine | null>(() =>
    episode.value.transcript.find(
      (line, i) => currentTime.value >= line.startTime && currentTime.value < line.endTime
    ) ?? null
  )

  const progress = computed(() =>
    episode.value.duration > 0 ? (currentTime.value / episode.value.duration) * 100 : 0
  )

  function togglePlay() { isPlaying.value = !isPlaying.value }
  function seek(time: number) { currentTime.value = Math.max(0, Math.min(time, episode.value.duration)) }
  function setSpeed(speed: number) { playbackRate.value = speed }
  function skip(seconds: number) { seek(currentTime.value + seconds) }

  return { episode, isPlaying, currentTime, playbackRate, currentTranscript, progress, togglePlay, seek, setSpeed, skip }
})
```

`frontend/src/stores/ask.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage } from '@/types'

export const useAskStore = defineStore('ask', () => {
  const messages = ref<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: '你好！我是 NewsCast AI 助手。有什么想深入了解的吗？比如技术细节、市场影响、还是竞品对比？',
      timestamp: Date.now() - 120000,
      context: { type: 'news', id: '1', title: 'Apple M5 Ultra 芯片发布' },
    },
  ])
  const isTyping = ref(false)
  const currentContext = ref<{ type: 'news' | 'podcast'; id: string; title: string } | null>({
    type: 'news', id: '1', title: 'Apple M5 Ultra 芯片发布',
  })

  function sendMessage(content: string) {
    messages.value.push({
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: Date.now(),
    })
    isTyping.value = true

    setTimeout(() => {
      messages.value.push({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `关于「${content}」，这是一个很好的问题！\n\nM5 Ultra 芯片的核心突破在于：\n\n1️⃣ **制程升级**：从 5nm 跳跃到 3nm+，能效比提升 40%\n2️⃣ **神经引擎翻倍**：16核→32核，AI 算力直接翻番\n3️⃣ **内存带宽翻倍**：400GB/s→800GB/s\n\n这意味着在你的 iPhone 上就能本地运行百亿参数的大模型，不需要联网，隐私和速度都有质的飞跃。`,
        timestamp: Date.now(),
      })
      isTyping.value = false
    }, 1500)
  }

  return { messages, isTyping, currentContext, sendMessage }
})
```

`frontend/src/stores/theme.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref, watchEffect } from 'vue'

export type Theme = 'theme-warm' | 'theme-pro' | 'theme-mini' | 'theme-dark'

export const useThemeStore = defineStore('theme', () => {
  const current = ref<Theme>((localStorage.getItem('theme') as Theme) || 'theme-warm')

  watchEffect(() => {
    document.documentElement.className = current.value
    localStorage.setItem('theme', current.value)
  })

  function setTheme(theme: Theme) {
    current.value = theme
  }

  const themes = [
    { value: 'theme-warm' as const, label: '温暖陪伴', color: 'bg-gradient-to-br from-orange-100 to-orange-500' },
    { value: 'theme-pro' as const, label: '专业克制', color: 'bg-gradient-to-br from-blue-900 to-slate-900' },
    { value: 'theme-mini' as const, label: '现代极简', color: 'bg-gradient-to-br from-stone-50 to-stone-300' },
    { value: 'theme-dark' as const, label: '暗夜沉浸', color: 'bg-gradient-to-br from-stone-800 to-black' },
  ]

  return { current, setTheme, themes }
})
```

`frontend/src/stores/preferences.ts`:
```typescript
import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import type { UserPreferences, CompanionSettings } from '@/types'

const DEFAULT_PREFS: UserPreferences = {
  interests: ['科技', '财经', '国际', 'AI', '创投'],
  pushTimes: ['8:00', '18:00', '22:00'],
  theme: 'theme-warm',
  companion: {
    name: '小暖',
    personality: '亲和温暖',
    voiceId: 'mimo-female-a',
    speed: 1.0,
    addressAs: '朋友',
  },
}

export const usePreferencesStore = defineStore('preferences', () => {
  const saved = localStorage.getItem('preferences')
  const prefs = ref<UserPreferences>(saved ? { ...DEFAULT_PREFS, ...JSON.parse(saved) } : DEFAULT_PREFS)

  watch(prefs, (val) => {
    localStorage.setItem('preferences', JSON.stringify(val))
  }, { deep: true })

  function updatePrefs(partial: Partial<UserPreferences>) {
    Object.assign(prefs.value, partial)
  }

  function updateCompanion(partial: Partial<CompanionSettings>) {
    Object.assign(prefs.value.companion, partial)
  }

  function toggleInterest(tag: string) {
    const idx = prefs.value.interests.indexOf(tag)
    if (idx === -1) prefs.value.interests.push(tag)
    else prefs.value.interests.splice(idx, 1)
  }

  return { prefs, updatePrefs, updateCompanion, toggleInterest }
})
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add mock data and Pinia stores for news, podcast, ask, theme, preferences"
```

---

### Task 3: 响应式应用壳 — AppShell + 导航

**Files:**
- Create: `frontend/src/components/AppShell.vue`
- Create: `frontend/src/components/MobileBottomTab.vue`
- Create: `frontend/src/components/DesktopSidebar.vue`
- Create: `frontend/src/lib/utils.ts`

- [ ] **Step 1: 创建 utils.ts**

`frontend/src/lib/utils.ts`:
```typescript
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

- [ ] **Step 2: 创建 MobileBottomTab.vue**

`frontend/src/components/MobileBottomTab.vue`:
```vue
<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { Newspaper, Podcast, MessageCircle, User } from 'lucide-vue-next'
import type { TabName } from '@/types'

const route = useRoute()
const router = useRouter()

const tabs: { name: TabName; icon: typeof Newspaper; label: string; path: string }[] = [
  { name: 'news', icon: Newspaper, label: '新闻', path: '/news' },
  { name: 'podcast', icon: Podcast, label: '播客', path: '/podcast' },
  { name: 'ask', icon: MessageCircle, label: '追问', path: '/ask' },
  { name: 'me', icon: User, label: '我的', path: '/me' },
]

const activeTab = computed<TabName>(() => {
  const name = route.name as string
  return (name as TabName) || 'news'
})

function go(tab: typeof tabs[0]) {
  router.push(tab.path)
}
</script>

<template>
  <nav class="flex justify-around items-center px-4 pb-6 pt-2 bg-white border-t border-stone-100 safe-area-bottom lg:hidden">
    <button
      v-for="tab in tabs"
      :key="tab.name"
      @click="go(tab)"
      class="flex flex-col items-center gap-1 px-3 py-1 transition-colors"
      :class="activeTab === tab.name ? 'text-warm-500' : 'text-stone-400'"
    >
      <component :is="tab.icon" class="w-6 h-6" :stroke-width="activeTab === tab.name ? 2.5 : 1.5" />
      <span class="text-[10px] font-medium">{{ tab.label }}</span>
    </button>
  </nav>
</template>
```

- [ ] **Step 3: 创建 DesktopSidebar.vue**

`frontend/src/components/DesktopSidebar.vue`:
```vue
<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { Newspaper, Podcast, MessageCircle, User } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const navItems = [
  { name: 'news', icon: Newspaper, label: '新闻', path: '/news' },
  { name: 'podcast', icon: Podcast, label: '播客', path: '/podcast' },
  { name: 'ask', icon: MessageCircle, label: '追问', path: '/ask' },
  { name: 'me', icon: User, label: '我的', path: '/me' },
]

const active = computed(() => route.name as string)

function go(item: typeof navItems[0]) {
  router.push(item.path)
}
</script>

<template>
  <aside class="hidden lg:flex flex-col items-center w-18 py-6 gap-1 bg-stone-50 border-r border-stone-100">
    <div class="text-2xl mb-6 text-warm-500 font-bold">N</div>
    <button
      v-for="item in navItems"
      :key="item.name"
      @click="go(item)"
      class="w-12 h-12 rounded-2xl flex flex-col items-center justify-center gap-0.5 text-[10px] transition-all"
      :class="active === item.name ? 'bg-warm-50 text-warm-500' : 'text-stone-400 hover:text-stone-600'"
    >
      <component :is="item.icon" class="w-5 h-5" />
      <span>{{ item.label }}</span>
    </button>
  </aside>
</template>
```

- [ ] **Step 4: 创建 AppShell.vue（响应式壳）**

`frontend/src/components/AppShell.vue`:
```vue
<script setup lang="ts">
import MobileBottomTab from './MobileBottomTab.vue'
import DesktopSidebar from './DesktopSidebar.vue'
import FloatingAskButton from './FloatingAskButton.vue'
</script>

<template>
  <div class="flex h-dvh w-full overflow-hidden bg-stone-50">
    <!-- 桌面端侧栏 -->
    <DesktopSidebar />

    <!-- 主内容区 -->
    <main class="flex-1 overflow-y-auto scrollbar-hide">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 移动端底部Tab -->
    <MobileBottomTab />

    <!-- 浮动追问按钮 -->
    <FloatingAskButton />
  </div>
</template>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.15s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add responsive AppShell with mobile tabs and desktop sidebar"
```

---

### Task 4: 浮动追问按钮（可拖拽+贴边吸附）

**Files:**
- Create: `frontend/src/components/FloatingAskButton.vue`

- [ ] **Step 1: 创建 FloatingAskButton.vue**

`frontend/src/components/FloatingAskButton.vue`:
```vue
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Plus } from 'lucide-vue-next'
import { useAskStore } from '@/stores/ask'

const askStore = useAskStore()
const fabRef = ref<HTMLButtonElement>()
const x = ref(0)
const y = ref(0)
const dragging = ref(false)
const snapped = ref<'left' | 'right'>('right')
const opacity = ref(0.65)

let startX = 0, startY = 0, startLeft = 0, startTop = 0
let hasMoved = false

function initPosition() {
  x.value = window.innerWidth - 72
  y.value = window.innerHeight - 160
}

function snap() {
  const cx = x.value + 24
  if (cx < window.innerWidth / 2) {
    x.value = 4
    snapped.value = 'left'
  } else {
    x.value = window.innerWidth - 52
    snapped.value = 'right'
  }
  y.value = Math.max(80, Math.min(window.innerHeight - 140, y.value))
}

function onPointerDown(e: PointerEvent) {
  dragging.value = true
  hasMoved = false
  opacity.value = 1
  startX = e.clientX; startY = e.clientY
  startLeft = x.value; startTop = y.value
  e.preventDefault()
}

function onPointerMove(e: PointerEvent) {
  if (!dragging.value) return
  const dx = e.clientX - startX, dy = e.clientY - startY
  if (Math.abs(dx) > 3 || Math.abs(dy) > 3) hasMoved = true
  x.value = startLeft + dx
  y.value = startTop + dy
}

function onPointerUp() {
  if (!dragging.value) return
  dragging.value = false
  opacity.value = 0.65
  snap()
}

function onClick() {
  if (hasMoved) return
  // 触发追问抽屉
  window.dispatchEvent(new CustomEvent('toggle-ask-drawer'))
}

onMounted(() => {
  initPosition()
  snap()
  window.addEventListener('resize', snap)
})

onUnmounted(() => {
  window.removeEventListener('resize', snap)
})
</script>

<template>
  <button
    ref="fabRef"
    class="fixed z-50 w-12 h-12 rounded-full bg-warm-500 text-white flex items-center justify-center shadow-lg shadow-warm-500/25 transition-all duration-300 cursor-grab active:cursor-grabbing lg:hidden"
    :class="{
      'opacity-100 scale-110 shadow-xl': dragging,
      'rounded-l-full': snapped === 'right' && !dragging,
      'rounded-r-full': snapped === 'left' && !dragging,
    }"
    :style="{
      left: x + 'px',
      top: y + 'px',
      opacity: dragging ? 1 : opacity,
    }"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @click="onClick"
  >
    <Plus class="w-6 h-6" />
  </button>
</template>
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "feat: add draggable floating ask button with edge snapping"
```

---

### Task 5: 新闻卡片页 — 横向滑动

**Files:**
- Create: `frontend/src/components/NewsCard.vue`
- Create: `frontend/src/components/CardStack.vue`
- Create: `frontend/src/composables/useSwipe.ts`
- Create: `frontend/src/pages/CardNewsPage.vue`

- [ ] **Step 1: 创建 useSwipe composable**

`frontend/src/composables/useSwipe.ts`:
```typescript
import { ref, onUnmounted } from 'vue'

export function useSwipe(onSwipeLeft: () => void, onSwipeRight: () => void, threshold = 80) {
  const translateX = ref(0)
  const isDragging = ref(false)
  let startX = 0

  function onTouchStart(e: TouchEvent) {
    startX = e.touches[0].clientX
    isDragging.value = true
  }

  function onTouchMove(e: TouchEvent) {
    if (!isDragging.value) return
    translateX.value = e.touches[0].clientX - startX
  }

  function onTouchEnd() {
    if (!isDragging.value) return
    if (translateX.value < -threshold) onSwipeLeft()
    else if (translateX.value > threshold) onSwipeRight()
    translateX.value = 0
    isDragging.value = false
  }

  function onKeyDown(e: KeyboardEvent) {
    if (e.key === 'ArrowLeft') onSwipeLeft()
    if (e.key === 'ArrowRight') onSwipeRight()
  }

  window.addEventListener('keydown', onKeyDown)
  onUnmounted(() => window.removeEventListener('keydown', onKeyDown))

  return { translateX, isDragging, onTouchStart, onTouchMove, onTouchEnd }
}
```

- [ ] **Step 2: 创建 NewsCard.vue**

`frontend/src/components/NewsCard.vue`:
```vue
<script setup lang="ts">
import type { NewsItem } from '@/types'
import { Badge } from '@/components/ui/Badge.vue'

defineProps<{ item: NewsItem }>()
</script>

<template>
  <div class="bg-white rounded-card p-6 shadow-md border border-orange-50 flex flex-col min-h-[400px] select-none">
    <Badge class="self-start mb-4 bg-orange-50 text-orange-600 hover:bg-orange-50 text-xs font-bold px-3 py-1 rounded-full">
      {{ item.category }}
    </Badge>
    <div class="flex items-center gap-2 mb-4 text-sm">
      <span class="font-semibold text-orange-500">{{ item.source }}</span>
      <span class="text-stone-400">· {{ item.publishedAt }}</span>
    </div>
    <div class="w-full h-40 bg-gradient-to-br from-orange-100 to-orange-200 rounded-xl mb-5 flex items-center justify-center text-5xl">
      {{ item.category.includes('科技') ? '🧠' : item.category.includes('财经') ? '📈' : item.category.includes('体育') ? '⚽' : '🌍' }}
    </div>
    <h3 class="text-xl font-bold leading-relaxed mb-3 text-stone-900">{{ item.title }}</h3>
    <p class="text-stone-500 leading-relaxed flex-1">{{ item.summary }}</p>
    <div class="flex justify-between mt-4 pt-4 border-t border-stone-100 text-xs text-stone-300">
      <span>👈 跳过</span>
      <span>详情 👉</span>
    </div>
  </div>
</template>
```

- [ ] **Step 3: 创建 CardStack.vue**

`frontend/src/components/CardStack.vue`:
```vue
<script setup lang="ts">
import { useNewsStore } from '@/stores/news'
import { useSwipe } from '@/composables/useSwipe'
import NewsCard from './NewsCard.vue'
import { computed } from 'vue'

const store = useNewsStore()

const { translateX, onTouchStart, onTouchMove, onTouchEnd } = useSwipe(
  () => store.next(),
  () => store.previous(),
)

const cardStyle = computed(() => ({
  transform: `translateX(${translateX.value}px) rotate(${translateX.value * 0.05}deg)`,
  transition: translateX.value === 0 ? 'transform 0.3s ease' : 'none',
  opacity: translateX.value ? 1 - Math.abs(translateX.value) / 400 : 1,
}))
</script>

<template>
  <div
    v-if="store.currentItem"
    class="relative px-5"
    @touchstart.passive="onTouchStart"
    @touchmove.passive="onTouchMove"
    @touchend="onTouchEnd"
  >
    <!-- 背景层：下一张卡片 -->
    <div
      v-if="store.currentIndex < store.items.length - 1"
      class="absolute inset-x-5 top-2 scale-[0.96] opacity-30"
    >
      <NewsCard :item="store.items[store.currentIndex + 1]" />
    </div>

    <!-- 当前卡片 -->
    <div :style="cardStyle" class="relative z-10">
      <NewsCard :item="store.currentItem" />
    </div>
  </div>

  <div v-else class="flex items-center justify-center h-64 text-stone-400">
    暂无新闻
  </div>
</template>
```

- [ ] **Step 4: 创建 CardNewsPage.vue**

`frontend/src/pages/CardNewsPage.vue`:
```vue
<script setup lang="ts">
import { useNewsStore } from '@/stores/news'
import CardStack from '@/components/CardStack.vue'

const store = useNewsStore()
</script>

<template>
  <div class="flex flex-col h-full pt-2 pb-4">
    <div class="flex justify-between items-center px-5 py-3">
      <h1 class="text-2xl font-bold text-stone-900">今日新闻</h1>
      <span class="text-sm text-stone-400">6月20日 周四</span>
    </div>

    <!-- 进度指示器 -->
    <div class="flex items-center gap-1.5 px-5 mb-4">
      <div
        v-for="(_, i) in store.items"
        :key="i"
        class="h-1.5 rounded-full transition-all duration-300"
        :class="i === store.currentIndex ? 'w-5 bg-warm-500' : i < store.currentIndex ? 'w-1.5 bg-warm-400' : 'w-1.5 bg-stone-200'"
      />
      <span class="text-xs text-stone-400 ml-auto">第 {{ store.currentIndex + 1 }}/{{ store.totalCount }} 条</span>
    </div>

    <CardStack />
  </div>
</template>
```

- [ ] **Step 5: 验证页面可查看**

```bash
cd /Users/richelleshi/news-broadcast/frontend && npm run dev
```

打开 `http://localhost:5173/news`，确认：新闻卡片显示、进度条、触摸滑动可用（移动端模拟器）、键盘← →可用。

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: add news card page with horizontal swipe interaction"
```

---

### Task 6: 播客页 — 歌词模式播放器

**Files:**
- Create: `frontend/src/components/PodcastPlayer.vue`
- Create: `frontend/src/components/SubtitleArea.vue`
- Create: `frontend/src/pages/PodcastPage.vue`
- Create: `frontend/src/composables/useAudio.ts`

- [ ] **Step 1: 创建 useAudio composable**

`frontend/src/composables/useAudio.ts`:
```typescript
import { ref, onUnmounted } from 'vue'

export function useAudio() {
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(720)
  const playbackRate = ref(1.0)
  let timer: ReturnType<typeof setInterval> | null = null

  function toggle() {
    isPlaying.value = !isPlaying.value
    if (isPlaying.value) {
      timer = setInterval(() => {
        if (currentTime.value < duration.value) {
          currentTime.value += 1
        } else {
          isPlaying.value = false
          currentTime.value = 0
        }
      }, 1000)
    } else {
      if (timer) { clearInterval(timer); timer = null }
    }
  }

  function seek(time: number) {
    currentTime.value = Math.max(0, Math.min(time, duration.value))
  }

  function skip(seconds: number) {
    seek(currentTime.value + seconds)
  }

  function setSpeed(speed: number) {
    playbackRate.value = speed
  }

  onUnmounted(() => { if (timer) clearInterval(timer) })

  return { isPlaying, currentTime, duration, playbackRate, toggle, seek, skip, setSpeed }
}
```

- [ ] **Step 2: 创建 SubtitleArea.vue（歌词模式）**

`frontend/src/components/SubtitleArea.vue`:
```vue
<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import type { PodcastEpisode } from '@/types'

const props = defineProps<{
  episode: PodcastEpisode
  currentTime: number
}>()

const scrollContainer = ref<HTMLElement>()

const activeIndex = computed(() => {
  return props.episode.transcript.findIndex(
    (line, i) =>
      props.currentTime >= line.startTime &&
      props.currentTime < (props.episode.transcript[i + 1]?.startTime ?? line.endTime)
  )
})

watch(activeIndex, async () => {
  await nextTick()
  if (scrollContainer.value) {
    const activeEl = scrollContainer.value.querySelector('.lyric-active') as HTMLElement
    if (activeEl) {
      activeEl.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
})
</script>

<template>
  <div
    ref="scrollContainer"
    class="flex-1 overflow-y-auto scrollbar-hide py-8 px-7"
    style="mask-image: linear-gradient(to bottom, transparent 0%, black 12%, black 88%, transparent 100%); -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 12%, black 88%, transparent 100%);"
  >
    <div class="h-[40vh]" />
    <div
      v-for="(line, i) in episode.transcript"
      :key="i"
      class="text-center py-4 transition-all duration-500 cursor-pointer"
      :class="{
        'lyric-active': i === activeIndex,
        'opacity-30': i < activeIndex,
      }"
    >
      <p
        class="text-[10px] font-bold tracking-widest uppercase mb-1 transition-all duration-500"
        :class="i === activeIndex ? 'opacity-100' : 'opacity-0'"
        :style="{ color: line.speaker === episode.hosts[0].name ? episode.hosts[0].voiceColor : episode.hosts[1].voiceColor }"
      >
        🎙️ {{ line.speaker }}
      </p>
      <p
        class="leading-relaxed text-white/30 transition-all duration-500"
        :class="{
          '!text-white !font-semibold text-[22px] leading-snug': i === activeIndex,
          '!text-white/45': i < activeIndex && i >= activeIndex - 2,
          'text-[17px]': i !== activeIndex,
        }"
      >
        {{ line.text }}
      </p>
    </div>
    <div class="h-[40vh]" />
  </div>
</template>
```

- [ ] **Step 3: 创建 PodcastPlayer.vue**

`frontend/src/components/PodcastPlayer.vue`:
```vue
<script setup lang="ts">
import { usePodcastStore } from '@/stores/podcast'
import { useAudio } from '@/composables/useAudio'
import SubtitleArea from './SubtitleArea.vue'
import { computed } from 'vue'
import { ChevronDown, Ellipsis, Play, Pause, SkipBack, SkipForward } from 'lucide-vue-next'

const store = usePodcastStore()
const { isPlaying, currentTime, playbackRate, toggle, seek, skip, setSpeed } = useAudio()

const progress = computed(() => (currentTime.value / 720) * 100)
const currentStr = computed(() => {
  const m = Math.floor(currentTime.value / 60)
  const s = Math.floor(currentTime.value % 60)
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})
const durationStr = computed(() => {
  const m = Math.floor(720 / 60)
  const s = 720 % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})
</script>

<template>
  <div class="flex flex-col h-full bg-gradient-to-b from-[#3d3226] via-[#29221a] to-[#1c1814] text-white">
    <!-- Header -->
    <div class="flex justify-between items-center px-5 py-4">
      <ChevronDown class="w-6 h-6 text-white/60 cursor-pointer" />
      <div class="text-center">
        <p class="text-[10px] text-orange-400 font-bold tracking-widest uppercase">{{ store.episode.date }} · 晨间新闻</p>
        <p class="text-sm font-semibold mt-0.5">{{ store.episode.title }}</p>
        <p class="text-[10px] text-white/40 mt-0.5">🎙️ 小暖 · 小明 ｜ {{ durationStr }}</p>
      </div>
      <Ellipsis class="w-6 h-6 text-white/60 cursor-pointer" />
    </div>

    <!-- 字幕区 -->
    <SubtitleArea :episode="store.episode" :current-time="currentTime" />

    <!-- 控制区 -->
    <div class="px-6 pb-8 pt-2">
      <!-- 进度条 -->
      <div class="flex items-center gap-3 mb-2">
        <span class="text-xs text-white/50 w-9">{{ currentStr }}</span>
        <div class="flex-1 h-1 bg-white/10 rounded-full relative cursor-pointer" @click="seek(($event.offsetX / ($event.target as HTMLElement).offsetWidth) * 720)">
          <div class="h-full bg-orange-500 rounded-full transition-all" :style="{ width: progress + '%' }" />
          <div class="absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-orange-500 rounded-full shadow-lg shadow-orange-500/50" :style="{ left: progress + '%' }" />
        </div>
        <span class="text-xs text-white/50 w-9">{{ durationStr }}</span>
      </div>

      <!-- 按钮 -->
      <div class="flex justify-center items-center gap-7 mt-3">
        <button class="text-sm font-bold text-white/50 hover:text-white/80 transition-colors" @click="setSpeed(0.75)">0.75x</button>
        <button class="p-2 text-white/60 hover:text-white transition-colors" @click="skip(-15)"><SkipBack class="w-6 h-6" /></button>
        <button class="w-14 h-14 rounded-full bg-orange-500 flex items-center justify-center shadow-lg shadow-orange-500/40 hover:scale-105 transition-transform" @click="toggle">
          <Pause v-if="isPlaying" class="w-7 h-7" />
          <Play v-else class="w-7 h-7 ml-0.5" />
        </button>
        <button class="p-2 text-white/60 hover:text-white transition-colors" @click="skip(15)"><SkipForward class="w-6 h-6" /></button>
        <button class="text-sm font-bold text-white/50 hover:text-white/80 transition-colors" @click="setSpeed(1.25)">1.25x</button>
      </div>

      <!-- 底部操作 -->
      <div class="flex justify-around mt-5">
        <button class="text-xs text-white/35 hover:text-white/60 transition-colors">🎤 打断追问</button>
        <button class="text-xs text-white/35 hover:text-white/60 transition-colors">📋 章节列表</button>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 4: 创建 PodcastPage.vue**

`frontend/src/pages/PodcastPage.vue`:
```vue
<script setup lang="ts">
import PodcastPlayer from '@/components/PodcastPlayer.vue'
</script>

<template>
  <div class="h-full">
    <PodcastPlayer />
  </div>
</template>
```

- [ ] **Step 5: 验证播客页**

确认播客页显示：顶部信息栏、歌词字幕区、播放控制、进度条、播放/暂停动画。

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: add podcast page with lyrics-style player"
```

---

### Task 7: 追问页 + 追问抽屉

**Files:**
- Create: `frontend/src/components/ChatBubble.vue`
- Create: `frontend/src/components/AskDrawer.vue`
- Create: `frontend/src/pages/AskPage.vue`

- [ ] **Step 1: 创建 ChatBubble.vue**

`frontend/src/components/ChatBubble.vue`:
```vue
<script setup lang="ts">
import type { ChatMessage } from '@/types'

defineProps<{ message: ChatMessage }>()
</script>

<template>
  <div class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
    <div
      class="max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed"
      :class="message.role === 'user'
        ? 'bg-warm-500 text-white rounded-br-md'
        : 'bg-stone-100 text-stone-800 rounded-bl-md'"
    >
      <p v-if="message.role === 'assistant'" class="text-[10px] font-bold opacity-50 mb-1 tracking-wide">🤖 NewsCast AI</p>
      <p v-else class="text-[10px] font-bold opacity-50 mb-1 tracking-wide">我</p>
      <div v-html="message.content.replace(/\n/g, '<br>')" />
    </div>
  </div>
</template>
```

- [ ] **Step 2: 创建 AskDrawer.vue（移动端底部抽屉）**

`frontend/src/components/AskDrawer.vue`:
```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useAskStore } from '@/stores/ask'
import ChatBubble from './ChatBubble.vue'
import { Send, Mic } from 'lucide-vue-next'

const askStore = useAskStore()
const input = ref('')

function send() {
  if (!input.value.trim()) return
  askStore.sendMessage(input.value)
  input.value = ''
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex flex-col justify-end" @click.self="$emit('close')">
    <div class="bg-black/30 absolute inset-0" @click="$emit('close')" />
    <div class="relative bg-white rounded-t-3xl shadow-2xl max-h-[55%] flex flex-col animate-slide-up">
      <div class="flex justify-center pt-3 pb-1">
        <div class="w-9 h-1 bg-stone-300 rounded-full cursor-pointer" @click="$emit('close')" />
      </div>

      <!-- 上下文 -->
      <div v-if="askStore.currentContext" class="mx-5 mb-3 px-3 py-2 bg-orange-50 text-orange-700 text-xs rounded-lg border border-orange-100">
        📰 当前话题：{{ askStore.currentContext.title }}
      </div>

      <!-- 对话 -->
      <div class="flex-1 overflow-y-auto px-5 flex flex-col gap-2 pb-4 max-h-64">
        <ChatBubble v-for="msg in askStore.messages" :key="msg.id" :message="msg" />
        <div v-if="askStore.isTyping" class="flex gap-1.5 px-4 py-3">
          <span class="w-2 h-2 rounded-full bg-stone-300 animate-bounce" />
          <span class="w-2 h-2 rounded-full bg-stone-300 animate-bounce" style="animation-delay:0.15s" />
          <span class="w-2 h-2 rounded-full bg-stone-300 animate-bounce" style="animation-delay:0.3s" />
        </div>
      </div>

      <!-- 输入 -->
      <div class="flex items-center gap-2 px-4 py-3 border-t border-stone-100">
        <input
          v-model="input"
          type="text"
          placeholder="输入追问..."
          class="flex-1 px-4 py-2.5 bg-stone-50 border border-stone-200 rounded-full text-sm outline-none focus:border-warm-400 transition-colors"
          @keydown.enter="send"
        />
        <button class="w-10 h-10 rounded-full bg-orange-50 text-warm-500 flex items-center justify-center hover:bg-orange-100 transition-colors">
          <Mic class="w-5 h-5" />
        </button>
        <button
          class="w-10 h-10 rounded-full bg-warm-500 text-white flex items-center justify-center hover:bg-warm-600 transition-colors disabled:opacity-40"
          :disabled="!input.trim()"
          @click="send"
        >
          <Send class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes slide-up {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
.animate-slide-up { animation: slide-up 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
</style>
```

- [ ] **Step 3: 创建 AskPage.vue**

`frontend/src/pages/AskPage.vue`:
```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useAskStore } from '@/stores/ask'
import ChatBubble from '@/components/ChatBubble.vue'
import { Send, Mic } from 'lucide-vue-next'

const askStore = useAskStore()
const input = ref('')

function send() {
  if (!input.value.trim()) return
  askStore.sendMessage(input.value)
  input.value = ''
}
</script>

<template>
  <div class="flex flex-col h-full">
    <h1 class="text-2xl font-bold px-5 py-4">AI 追问</h1>

    <!-- 上下文 -->
    <div v-if="askStore.currentContext" class="mx-5 mb-3 px-3 py-2 bg-orange-50 text-orange-700 text-xs rounded-lg border border-orange-100 text-center">
      📰 当前话题：{{ askStore.currentContext.title }}
    </div>

    <!-- 对话列表 -->
    <div class="flex-1 overflow-y-auto px-5 flex flex-col gap-2 pb-4">
      <ChatBubble v-for="msg in askStore.messages" :key="msg.id" :message="msg" />
      <div v-if="askStore.isTyping" class="flex gap-1.5 px-4 py-3">
        <span class="w-2 h-2 rounded-full bg-stone-300 animate-bounce" />
        <span class="w-2 h-2 rounded-full bg-stone-300 animate-bounce" style="animation-delay:0.15s" />
        <span class="w-2 h-2 rounded-full bg-stone-300 animate-bounce" style="animation-delay:0.3s" />
      </div>
    </div>

    <!-- 输入 -->
    <div class="flex items-center gap-2 px-4 py-3 border-t border-stone-100 bg-white">
      <input
        v-model="input"
        type="text"
        placeholder="输入追问..."
        class="flex-1 px-4 py-2.5 bg-stone-50 border border-stone-200 rounded-full text-sm outline-none focus:border-warm-400 transition-colors"
        @keydown.enter="send"
      />
      <button class="w-10 h-10 rounded-full bg-orange-50 text-warm-500 flex items-center justify-center">
        <Mic class="w-5 h-5" />
      </button>
      <button
        class="w-10 h-10 rounded-full bg-warm-500 text-white flex items-center justify-center disabled:opacity-40"
        :disabled="!input.trim()"
        @click="send"
      >
        <Send class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
```

- [ ] **Step 4: 在 AppShell 中集成 AskDrawer**

修改 `AppShell.vue`，添加 AskDrawer 的显示/隐藏逻辑，监听 `toggle-ask-drawer` 事件。

```vue
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import MobileBottomTab from './MobileBottomTab.vue'
import DesktopSidebar from './DesktopSidebar.vue'
import FloatingAskButton from './FloatingAskButton.vue'
import AskDrawer from './AskDrawer.vue'

const showAskDrawer = ref(false)

function toggleDrawer() { showAskDrawer.value = !showAskDrawer.value }

onMounted(() => window.addEventListener('toggle-ask-drawer', toggleDrawer))
onUnmounted(() => window.removeEventListener('toggle-ask-drawer', toggleDrawer))
</script>

<template>
  <div class="flex h-dvh w-full overflow-hidden bg-stone-50">
    <DesktopSidebar />
    <main class="flex-1 overflow-y-auto scrollbar-hide">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <MobileBottomTab />
    <FloatingAskButton />
    <AskDrawer v-if="showAskDrawer" @close="showAskDrawer = false" />
  </div>
</template>
```

- [ ] **Step 5: 验证追问功能**

确认：输入文字发送、模拟AI回复、打字动画、FAB按钮唤起抽屉。

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat: add ask page and bottom drawer with chat interface"
```

---

### Task 8: 我的页面 — 主题切换 + 陪伴人格设置

**Files:**
- Create: `frontend/src/components/ThemeSwitcher.vue`
- Create: `frontend/src/pages/MePage.vue`

- [ ] **Step 1: 创建 ThemeSwitcher.vue**

`frontend/src/components/ThemeSwitcher.vue`:
```vue
<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>

<template>
  <div class="flex gap-3">
    <button
      v-for="t in themeStore.themes"
      :key="t.value"
      @click="themeStore.setTheme(t.value)"
      class="w-8 h-8 rounded-full border-2 transition-all"
      :class="[
        t.color,
        themeStore.current === t.value ? 'border-warm-500 shadow-[0_0_0_3px_rgba(249,115,22,0.2)]' : 'border-transparent',
      ]"
      :title="t.label"
    />
  </div>
</template>
```

- [ ] **Step 2: 创建 MePage.vue**

`frontend/src/pages/MePage.vue`:
```vue
<script setup lang="ts">
import { usePreferencesStore } from '@/stores/preferences'
import { useThemeStore } from '@/stores/theme'
import ThemeSwitcher from '@/components/ThemeSwitcher.vue'
import { ChevronRight } from 'lucide-vue-next'

const prefsStore = usePreferencesStore()
const themeStore = useThemeStore()

const personalityOptions = ['亲和温暖', '干练知性', '幽默活泼', '沉稳深度']
const voiceOptions = ['MiMo 精品女声 A', 'MiMo 精品男声 B', 'MiMo 温柔女声 C']
</script>

<template>
  <div class="pb-8">
    <h1 class="text-2xl font-bold px-5 py-4">我的</h1>

    <!-- 陪伴助手人格 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold text-stone-400 uppercase tracking-widest px-5 mb-2">🤖 陪伴助手人格</h2>
      <div class="mx-4 bg-stone-50 rounded-2xl divide-y divide-stone-100 overflow-hidden">
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">助手名称</span>
          <span class="text-sm text-stone-500">{{ prefsStore.prefs.companion.name }}</span>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">播客角色</span>
          <span class="text-sm text-stone-500">女主播 · {{ prefsStore.prefs.companion.name }}</span>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">性格风格</span>
          <select
            :value="prefsStore.prefs.companion.personality"
            @change="prefsStore.updateCompanion({ personality: ($event.target as HTMLSelectElement).value as any })"
            class="text-sm text-stone-500 bg-transparent outline-none text-right"
          >
            <option v-for="p in personalityOptions" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">语音音色</span>
          <select
            :value="prefsStore.prefs.companion.voiceId"
            @change="prefsStore.updateCompanion({ voiceId: ($event.target as HTMLSelectElement).value })"
            class="text-sm text-stone-500 bg-transparent outline-none text-right"
          >
            <option v-for="v in voiceOptions" :key="v" :value="v">{{ v }}</option>
          </select>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">语速</span>
          <select
            :value="prefsStore.prefs.companion.speed"
            @change="prefsStore.updateCompanion({ speed: parseFloat(($event.target as HTMLSelectElement).value) })"
            class="text-sm text-stone-500 bg-transparent outline-none text-right"
          >
            <option :value="0.85">稍慢 (0.85x)</option>
            <option :value="1.0">正常 (1.0x)</option>
            <option :value="1.15">稍快 (1.15x)</option>
          </select>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">称呼方式</span>
          <span class="text-sm text-stone-500">{{ prefsStore.prefs.companion.addressAs }}</span>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm text-stone-400">🎭 VTube虚拟形象</span>
          <span class="text-xs text-warm-500">后续支持</span>
        </div>
      </div>
    </section>

    <!-- 主题外观 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold text-stone-400 uppercase tracking-widest px-5 mb-2">🎨 主题外观</h2>
      <div class="mx-4 bg-stone-50 rounded-2xl divide-y divide-stone-100 overflow-hidden">
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">当前主题</span>
          <ThemeSwitcher />
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">{{ themeStore.themes.find(t => t.value === themeStore.current)?.label }}</span>
          <span class="text-sm text-warm-500">● 当前</span>
        </div>
      </div>
    </section>

    <!-- 兴趣偏好 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold text-stone-400 uppercase tracking-widest px-5 mb-2">📋 兴趣偏好</h2>
      <div class="mx-4 bg-stone-50 rounded-2xl p-4">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="tag in ['科技','财经','体育','国际','娱乐','AI','健康','创投','教育','汽车']"
            :key="tag"
            @click="prefsStore.toggleInterest(tag)"
            class="px-3 py-1.5 rounded-full text-xs border transition-all"
            :class="prefsStore.prefs.interests.includes(tag)
              ? 'bg-orange-50 border-warm-400 text-warm-600 font-semibold'
              : 'bg-white border-stone-200 text-stone-600'"
          >
            {{ tag }}
          </button>
        </div>
      </div>
    </section>

    <!-- 推送时间 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold text-stone-400 uppercase tracking-widest px-5 mb-2">⏰ 推送时间</h2>
      <div class="mx-4 bg-stone-50 rounded-2xl divide-y divide-stone-100 overflow-hidden">
        <div v-for="t in prefsStore.prefs.pushTimes" :key="t" class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">{{ t === '8:00' ? '早间' : t === '18:00' ? '晚间' : '夜间' }}</span>
          <span class="text-sm text-stone-500">{{ t }} ✓</span>
        </div>
      </div>
    </section>

    <!-- 关于 -->
    <section class="mb-4">
      <h2 class="text-[11px] font-bold text-stone-400 uppercase tracking-widest px-5 mb-2">ℹ️ 关于</h2>
      <div class="mx-4 bg-stone-50 rounded-2xl divide-y divide-stone-100 overflow-hidden">
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">版本</span>
          <span class="text-sm text-stone-500">v0.1 MVP</span>
        </div>
        <div class="flex justify-between items-center px-4 py-3.5">
          <span class="text-sm">邀请码</span>
          <span class="text-sm text-stone-500 flex items-center gap-1">**** <ChevronRight class="w-3 h-3" /></span>
        </div>
      </div>
    </section>
  </div>
</template>
```

- [ ] **Step 3: 验证我的页面**

确认：主题切换按钮点击后全局变色、兴趣标签切换、下拉选择器可交互。

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add me page with theme switcher, companion settings, and preferences"
```

---

### Task 9: 最终集成 — README + 验证全部功能

**Files:**
- Create: `README.md`
- Modify: `frontend/src/components/AppShell.vue` (确认 AskDrawer 已集成)

- [ ] **Step 1: 创建 README.md**

```markdown
# NewsCast — 个性化新闻播报

一个部署在网页端的个性化新闻播报工具，支持卡片式滑动浏览和双人对话播客两种消费模式。

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Tailwind CSS + shadcn-vue + Lucide Icons
- **后端**: Python FastAPI (Phase 2)
- **动效**: inspira-ui

## 快速开始

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173

## 项目结构

```
news-broadcast/
├── frontend/          # Vue3 前端应用
│   └── src/
│       ├── components/  # UI 组件
│       ├── pages/       # 页面
│       ├── stores/      # Pinia 状态管理
│       ├── composables/ # 组合式函数
│       ├── data/        # 模拟数据
│       └── types/       # TypeScript 类型
├── backend/           # FastAPI 后端 (Phase 2)
└── docs/              # 开发文档
```

## 功能

- 📰 Tinder式滑动浏览新闻
- 🎧 音乐播放器歌词模式的播客
- 💬 AI追问面板（底部抽屉/侧栏）
- 🎨 4套主题可切换
- 📱 移动端优先 + 桌面端多栏布局
```

- [ ] **Step 2: 完整功能验证清单**

```bash
cd /Users/richelleshi/news-broadcast/frontend && npm run dev
```

- [ ] 路由 `/news`：新闻卡片显示、进度条正确、触摸/键盘滑动
- [ ] 路由 `/podcast`：播客歌词模式、播放/暂停按钮、进度条
- [ ] 路由 `/ask`：对话气泡、输入发送、AI模拟回复
- [ ] 路由 `/me`：主题切换（点击4个主题圆点）、兴趣标签、下拉选择器
- [ ] FAB按钮：拖拽、贴边吸附、点击弹出追问抽屉
- [ ] 桌面端（宽度≥1024px）：侧栏导航显示、追问侧栏
- [ ] 移动端（宽度<768px）：底部Tab导航

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: add README and final integration"
```

---

## 自审清单

1. **Spec coverage**: ✅ PRD Phase 1 全部功能覆盖——新闻卡片、播客播放器、追问面板、用户设置、主题切换、响应式布局
2. **No placeholders**: ✅ 所有步骤都包含完整可执行代码，无 TBD/TODO
3. **Type consistency**: ✅ NewsItem, PodcastEpisode, ChatMessage, UserPreferences 等类型在 stores 和组件中一致使用

## 后续 Phase 计划

- **Phase 2**: FastAPI 后端搭建 + 新闻采集 API + DeepSeek 追问 API + MiMo TTS
- **Phase 3**: GitHub Actions 定时调度 + Vercel 部署

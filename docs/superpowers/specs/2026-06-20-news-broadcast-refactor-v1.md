# NewsCast v1 重构设计

**目标**：核心重写，修复 5 个根深问题，达到可测试状态。

## 决策

| # | 决策 | 方案 |
|---|------|------|
| 1 | 布局 | 放弃 CSS Grid，用固定定位 Tab + 普通滚动页面 |
| 2 | 新闻导航 | prev/next 按钮为主，滑动手势为辅 |
| 3 | AI 上下文 | 三级注入：原文抓取 → 搜索 API → DeepSeek |
| 4 | 数据持久化 | 后端文件存储 + localStorage 双保险 |

## 架构

- AppShell: `<main>` + 固定底部 Tab + 固定 FAB
- 每个页面自然滚动，不依赖高度传导链
- AI: `/api/ask` → 抓原文 → 组装 context → DeepSeek
- 设置: Pinia → localStorage + `/api/me/preferences` → `data/prefs/{token}.json`

## Web Search 集成

- 优先: httpx 抓取 sourceUrl 原文 → BeautifulSoup 提取正文
- 备选: Brave Search API (免费 2000/月) 或 Bing API
- 降级: 仅有标题+摘要作为上下文

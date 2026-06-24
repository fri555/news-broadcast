# NewsCast — 个性化新闻播报

个性化新闻播报工具，支持**卡片滑动浏览**和**双人对话播客**两种消费模式，AI 自然语言追问交互。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + TypeScript + Vite + Tailwind CSS + Lucide Icons |
| 后端 | Python FastAPI |
| AI | DeepSeek API |

## 快速开始

### 1. 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 配置 DeepSeek API Key（可选，不配也能用）
cp .env .env.local
# 编辑 .env.local 填入 DEEPSEEK_API_KEY

uvicorn main:app --reload --port 8000
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173

## 项目结构

```
news-broadcast/
├── frontend/                # Vue3 前端
│   └── src/
│       ├── api/            # API 层（对接后端）
│       ├── components/     # UI 组件
│       ├── composables/    # 组合式函数
│       ├── pages/          # 页面
│       ├── router/         # 路由
│       ├── stores/         # Pinia 状态
│       └── types/          # TypeScript 类型
├── backend/                # FastAPI 后端
│   ├── api/                # 路由
│   ├── main.py             # 入口
│   ├── models.py           # 数据模型
│   └── services.py         # AI 服务
└── docs/                   # 文档
```

## 功能

- 📰 **卡片新闻**：Tinder式横向滑动浏览，左右切换
- 🎧 **播客播放**：音乐播放器歌词模式，双人对话字幕
- 💬 **AI 追问**：底部抽屉式追问面板，支持文字/语音输入
- 🎨 **四套主题**：温暖陪伴 / 专业克制 / 现代极简 / 暗夜沉浸
- 📱 **响应式**：移动端底部Tab + 桌面端侧栏

## 配置 DeepSeek API

在 `backend/.env` 中设置：

```
DEEPSEEK_API_KEY=sk-your-key-here
```

未配置时 AI 追问会使用内置 fallback 回复。新闻浏览和播客功能不受影响。

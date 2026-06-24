# NewsCast VTube / Live2D 接入调研

**日期**：2026-06-23
**目标**：为 NewsCast 增加陪伴式虚拟形象，能随播客/追问说话、切表情、做轻量动作。

---

## 1. 两条路线

| 路线 | 适合场景 | 优点 | 风险 |
|------|----------|------|------|
| VTube Studio API | 用户本机安装 VTube Studio，网页/后端通过 WebSocket 控制模型 | 成熟，能控制模型、表情、热键、道具；插件无需授权费 | 依赖桌面 App，移动端不适合；用户要打开 VTube Studio 并允许 Plugin API |
| Web 内嵌 Live2D | 直接在网页里加载 Live2D 模型 | 适合移动端和 Web App，体验一体化 | 需要 Live2D 模型资源；SDK/模型许可要确认；唇形和表情要自己做 |

---

## 2. 推荐实现路径

短期：先做 **Web 内嵌 Live2D 占位层**。
- 在播客页/追问页右下角显示 Live2D 角色。
- 播放 TTS 时根据音量或播放状态做嘴型开合。
- 根据状态切表情：待机、聆听、回答、播客中。

中期：增加 **VTube Studio 桌面联动**。
- 如果用户本机开了 VTube Studio，连接 `ws://localhost:8001`。
- 获取/触发表情 hotkey。
- 在回答开始/结束时触发动作或表情。

---

## 3. 参考项目

- VTube Studio API：`DenchiSoft/VTubeStudio`
  - API 默认 WebSocket：`ws://localhost:8001`
  - 需要用户在 VTube Studio 中允许 Plugin API access
  - 支持获取/加载模型、执行 hotkey、控制模型参数、表情、道具等
- Live2D 官方 Web 示例：`Live2D/CubismWebSamples`
  - 官方 Web SDK 示例，适合严肃接入和许可合规
- `pixi-live2d-display`
  - PixiJS 插件，集成成本低，适合快速在网页中显示 Live2D 模型

---

## 4. NewsCast 集成点

| 状态 | 虚拟形象行为 |
|------|--------------|
| 新闻页待机 | 轻微呼吸/眨眼 |
| 新闻朗读 | 嘴型开合，表情“讲解” |
| 播客播放 | 主播 A/B 可切不同表情或两个角色轮流高亮 |
| 追问聆听 | 靠近/专注表情，显示正在听 |
| 回答中 | 嘴型开合，语气对应表情 |
| 错误/无网络 | 困惑或抱歉表情 |

---

## 5. 待确认

- 你之前提到的 GitHub 项目具体是哪一个。
- 是否已有 Live2D 模型文件：`.model3.json`、贴图、motions、expressions。
- 是优先移动端 Web 内嵌，还是优先桌面 VTube Studio 联动。

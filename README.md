# 游戏伴侣 (Game Companion)

一款 Windows 桌面覆盖工具，在游戏过程中提供实时鼓励、攻略搜索、弹幕互动和 AI 问答服务。

## 功能特性

- 🎮 屏幕识别 — 实时捕获屏幕，AI 视觉理解游戏内容
- 💬 自动弹幕 — 根据游戏场景自动生成风格化弹幕
- 🤖 AI 问答 — 用户打字提问，搜索教程 + AI 回答
- 🎭 人格系统 — LLM 生成/自定义角色人格，影响所有输出
- 🧠 长期记忆 — 向量 + 重排语义检索，防退化设计
- 🎨 模块化 UI — 工具栏/侧边栏/气泡/弹幕自由组合开关

## 技术栈

| 组件 | 技术 |
|------|------|
| 覆盖窗口 | Electron (transparent: true, frame: false) |
| UI | HTML + CSS + JavaScript（原生，不使用框架） |
| 屏幕截图 | Python dxcam (DXGI) |
| AI API | 用户自定义（OpenAI/Claude/DeepSeek/本地等） |
| 通信 | WebSocket (localhost, JSON 协议) |

## 项目结构

```
游戏伴侣/
├── frontend/           ← Electron 前端（源码）
├── backend/            ← Python 后端（源码）
├── docs/               ← 设计文档
├── start.bat           ← 一键启动
└── README.md
```

## 开发阶段

| 阶段 | 内容 | 状态 |
|------|------|------|
| 1 | 项目脚手架 + WebSocket 通信层 | 进行中 |
| 2 | Electron UI 核心 | 待开始 |
| 3 | 屏幕捕获 + AI 视觉分析 | 待开始 |
| 4 | 记忆系统 | 待开始 |
| 5 | 人格系统 | 待开始 |
| 6 | 弹幕引擎 | 待开始 |
| 7 | 搜索系统 | 待开始 |
| 8 | 设置系统 | 待开始 |
| 9 | 打包发布 | 待开始 |

## 设计规格

详见 `docs/superpowers/specs/2026-06-07-game-companion-design.md`

## 变更记录

- 2026-06-07：项目初始化，创建设计文档和 CLAUDE.md

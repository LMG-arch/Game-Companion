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
├── frontend/                  ← Electron 前端
│   ├── main/
│   │   ├── main.js            ← 主进程入口
│   │   └── python-manager.js  ← Python 进程管理
│   ├── renderer/
│   │   ├── index.html         ← 页面入口
│   │   ├── index.js           ← 入口 JS
│   │   └── modules/
│   │       └── web-socket.js  ← WebSocket 客户端
│   └── package.json
├── backend/                   ← Python 后端
│   ├── main.py                ← 后端入口
│   ├── core/
│   │   ├── config.py          ← 配置读取
│   │   └── websocket_server.py ← WebSocket 服务器
│   └── utils/
│       ├── logger.py          ← 日志模块
│       └── port_file.py       ← 端口发现
├── docs/                      ← 设计文档
├── start.bat                  ← 一键启动
└── README.md
```

## 开发阶段

| 阶段 | 内容 | 状态 |
|------|------|------|
| 1 | 项目脚手架 + WebSocket 通信层 | ✅ 完成 |
| 2 | Electron UI 核心 | ✅ 完成 |
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

- 2026-06-07：阶段 2 完成 — Electron UI 核心（工具栏/侧边栏/气泡/弹幕层/输入框/点击穿透/快捷键）
- 2026-06-07：阶段 1 完成 — 项目脚手架 + WebSocket 通信层，修复中文编码和点击穿透
- 2026-06-07：阶段 1 实现 — 创建后端核心模块（日志、配置、端口发现、WebSocket 服务器）和前端核心文件（主进程、Python 管理、WebSocket 客户端、页面入口）
- 2026-06-07：创建阶段 1 详细实现计划（13 个任务，含完整代码和验证步骤）
- 2026-06-07：补充设计规格（通信协议 payload、config.json 结构、人格 JSON 结构、AI 调用参数、向量/重排 API 接口、错误处理策略）；补充实现计划（各阶段子任务、验证标准、修正依赖图）
- 2026-06-07：项目初始化，创建设计文档和 CLAUDE.md

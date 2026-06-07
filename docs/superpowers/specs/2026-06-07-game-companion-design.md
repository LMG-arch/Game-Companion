# 游戏伴侣 (Game Companion) — 设计规格说明书

**版本**: v1.0
**日期**: 2026-06-07
**状态**: 设计稿

---

## 1. 概述

游戏伴侣是一款 Windows 桌面辅助工具，通过在游戏画面上叠加透明 UI，为玩家提供实时鼓励、攻略搜索、弹幕互动和 AI 问答服务。所有数据本地保存，AI 集成可自定义。

### 核心能力

| 能力 | 说明 |
|------|------|
| 🎮 屏幕识别 | 实时捕获屏幕，AI 视觉理解游戏内容 |
| 💬 自动弹幕 | 根据游戏场景自动生成风格化弹幕 |
| 🤖 AI 问答 | 用户打字提问，搜索教程+AI 回答 |
| 🎭 人格系统 | LLM 生成/自定义角色人格，影响所有输出 |
| 🧠 长期记忆 | 向量+重排语义检索，防退化设计 |
| 🎨 模块化 UI | 工具栏/侧边栏/气泡/弹幕自由组合开关 |

---

## 2. 整体架构

```
┌──────────────────────────────────────────────────────────────┐
│                      Windows 桌面                             │
│                                                              │
│  ┌────────────────────────────┐  ┌────────────────────────┐  │
│  │  Electron 覆盖窗口          │  │  Python 后端进程        │  │
│  │  ┌──────────────────────┐  │  │  ┌──────────────────┐  │  │
│  │  │ UI 组件层            │  │  │  │ 屏幕捕获(dxcam)  │  │  │
│  │  │ 工具栏/侧边栏/气泡   │  │  │  ├──────────────────┤  │  │
│  │  │ 弹幕层/输入框/设置   │  │  │  │ AI引擎(自定义)   │  │  │
│  │  └──────────────────────┘  │  │  ├──────────────────┤  │  │
│  │  ┌──────────────────────┐  │  │  │ 记忆系统(向量)   │  │  │
│  │  │ 弹幕引擎/点击穿透    │  │  │  ├──────────────────┤  │  │
│  │  │ WebSocket 通信       │  │  │  │ 人格系统/搜索    │  │  │
│  │  └──────────────────────┘  │  │  └──────────────────┘  │  │
│  └──────────┬─────────────────┘  └─────────┬──────────────┘  │
│             │ Electron 主进程管理 Python 子进程               │
│             │ WebSocket (localhost)                           │
│             │ 端口发现: Python 写入端口号到临时文件            │
│             ▼                                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  配置存储: %APPDATA%/游戏伴侣/config.json              │    │
│  │  记忆存储: %APPDATA%/游戏伴侣/memory/                  │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### 技术栈

| 组件 | 技术 |
|------|------|
| 覆盖窗口 | Electron (transparent: true, frame: false) |
| UI | HTML + CSS + JavaScript (原生，不引入框架) |
| 屏幕截图 | Python dxcam (DXGI) |
| AI API | 用户自定义 (OpenAI/Claude/DeepSeek/本地等) |
| 向量检索 | 远程 API (用户配置)，无配置时降级关键词 |
| 重排模型 | 远程 API (用户配置)，无配置时跳过 |
| 通信 | WebSocket (localhost, JSON 协议) |
| 搜索 | 用户配置的搜索引擎 (Google/Bing/SearXNG等) |

### 进程管理

Electron 主进程负责启动和终止 Python 子进程。启动流程:

1. 用户双击 `start.bat` 或 Electron exe
2. Electron 主进程启动 Python 子进程 (child_process.spawn)
3. Python 启动 WebSocket 服务器，将端口号写入临时文件 `%TEMP%/game-companion-port.txt`
4. Electron 读取端口号，建立 WebSocket 连接
5. 连接成功后，Python 开始截图循环，UI 展示就绪状态
6. Electron 关闭时，先发关闭消息，再 kill Python 子进程

---

## 3. UI 布局与交互

### 3.1 四模块自由组合

```
┌─ 进度:45% ── 🔍搜索 ────── ⚙️ ─┐  ← ① 顶部工具栏
│                                   │
│    🎉"太强了！" (弹幕→→→)         │  ← ② 弹幕层
│                                   │
│    🎮 游戏画面                    │
│                                   │
│                      ┌────┤       │  ← ③ 右侧侧边栏
│                      │ 💬 │       │
│                      │ 📖 │       │
│                      │    │       │
│           ┌────┐     │    │       │
│           │🤖  │     │    │       │  ← ④ 浮动气泡
│           │加油│     └────┘       │
│           └────┘                  │
└──────────────────────────────────┘
```

每个模块可在设置面板中**独立开关**。

### 3.2 点击穿透策略

| 模式 | 触发条件 | 交互区域 | 穿透区域 |
|------|---------|---------|---------|
| 🟢 全穿透 | 默认状态 | 无 | 整个窗口 → 游戏 |
| 🟡 输入模式 | 快捷键呼出输入框 | 输入框 (键盘) | 其余全部区域 |
| 🔵 设置模式 | 打开设置面板 | 整个面板 | 面板外区域 |
| 🟣 气泡交互 | 悬停/点击气泡 | 气泡区域 | 其余全部区域 |

全屏独占模式 (Fullscreen Exclusive) 处理: Electron 窗口设置为 `alwaysOnTop` + 无边框 + 全屏尺寸覆盖，在绝大多数 DX11/DX12/Vulkan 游戏上可正常渲染。

### 3.3 快捷键

| 快捷键 | 功能 | 默认值 |
|--------|------|--------|
| `Ctrl+Shift+Space` | 呼出/隐藏输入框 | 可配置 |
| `Ctrl+Shift+H` | 隐藏/显示所有UI | 可配置 |
| `Ctrl+Shift+S` | 打开设置 | 可配置 |
| `Ctrl+Shift+D` | 弹幕开关 | 可配置 |

---

## 4. 设置系统

所有设置在 Electron 设置面板中可视化配置，数据存储在 `%APPDATA%/游戏伴侣/config.json`，修改即时生效，WebSocket 推送通知 Python 后端热加载。

### 配置分类

**通用**: 开机自启、快捷键绑定、语言、模块开关(4个独立开关)

**界面**: 透明度(滑块0-100%)、弹幕速度/密度/字体/颜色、侧边栏宽度、主题(深色/浅色)

**AI**:
- AI Provider: OpenAI / Claude / DeepSeek / 自定义
- API 地址、API Key、模型名 (均在 UI 中配置)
- 系统提示词 (可编辑文本框)

**游戏**: 截图频率(秒/帧)、识别区域(全屏/窗口)

**弹幕**: 自动弹幕开关、鼓励频率、风格(战术分析/陪伴聊天/教程/自动匹配)、屏蔽关键词

**搜索**: 搜索引擎(Google/Bing/SearXNG/自定义)、搜索 API 地址、代理设置

**记忆**:
- 向量模型: API 地址 + Key + 模型名 (无配置则降级关键词检索)
- 重排模型: API 地址 + Key (无配置则跳过)
- 检索参数: Top K(默认20)、Top N(默认8)
- 混合权重: 语义/时间 滑块
- 测试检索功能、记忆健康度面板、记忆清除/导出/导入
- "立即体检"按钮

**角色人格**: (见第6节)

**关于**: 导出/导入全部配置

### config.json 完整结构

```json
{
  "general": {
    "auto_launch": false,
    "language": "zh-CN",
    "modules": {
      "toolbar": true,
      "sidebar": true,
      "bubble": true,
      "danmaku": true
    },
    "shortcuts": {
      "toggle_input": "Ctrl+Shift+Space",
      "toggle_ui": "Ctrl+Shift+H",
      "open_settings": "Ctrl+Shift+S",
      "toggle_danmaku": "Ctrl+Shift+D"
    }
  },
  "ui": {
    "opacity": 90,
    "theme": "dark",
    "sidebar_width": 300,
    "danmaku": {
      "speed": 5,
      "density": 5,
      "font_size": 16,
      "color": "#FFFFFF",
      "font_family": "Microsoft YaHei"
    }
  },
  "ai": {
    "provider": "openai",
    "api_url": "https://api.openai.com/v1",
    "api_key": "",
    "model": "gpt-4o",
    "system_prompt": "你是一个游戏伴侣...",
    "temperature": 0.7,
    "max_tokens": 500,
    "timeout": 30,
    "retry_count": 2,
    "fallback_provider": null
  },
  "game": {
    "capture_fps": 1,
    "silent_fps": 0.2,
    "silent_threshold": 5,
    "capture_region": "fullscreen"
  },
  "danmaku": {
    "auto_enabled": true,
    "encouragement_interval": 30,
    "style": "auto",
    "blocked_keywords": []
  },
  "search": {
    "engine": "google",
    "api_url": "",
    "api_key": "",
    "proxy": null
  },
  "memory": {
    "vector": {
      "api_url": "",
      "api_key": "",
      "model": ""
    },
    "reranker": {
      "api_url": "",
      "api_key": ""
    },
    "top_k": 20,
    "top_n": 8,
    "semantic_weight": 0.7,
    "time_weight": 0.3
  },
  "personality": {
    "active": "preset_soft"
  }
}
```

---

## 5. 通信协议

WebSocket (localhost) 连接。Electron 通过读取 Python 写入的端口文件建立连接，连接断开时自动重连。

### 消息格式

```json
{
  "type": "消息类型",
  "id": "uuid",
  "payload": { ... }
}
```

### 核心消息类型及 Payload

#### 🖥️→🐍 `ping` 心跳
```json
{ "type": "ping", "id": "uuid", "payload": {} }
```
回复：`{ "type": "pong", "id": "同一uuid", "payload": {} }`

#### 🖥️→🐍 `screen.capture` 请求截图分析
```json
{
  "type": "screen.capture",
  "id": "uuid",
  "payload": {}
}
```

#### 🐍→🖥️ `screen.analyzed` 场景识别结果
```json
{
  "type": "screen.analyzed",
  "id": "uuid",
  "payload": {
    "scene": "combat | exploration | menu | stuck | death | idle",
    "confidence": 0.85,
    "description": "玩家正在与 BOSS 战斗，血量剩余 30%",
    "suggestion": "建议使用回复药水",
    "danmaku_hint": "加油！你可以的！"
  }
}
```

#### 🐍→🖥️ `danmaku.send` 弹幕发送
```json
{
  "type": "danmaku.send",
  "id": "uuid",
  "payload": {
    "text": "太强了！",
    "priority": "high | normal | low",
    "style": "encouragement | tutorial | comment"
  }
}
```

#### 🖥️→🐍 `question.ask` 用户提问
```json
{
  "type": "question.ask",
  "id": "uuid",
  "payload": {
    "text": "这只 BOSS 怎么打？",
    "context": "可选，当前游戏场景描述"
  }
}
```

#### 🐍→🖥️ `question.answer` AI 回答
```json
{
  "type": "question.answer",
  "id": "uuid",
  "payload": {
    "answer": "这只 BOSS 弱雷属性，建议...",
    "sources": [
      { "title": "攻略标题", "url": "https://..." }
    ],
    "confidence": 0.9
  }
}
```

#### 🐍→🖥️ `memory.query_result` 记忆检索结果
```json
{
  "type": "memory.query_result",
  "id": "uuid",
  "payload": {
    "query": "玩家偏好",
    "results": [
      {
        "text": "玩家偏好使用弓箭武器",
        "importance": 0.8,
        "created_at": "2026-06-01T14:30:00"
      }
    ],
    "total": 5,
    "mode": "vector | keyword | empty"
  }
}
```

#### 🖥️→🐍 `settings.updated` 配置变更
```json
{
  "type": "settings.updated",
  "id": "uuid",
  "payload": {
    "section": "ai | game | danmaku | search | memory | personality",
    "changes": {
      "ai.provider": "openai",
      "ai.model": "gpt-4o"
    }
  }
}
```

#### 🐍→🖥️ `ai.status` AI 服务状态
```json
{
  "type": "ai.status",
  "id": "uuid",
  "payload": {
    "provider": "openai",
    "status": "online | offline | error",
    "message": "API key 无效"
  }
}
```

#### 🖥️→🐍 `shutdown` 关闭通知
```json
{ "type": "shutdown", "id": "uuid", "payload": {} }
```

#### 🖥️→🐍 `memory.test` 记忆检索测试
```json
{
  "type": "memory.test",
  "id": "uuid",
  "payload": {
    "query": "测试查询内容"
  }
}
```
回复：`memory.query_result`

#### 🐍→🖥️ `error` 错误通知
```json
{
  "type": "error",
  "id": "uuid",
  "payload": {
    "code": "AI_TIMEOUT | SCREEN_CAPTURE_FAILED | MEMORY_ERROR",
    "message": "AI 请求超时",
    "recoverable": true
  }
}
```

---

## 6. 角色人格系统

### 6.1 预设人格

内置 6 套人格模板:

| 人格 | 性格 | 说话风格 | 适合场景 |
|------|------|---------|---------|
| 🥰 软萌甜心 | 温柔、可爱、爱鼓励 | "加油的说~""太棒了！🥰" | 放松向游戏 |
| 🔥 热血战友 | 激动、燃、好胜 | "上啊！干翻它！" | 竞技/动作游戏 |
| 😏 毒舌吐槽 | 犀利、幽默、口是心非 | "这都能死？……还行吧" | 熟手玩家 |
| 📚 智慧导师 | 沉稳、博学、耐心 | "BOSS弱雷，建议带雷元素武器" | 需要攻略时 |
| 😴 慵懒猫娘 | 懒散、偶尔认真、治愈 | "嗯~打得好就夸夸你喵~" | 休闲陪伴 |
| 🤖 AI酱 | 中性、高效、专业 | "检测到您正在挑战第3关" | 效率向 |

### 6.2 LLM 人格生成

用户输入关键词/描述 → LLM 生成完整人格设定:

- 姓名、称号
- 性格维度数值 (傲娇度/温柔度/毒舌度等)
- 口癖列表
- 背景故事 (2-3 句)
- 弹幕示例 (5-8 条)
- 系统提示词 (自动生成，可直接用于 AI 调用)

生成结果保存为独立 JSON 文件，可在人格编辑器中微调。

### 6.3 人格编辑器界面

- 头像 (AI 生成图片)
- 姓名、称号 (文本框)
- 性格维度拖拽滑块 (5 组: 温柔←→傲娇、幽默←→严肃、毒舌←→温柔、活泼←→沉稳、话多←→话少)
- 口癖管理 (标签式添加/删除)
- 系统提示词 (可编辑文本框)
- 操作: 保存 / 另存为新人格 / 恢复默认 / 删除

### 6.4 人格数据

本地 `%APPDATA%/游戏伴侣/personalities/` 目录下 JSON 文件存储。
每次 AI 调用时将活跃人格的 system prompt 注入到消息中。
切换人格后所有后续输出即时生效。

### 6.5 人格 JSON 完整结构

```json
{
  "id": "preset_soft",
  "name": "软萌甜心",
  "title": "你的专属啦啦队",
  "avatar": null,
  "dimensions": {
    "gentle_tsundere": 0.9,
    "humor_serious": 0.7,
    "snark_kind": 0.2,
    "active_calm": 0.8,
    "talkative_quiet": 0.7
  },
  "catchphrases": ["的说~", "太棒了！", "加油哦~", "好厉害！"],
  "background": "一个温柔可爱的虚拟伙伴，总是默默支持着玩家。",
  "danmaku_examples": [
    "加油的说~",
    "太棒了！🥰",
    "你一定可以的！",
    "好厉害的操作！",
    "慢慢来，不着急~",
    "相信自己！",
    "胜利就在眼前！"
  ],
  "system_prompt": "你是「软萌甜心」，一个温柔可爱的游戏伴侣。你说话带「的说~」口癖，总是积极鼓励玩家，用可爱的表情和语气表达支持。即使玩家失败了也要温柔安慰。",
  "is_preset": true
}
```

---

---

## 7. 记忆系统（防退化设计）

### 7.1 核心原则

> 宁可少记，不要记错；宁可漏召，不要乱召。

### 7.2 记忆写入

**三关筛选**:

1. **价值评估** — LLM 判断信息是否有长期价值。无价值直接丢弃。判断标准: 玩家偏好/能力变化/卡关事件/重要成就。
2. **去重检测** — 与已有记忆对比。重复则合并(更新时间和权重)，矛盾则标记旧记忆为"待验证"并写入新记忆。
3. **结构化存储** — 写入向量库 + SQLite 原文存储。

### 7.3 记忆结构

```json
{
  "id": "mem_001a2b3c",
  "text": "玩家在只狼·狮子猿处卡关3天，尝试了10+次",
  "type": "game_stuck",
  "game": "只狼",
  "importance": 0.85,
  "confidence": 0.9,
  "created_at": "2026-06-01T14:30:00",
  "last_accessed": "2026-06-05T20:00:00",
  "access_count": 5,
  "expire_at": "2026-08-01T14:30:00",
  "verified": true,
  "tags": ["只狼", "狮子猿", "卡关"]
}
```

### 7.4 记忆召回 (三阶段)

| 阶段 | 操作 | 说明 |
|------|------|------|
| ① 多路召回 | 向量检索(Top 30) + 关键词(Top 10) + 时间优先(Top 10) | 合并去重得 ~40 条 |
| ② 重排过滤 | Cross-Encoder 打分，过滤低分(<0.3)和不相关记忆 | 取 Top 8-12 |
| ③ 适配注入 | 矛盾检查、过时标记、去重 | 最终 5-8 条注入 prompt |

### 7.5 自动维护 (每天/启动时执行)

1. **过期清理**: expire_at 已过的归档/删除
2. **矛盾检测**: 发现矛盾记忆，保高置信度，标记另一条待验证
3. **冗余合并**: 同内容的多条记忆合并为一条
4. **低频衰减**: 3个月未访问 → 降低重要性；6个月未访问 → 归档(不删除，不参与召回)
5. **向量索引重建**: 批量删除后触发
6. **记忆摘要生成**: 用 50 字以内概括对玩家的了解，作为兜底

### 7.6 兜底方案

- 检索 ≥ 3 条 → 正常返回 Top 8
- 检索 < 3 条 → 使用记忆摘要兜底
- 检索 0 条 → 空上下文，AI 只靠人格和当前画面工作
- **绝不注入虚假记忆或模糊内容**

### 7.7 用户可见

设置面板中: 记忆健康度(百分比)、总条数/活跃/归档/待验证/矛盾数、"测试检索"功能、"立即体检"按钮。

### 7.8 向量检索 API 接口

用户配置远程向量 API，接口格式兼容 OpenAI Embeddings：

**请求**:
```
POST {api_url}/embeddings
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "input": "查询文本",
  "model": "text-embedding-3-small"
}
```

**响应**:
```json
{
  "data": [
    {
      "embedding": [0.1, 0.2, ...],
      "index": 0
    }
  ]
}
```

向量存储使用本地 SQLite + numpy 数组，检索时计算余弦相似度。

### 7.9 重排模型 API 接口

用户配置远程重排 API，接口格式：

**请求**:
```
POST {api_url}/rerank
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "query": "查询文本",
  "documents": ["记忆1文本", "记忆2文本", ...],
  "top_n": 8
}
```

**响应**:
```json
{
  "results": [
    {
      "index": 0,
      "relevance_score": 0.95,
      "document": "记忆1文本"
    }
  ]
}
```

无配置时跳过重排，直接使用向量检索结果。

---

## 8. Python 后端模块

```
backend/
├── main.py                    ← WebSocket 服务器入口 + 启动截图循环
├── requirements.txt           ← 依赖列表
├── core/
│   ├── config.py              ← 读取 config.json，热加载
│   ├── websocket_server.py    ← WebSocket 通信层 (asyncio)
│   └── lifecycle.py           ← 生命周期管理 (启动/关闭/重启)
├── screen/
│   └── capturer.py            ← dxcam 截图 + 变化检测
├── ai/
│   ├── engine.py              ← AI 调用统一入口 (带重试/切换)
│   ├── providers/
│   │   ├── openai_compat.py   ← OpenAI 格式兼容 (含自定义 API)
│   │   ├── claude.py          ← Anthropic Claude
│   │   └── custom.py          ← 完全自定义格式 (用户提供完整请求体模板)
│   ├── vision.py              ← 视觉理解 (截图→文本描述)
│   └── prompt.py              ← 人格/记忆/场景模板管理
├── memory/
│   ├── manager.py             ← 记忆管理器 (写入/召回/维护)
│   ├── vector_store.py        ← 向量检索 (远程 API，无配置降级关键词)
│   ├── reranker.py            ← 重排 (远程 API，无配置跳过)
│   └── extractor.py           ← LLM 记忆提取 + 价值评估
├── search/
│   ├── engine.py              ← 搜索统一入口
│   └── providers/
│       ├── google.py          ← Google Search API
│       ├── bing.py            ← Bing Search API
│       └── searxng.py         ← SearXNG (自托管搜索引擎)
├── personality/
│   ├── manager.py             ← 人格加载/切换
│   ├── presets.py             ← 6 套内置预设人格
│   └── generator.py           ← LLM 人格生成
└── utils/
    ├── logger.py              ← 日志模块
    └── port_file.py           ← 端口号写入临时文件
```

### 启动流程

```
Python main.py 启动
  ↓
读取 config.json
  ↓
初始化 AI 引擎 (按配置加载 Provider，失败则标记不可用)
  ↓
初始化记忆管理器 (测试向量 API 可用性 → 可用/降级模式)
  ↓
初始化人格系统 (加载活跃人格)
  ↓
启动 WebSocket 服务器 (随机端口)
  ↓
将端口号写入 %TEMP%/game-companion-port.txt
  ↓
启动屏幕捕获循环 (按配置频率截图 → 变化检测 → AI 分析)
  ↓
等待 WebSocket 消息 + 异步执行分析循环
```

### 智能降级链路

| 组件 | 链路 | 最终兜底 |
|------|------|---------|
| 记忆 | 向量+重排 → 仅向量 → 关键词+时间 | 空上下文 |
| AI | 主Provider → 备用Provider → 无 | 标记离线, 截图继续 |
| 搜索 | 配置的引擎 → 无搜索 | AI 仅凭知识回答 |

### AI 调用参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| temperature | 0.7 | 创造性，弹幕生成可调高到 0.9 |
| max_tokens | 500 | 单次回复最大长度 |
| timeout | 30s | 单次请求超时 |
| retry_count | 2 | 失败重试次数 |
| retry_delay | 1s → 2s → 4s | 指数退避 |

**Provider 切换策略**:
- 连续 3 次失败 → 标记当前 Provider 离线
- 切换到 fallback_provider（如配置）
- 所有 Provider 离线 → 标记 AI 不可用，截图循环继续
- 每 60 秒尝试重新连接离线的 Provider

### 错误处理策略

| 场景 | 处理方式 |
|------|---------|
| WebSocket 断连 | 前端每 3 秒重连，指数退避（3s → 6s → 12s → 最大 30s） |
| AI 请求超时 | 重试 2 次，仍失败则切换 Provider |
| AI 返回格式错误 | 记录日志，丢弃该次结果，不展示给用户 |
| 截图失败 | 记录日志，等待下一帧，连续 10 次失败则暂停 5 秒 |
| 向量 API 不可用 | 降级到关键词检索 |
| 重排 API 不可用 | 跳过重排，直接使用向量结果 |
| 搜索引擎不可用 | AI 仅凭知识回答 |
| config.json 读取失败 | 使用默认配置，创建新的 config.json |
| Python 进程崩溃 | Electron 检测到进程退出，提示用户重启 |
| 端口文件不存在 | Electron 每秒轮询，最多等待 30 秒 |

---

## 9. Electron 前端模块

```
frontend/
├── main/
│   ├── main.js                ← 入口: 透明窗口、快捷键、Python 进程管理
│   ├── window.js              ← 窗口管理 (transparent/frame/alwaysOnTop)
│   ├── ipc.js                 ← IPC 通信
│   ├── shortcuts.js           ← 全局快捷键注册
│   └── auto-launch.js         ← 开机自启 (写入注册表)
├── renderer/
│   ├── index.html             ← 入口
│   ├── index.js               ← 入口 JS (WebSocket 连接初始化)
│   ├── styles/
│   │   ├── global.css         ← 全局样式 / CSS 变量
│   │   ├── theme.css          ← 深色/浅色主题变量
│   │   └── danmaku.css        ← 弹幕关键帧动画
│   ├── components/
│   │   ├── TopBar.js          ← 顶部工具栏
│   │   ├── SidePanel.js       ← 右侧面板 (问答结果显示)
│   │   ├── Bubble.js          ← 浮动气泡 (可折叠)
│   │   ├── DanmakuLayer.js    ← 弹幕层 (轨道管理)
│   │   ├── ChatInput.js       ← 输入框 (快捷键呼出)
│   │   └── SettingsPanel.js   ← 设置面板 (所有配置项)
│   ├── modules/
│   │   ├── danmaku-engine.js  ← 弹幕队列 + CSS 动画调度
│   │   ├── web-socket.js      ← WebSocket 客户端 (自动重连)
│   │   └── click-through.js   ← 点击穿透模式管理
│   └── utils/
└── package.json
      依赖: electron, electron-builder
```

### UI 层级 (z-index 从低到高)

| 层级 | 组件 | 交互 |
|------|------|------|
| 1 | 透明背景 | pointer-events: none |
| 2 | 弹幕层 | pointer-events: none |
| 3 | 底部信息栏 | pointer-events: none |
| 4 | 浮动气泡 | 默认穿透, hover 后可交互 |
| 5 | 右侧面板 | 默认穿透, hover 后可交互 |
| 6 | 输入框 | 仅呼出时可见 + 可交互 |
| 7 | 设置面板 | 完全可交互 (打开时其他层自动变为可交互) |

---

## 10. 弹幕引擎

- **动画方式**: CSS `@keyframes` + `animation` (从右向左平移)，不占用主线程
- **轨道系统**: 上/中/下三轨道，新弹幕自动分配到负载最少的轨道，避免重叠
- **密度控制**: 可配置每秒最大弹幕数，超出部分排队等待
- **优先级队列**: 教程内容 > 鼓励内容 > 吐槽内容，高优先级插队
- **队列上限**: 最多缓存 50 条未展示弹幕，超出丢弃最早的低优先级弹幕
- **穿透保证**: `pointer-events: none` 确保所有弹幕事件穿透到游戏

---

## 11. 屏幕捕获

- **截图引擎**: dxcam (基于 DXGI)，单帧约 1ms
- **变化检测**: 计算帧哈希，与上一帧对比。无变化则跳过分析
- **截图频率**: 默认每秒 1 帧 (全速) / 每秒 0.2 帧 (静默)，设置面板可配置
- **静默优化**: 连续 5 帧无变化 → 自动降低到每 5 秒 1 帧；检测到变化立即恢复全速
- **分析管道**:

```
截图 → 视觉理解(LLM) → 场景判断(战斗/探索/菜单/卡关/死亡)
→ 检索相关记忆 → 人格化生成回应 → 弹幕/侧边栏内容
```

---

## 12. 数据存储

```
%APPDATA%/游戏伴侣/
├── config.json              ← 全部配置 (JSON, 热加载)
├── personalities/           ← 人格设定文件
│   ├── preset_soft.json     ← 预设人格: 软萌甜心
│   ├── preset_fighter.json  ← 预设人格: 热血战友
│   ├── ...                  ← 其余预设
│   └── custom_*.json        ← 用户自定义人格
├── memory/
│   └── raw_memory.db        ← 记忆原始数据 SQLite
├── screenshots/             ← 截图缓存 (最多保留最近 100 张, 自动清理)
├── search_cache.db          ← 搜索缓存 (TTL 24 小时)
├── logs/                    ← 运行日志 (自动轮转, 保留 7 天)
└── danmaku_history.db       ← 弹幕历史 (保留最近 1000 条)
```

所有数据**纯本地存储**，用户可在设置面板中一键清除/导出/导入。

---

## 13. 项目文件结构

```
D:\ai\游戏伴侣/
├── frontend/           ← Electron 前端 (源码)
├── backend/            ← Python 后端 (源码)
├── docs/               ← 文档
│   └── superpowers/
│       └── specs/
│           └── 2026-06-07-game-companion-design.md
├── start.bat           ← 一键启动 (Electron main.js 将自动启动 Python)
├── README.md           ← 使用说明 + 配置指南
└── layouts-comparison.html
```

---

## 14. 非功能性需求

- 覆盖层性能开销 < 5% CPU (游戏模式下)
- 弹幕使用 CSS 动画，不占用主线程，不造成帧率影响
- 点击穿透在任何模式下不误拦截游戏操作
- 记忆系统无需网络也能正常工作 (降级为关键词检索)
- AI 服务离线时，截图循环和弹幕基础功能继续运行
- Electron 关闭时正确终止 Python 子进程，无残留进程
- 支持 Windows 10/11 x64

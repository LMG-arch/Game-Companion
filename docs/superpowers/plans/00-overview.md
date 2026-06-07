# 游戏伴侣 — 实现计划总览

> 本项目拆分为 9 个独立子计划，每个子计划产出可独立验证的软件。按顺序执行。

---

## 子计划列表

| # | 名称 | 依赖 | 产出 |
|---|------|------|------|
| 1 | 项目基础架构 + 通信层 | 无 | Electron + Python 骨架，WebSocket 通信连通 |
| 2 | Electron 前端 UI 核心 | #1 | 透明覆盖窗口 + 4 模块 UI 骨架 + 点击穿透 |
| 3 | 屏幕捕获 + AI 视觉分析 | #1 | Python 截图循环 + AI 视觉理解 + 分析管道 |
| 4 | 记忆系统 | #1 | 记忆写入/召回/维护/降级/向量+重排 |
| 5 | 人格系统 | #1 | 预设人格 + LLM 生成 + 编辑器 |
| 6 | 弹幕引擎 | #2, #3 | 自动弹幕生成 + 前端弹幕动画 |
| 7 | 搜索系统 | #1 | 多引擎网页搜索 + 结果返回 |
| 8 | 设置系统 | #2, #3, #4, #5, #6, #7 | 完整设置面板 + 配置持久化 |
| 9 | 打包发布 | #8 | 一键安装包 + 自动更新 |

---

## 执行顺序图

```
#1 基础架构 ──┬── #2 UI核心 ──────────┬── #6 弹幕引擎
              │                       │
              ├── #3 截图+AI ─────────┤
              │                       │
              ├── #4 记忆系统 ────────┤
              │                       │
              ├── #5 人格系统 ────────┤
              │                       │
              └── #7 搜索系统 ────────┘
                                        │
                                        ▼
                                   #8 设置系统
                                        │
                                        ▼
                                   #9 打包发布
```

---

## 阶段 1：项目基础架构 + 通信层

### 目标
建立 Electron + Python 双进程架构，实现 WebSocket 通信连通。

### 子任务

| # | 任务 | 产出文件 |
|---|------|---------|
| 1.1 | 创建项目目录结构 | `frontend/`, `backend/` 目录 |
| 1.2 | Python 后端：WebSocket 服务器 | `backend/main.py`, `backend/core/websocket_server.py` |
| 1.3 | Python 后端：端口发现机制 | `backend/utils/port_file.py` |
| 1.4 | Python 后端：配置读取（基础） | `backend/core/config.py` |
| 1.5 | Python 后端：requirements.txt | `backend/requirements.txt` |
| 1.6 | Electron 前端：主进程 + 透明窗口 | `frontend/main/main.js`, `frontend/package.json` |
| 1.7 | Electron 前端：Python 进程管理 | `frontend/main/python-manager.js` |
| 1.8 | Electron 前端：WebSocket 客户端 | `frontend/renderer/modules/web-socket.js` |
| 1.9 | Electron 前端：基础页面 | `frontend/renderer/index.html`, `frontend/renderer/index.js` |
| 1.10 | 启动脚本 | `start.bat` |
| 1.11 | 通信协议测试：收发 echo 消息 | 验证双向通信 |

### 验证标准

- [ ] `start.bat` 一键启动 Electron + Python
- [ ] Electron 窗口透明显示，不遮挡桌面
- [ ] Python WebSocket 服务器启动成功，端口写入临时文件
- [ ] Electron 读取端口文件，成功连接 Python
- [ ] 前端发送 `ping`，后端回复 `pong`，前端显示回复
- [ ] 关闭 Electron 窗口，Python 进程正确退出，无残留

---

## 阶段 2：Electron 前端 UI 核心

### 目标
实现透明覆盖窗口 + 4 模块 UI 骨架 + 点击穿透。

### 子任务

| # | 任务 | 产出文件 |
|---|------|---------|
| 2.1 | 全局样式 + CSS 变量 | `frontend/renderer/styles/global.css` |
| 2.2 | 主题系统（深色/浅色） | `frontend/renderer/styles/theme.css` |
| 2.3 | 顶部工具栏组件 | `frontend/renderer/components/TopBar.js` |
| 2.4 | 右侧侧边栏组件 | `frontend/renderer/components/SidePanel.js` |
| 2.5 | 浮动气泡组件 | `frontend/renderer/components/Bubble.js` |
| 2.6 | 弹幕层组件（空壳） | `frontend/renderer/components/DanmakuLayer.js` |
| 2.7 | 输入框组件 | `frontend/renderer/components/ChatInput.js` |
| 2.8 | 点击穿透模块 | `frontend/renderer/modules/click-through.js` |
| 2.9 | 全局快捷键注册 | `frontend/main/shortcuts.js` |
| 2.10 | IPC 通信层 | `frontend/main/ipc.js` |

### 验证标准

- [ ] 4 个模块（工具栏/侧边栏/气泡/弹幕层）独立显示
- [ ] 默认全穿透模式：鼠标点击穿透到桌面
- [ ] `Ctrl+Shift+Space` 呼出输入框，其余区域穿透
- [ ] `Ctrl+Shift+S` 打开设置面板（占位）
- [ ] `Ctrl+Shift+H` 隐藏/显示所有 UI
- [ ] 悬停气泡时气泡可交互，移开后恢复穿透

---

## 阶段 3：屏幕捕获 + AI 视觉分析

### 目标
Python 截图循环 + AI 视觉理解 + 分析管道。

### 子任务

| # | 任务 | 产出文件 |
|---|------|---------|
| 3.1 | dxcam 截图模块 | `backend/screen/capturer.py` |
| 3.2 | 帧哈希变化检测 | `backend/screen/capturer.py` |
| 3.3 | 静默降频逻辑 | `backend/screen/capturer.py` |
| 3.4 | AI 引擎统一入口 | `backend/ai/engine.py` |
| 3.5 | OpenAI 兼容 Provider | `backend/ai/providers/openai_compat.py` |
| 3.6 | Claude Provider | `backend/ai/providers/claude.py` |
| 3.7 | 自定义 Provider | `backend/ai/providers/custom.py` |
| 3.8 | 视觉理解模块 | `backend/ai/vision.py` |
| 3.9 | 场景判断逻辑 | `backend/ai/vision.py` |
| 3.10 | 分析管道：截图→视觉→场景→消息 | `backend/main.py` |
| 3.11 | 前端接收分析结果并显示 | `frontend/renderer/index.js` |

### 验证标准

- [ ] 截图循环启动，每秒 1 帧
- [ ] 帧哈希检测：静止画面自动降频，变化时恢复
- [ ] 截图发送到 AI API，返回场景描述
- [ ] 前端侧边栏显示 AI 分析结果
- [ ] AI Provider 不可用时，标记离线，截图继续
- [ ] 切换 Provider（配置变更）后热加载生效

---

## 阶段 4：记忆系统

### 目标
记忆写入/召回/维护/降级/向量+重排。

### 子任务

| # | 任务 | 产出文件 |
|---|------|---------|
| 4.1 | SQLite 存储层 | `backend/memory/store.py` |
| 4.2 | 向量检索模块 | `backend/memory/vector_store.py` |
| 4.3 | 重排模块 | `backend/memory/reranker.py` |
| 4.4 | 记忆写入（三关筛选） | `backend/memory/manager.py` |
| 4.5 | 记忆召回（三阶段） | `backend/memory/manager.py` |
| 4.6 | LLM 记忆提取 + 价值评估 | `backend/memory/extractor.py` |
| 4.7 | 自动维护（过期/矛盾/冗余/衰减） | `backend/memory/manager.py` |
| 4.8 | 降级链路：向量→关键词→空上下文 | `backend/memory/manager.py` |
| 4.9 | 记忆摘要生成 | `backend/memory/manager.py` |
| 4.10 | 前端记忆健康度显示（设置面板中） | 见阶段 8 |

### 验证标准

- [ ] 记忆写入 SQLite，字段完整
- [ ] 向量检索可用时，返回相关记忆
- [ ] 向量检索不可用时，降级到关键词检索
- [ ] 重排可用时，结果按相关性排序
- [ ] 重排不可用时，跳过重排直接返回
- [ ] 矛盾记忆检测：标记旧记忆为"待验证"
- [ ] 低频衰减：3 个月未访问降低重要性
- [ ] 记忆摘要兜底：检索 0 条时使用摘要

---

## 阶段 5：人格系统

### 目标
预设人格 + LLM 生成 + 编辑器。

### 子任务

| # | 任务 | 产出文件 |
|---|------|---------|
| 5.1 | 人格 JSON 结构定义 | `backend/personality/schema.py` |
| 5.2 | 6 套预设人格数据 | `backend/personality/presets.py` |
| 5.3 | 人格加载/切换管理器 | `backend/personality/manager.py` |
| 5.4 | LLM 人格生成 | `backend/personality/generator.py` |
| 5.5 | 前端人格编辑器 UI | `frontend/renderer/components/PersonalityEditor.js` |
| 5.6 | 人格切换即时生效 | 通信协议消息 |
| 5.7 | 人格数据持久化 | `%APPDATA%/游戏伴侣/personalities/` |

### 验证标准

- [ ] 6 套预设人格可加载
- [ ] 输入关键词，LLM 生成完整人格设定
- [ ] 人格编辑器可修改姓名、性格、口癖、系统提示词
- [ ] 切换人格后，AI 输出风格立即变化
- [ ] 人格数据保存为 JSON 文件，重启后恢复

---

## 阶段 6：弹幕引擎

### 目标
自动弹幕生成 + 前端弹幕动画。

### 子任务

| # | 任务 | 产出文件 |
|---|------|---------|
| 6.1 | CSS 弹幕动画 | `frontend/renderer/styles/danmaku.css` |
| 6.2 | 弹幕队列管理 | `frontend/renderer/modules/danmaku-engine.js` |
| 6.3 | 轨道系统（上/中/下） | `frontend/renderer/modules/danmaku-engine.js` |
| 6.4 | 密度控制 + 优先级队列 | `frontend/renderer/modules/danmaku-engine.js` |
| 6.5 | 后端弹幕生成（基于场景+人格） | `backend/ai/engine.py` |
| 6.6 | 弹幕发送消息协议 | 通信协议扩展 |
| 6.7 | 弹幕历史记录 | `%APPDATA%/游戏伴侣/danmaku_history.db` |

### 验证标准

- [ ] 弹幕从右向左平移，CSS 动画不占用主线程
- [ ] 三轨道自动分配，不重叠
- [ ] 每秒最大弹幕数可配置
- [ ] 高优先级弹幕插队显示
- [ ] 队列满时丢弃低优先级弹幕
- [ ] 弹幕层 pointer-events: none，不拦截游戏操作

---

## 阶段 7：搜索系统

### 目标
多引擎网页搜索 + 结果返回。

### 子任务

| # | 任务 | 产出文件 |
|---|------|---------|
| 7.1 | 搜索统一入口 | `backend/search/engine.py` |
| 7.2 | Google Search Provider | `backend/search/providers/google.py` |
| 7.3 | Bing Search Provider | `backend/search/providers/bing.py` |
| 7.4 | SearXNG Provider | `backend/search/providers/searxng.py` |
| 7.5 | 搜索缓存（TTL 24h） | `%APPDATA%/游戏伴侣/search_cache.db` |
| 7.6 | 前端搜索结果显示 | `frontend/renderer/components/SidePanel.js` |

### 验证标准

- [ ] 用户提问触发搜索 + AI 回答
- [ ] 搜索结果缓存，24 小时内重复查询不请求
- [ ] 搜索引擎不可用时，AI 仅凭知识回答
- [ ] 侧边栏显示搜索结果摘要

---

## 阶段 8：设置系统

### 目标
完整设置面板 + 配置持久化。

### 子任务

| # | 任务 | 产出文件 |
|---|------|---------|
| 8.1 | 设置面板 UI 框架 | `frontend/renderer/components/SettingsPanel.js` |
| 8.2 | 通用设置（自启、快捷键、语言、模块开关） | 设置面板子组件 |
| 8.3 | 界面设置（透明度、弹幕、主题） | 设置面板子组件 |
| 8.4 | AI 设置（Provider、API、模型、提示词） | 设置面板子组件 |
| 8.5 | 游戏设置（截图频率、识别区域） | 设置面板子组件 |
| 8.6 | 弹幕设置（开关、频率、风格） | 设置面板子组件 |
| 8.7 | 搜索设置（引擎、API、代理） | 设置面板子组件 |
| 8.8 | 记忆设置（向量、重排、参数、健康度） | 设置面板子组件 |
| 8.9 | 人格设置（选择、编辑器入口） | 设置面板子组件 |
| 8.10 | 配置持久化（config.json 读写） | 前后端同步 |
| 8.11 | 配置热加载（WebSocket 通知） | 通信协议扩展 |
| 8.12 | 配置导入/导出 | 设置面板功能 |

### 验证标准

- [ ] 设置面板所有分类可访问
- [ ] 修改配置即时生效
- [ ] 重启后配置恢复
- [ ] 配置导出为 JSON 文件，可导入恢复
- [ ] Python 后端收到配置变更通知后热加载

---

## 阶段 9：打包发布

### 目标
一键安装包 + 自动更新。

### 子任务

| # | 任务 | 产出文件 |
|---|------|---------|
| 9.1 | electron-builder 配置 | `frontend/package.json` (build 字段) |
| 9.2 | Python 打包（PyInstaller 或内嵌） | 打包脚本 |
| 9.3 | 安装包生成（.exe / .msi） | `dist/` 目录 |
| 9.4 | 自动更新机制 | 更新模块 |
| 9.5 | 开机自启注册 | `frontend/main/auto-launch.js` |

### 验证标准

- [ ] 双击安装包，安装成功
- [ ] 启动后 Electron + Python 正常运行
- [ ] 开机自启生效
- [ ] 检测到新版本时提示更新

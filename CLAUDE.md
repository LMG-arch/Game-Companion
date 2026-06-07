# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在本仓库中工作时提供指导。

## 项目概述

游戏伴侣是一款 Windows 桌面覆盖工具，在游戏过程中提供实时鼓励、攻略搜索、弹幕互动和 AI 问答服务。所有数据存储在 `%APPDATA%/游戏伴侣/` 本地目录。

## 架构

**双进程模型**，通过 WebSocket（localhost，JSON `{type, id, payload}` 协议）通信。

- **前端**（`frontend/`）：Electron 透明覆盖窗口。原生 HTML/CSS/JS，不使用框架。管理 UI、点击穿透模式、全局快捷键、Python 进程生命周期。
- **后端**（`backend/`）：Python 异步服务器。屏幕捕获（dxcam/DXGI）、AI 集成、记忆系统、人格引擎、网页搜索。
- **端口发现**：Python 将端口号写入 `%TEMP%/game-companion-port.txt`，Electron 读取并连接。
- **进程生命周期**：Electron 通过 `child_process.spawn` 启动 Python，关闭时先发送 `shutdown` 消息再 kill 子进程。

## 关键设计决策

- **不使用 UI 框架** — 纯原生 HTML/CSS/JS
- **CSS `@keyframes`** 实现弹幕动画（不占用主线程）
- **点击穿透**：4 种模式（全穿透/输入/设置/气泡），通过 `pointer-events: none` 实现
- **Z-index 层级**：透明背景(1) → 弹幕(2) → 信息栏(3) → 气泡(4) → 侧边栏(5) → 输入框(6) → 设置面板(7)
- **AI 提供商**：用户可配置（OpenAI/Claude/DeepSeek/自定义），统一接口带重试和降级
- **记忆系统**：向量搜索 + 重排序器，优雅降级到关键词搜索 → 空上下文
- **屏幕捕获**：dxcam 约 1ms/帧，帧哈希变化检测，空闲时自动降频

## 实现阶段

详见 `docs/superpowers/plans/00-overview.md`。共 9 个阶段：

1. 项目脚手架 + WebSocket 通信层
2. Electron UI 核心（透明窗口、模块、点击穿透）
3. 屏幕捕获 + AI 视觉分析
4. 记忆系统（向量 + 重排序 + 降级）
5. 人格系统（预设 + LLM 生成 + 编辑器）
6. 弹幕引擎（自动生成 + 动画）
7. 搜索系统（多引擎）
8. 设置系统（完整配置面板 + 持久化）
9. 打包发布

阶段 1 无依赖；阶段 2–7 依赖阶段 1；阶段 8 依赖 2–7；阶段 9 依赖 8。

## 语言要求

本项目所有内容使用**中文**，包括但不限于：
- 代码注释
- commit message
- README.md 文档
- CLAUDE.md 文档
- 日志输出

不要使用英语。

## 版本管理工作流

每次修改必须遵循以下流程：

1. **更新 README.md** — 反映变更内容（新功能、配置步骤、使用说明）
2. **提交** — 写清晰的 commit message 描述变更
3. **推送** — 推送到远程 `origin`（`https://github.com/LMG-arch/game-ai-Partner.git`）

禁止不更新 README.md 就提交。即使是内部重构（无用户可见变更），也要更新 README.md 的变更记录部分。

## 设计规格

完整规格说明：`docs/superpowers/specs/2026-06-07-game-companion-design.md`

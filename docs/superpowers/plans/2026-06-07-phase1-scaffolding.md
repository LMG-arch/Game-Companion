# 阶段 1：项目脚手架 + WebSocket 通信层 实现计划

> **致代理工作者：** 必须使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务执行此计划。步骤使用 checkbox (`- [ ]`) 语法追踪进度。

**目标：** 建立 Electron + Python 双进程架构，实现 WebSocket 通信连通。

**架构：** Electron 主进程启动 Python 子进程，Python 写入端口号到临时文件，Electron 读取并建立 WebSocket 连接。通信使用 JSON `{type, id, payload}` 协议。

**技术栈：** Electron、Python asyncio、websockets 库、child_process.spawn

---

## 文件结构

| 文件 | 职责 |
|------|------|
| `backend/main.py` | Python 入口：启动 WebSocket 服务器 |
| `backend/core/websocket_server.py` | WebSocket 服务器：消息收发、路由 |
| `backend/core/config.py` | 配置读取：从 config.json 加载配置 |
| `backend/utils/port_file.py` | 端口发现：写入端口号到临时文件 |
| `backend/utils/logger.py` | 日志模块 |
| `backend/requirements.txt` | Python 依赖 |
| `frontend/package.json` | Electron 项目配置 |
| `frontend/main/main.js` | Electron 入口：透明窗口、进程管理 |
| `frontend/main/python-manager.js` | Python 进程管理：启动、监控、关闭 |
| `frontend/renderer/index.html` | 前端页面入口 |
| `frontend/renderer/index.js` | 前端入口 JS：WebSocket 连接初始化 |
| `frontend/renderer/modules/web-socket.js` | WebSocket 客户端：连接、重连、消息收发 |
| `start.bat` | 一键启动脚本 |

---

### 任务 1：创建项目目录结构

**文件：**
- 创建：`backend/`、`backend/core/`、`backend/utils/`、`backend/ai/`、`backend/screen/`、`backend/memory/`、`backend/search/`、`backend/personality/`
- 创建：`frontend/`、`frontend/main/`、`frontend/renderer/`、`frontend/renderer/modules/`、`frontend/renderer/components/`、`frontend/renderer/styles/`、`frontend/renderer/utils/`

- [ ] **步骤 1：创建后端目录**

```bash
mkdir -p backend/core backend/utils backend/ai/providers backend/screen backend/memory backend/search backend/personality
```

- [ ] **步骤 2：创建前端目录**

```bash
mkdir -p frontend/main frontend/renderer/modules frontend/renderer/components frontend/renderer/styles frontend/renderer/utils
```

- [ ] **步骤 3：创建 __init__.py 文件（Python 包标识）**

```bash
touch backend/__init__.py backend/core/__init__.py backend/utils/__init__.py backend/ai/__init__.py backend/ai/providers/__init__.py backend/screen/__init__.py backend/memory/__init__.py backend/search/__init__.py backend/personality/__init__.py
```

- [ ] **步骤 4：提交**

```bash
git add backend/ frontend/
git commit -m "初始化：创建项目目录结构"
```

---

### 任务 2：Python 日志模块

**文件：**
- 创建：`backend/utils/logger.py`
- 测试：手动验证日志输出

- [ ] **步骤 1：创建日志模块**

```python
# backend/utils/logger.py
"""日志模块：统一日志格式和输出"""

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "game-companion") -> logging.Logger:
    """创建并配置日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 控制台输出
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    # 文件输出
    log_dir = Path.home() / "AppData" / "Roaming" / "游戏伴侣" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "game-companion.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s:%(lineno)d: %(message)s"
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 全局日志器
logger = setup_logger()
```

- [ ] **步骤 2：验证日志模块**

```bash
cd "D:/ai/游戏伴侣" && python -c "from backend.utils.logger import logger; logger.info('日志模块测试成功')"
```

预期输出：`[HH:MM:SS] INFO game-companion: 日志模块测试成功`

- [ ] **步骤 3：提交**

```bash
git add backend/utils/logger.py
git commit -m "添加日志模块"
```

---

### 任务 3：Python 配置读取模块

**文件：**
- 创建：`backend/core/config.py`
- 创建：`%APPDATA%/游戏伴侣/config.json`（默认配置）

- [ ] **步骤 1：创建配置模块**

```python
# backend/core/config.py
"""配置读取模块：从 config.json 加载配置，支持热加载"""

import json
from pathlib import Path
from typing import Any

from backend.utils.logger import logger

# 默认配置
DEFAULT_CONFIG = {
    "general": {
        "auto_launch": False,
        "language": "zh-CN",
        "modules": {
            "toolbar": True,
            "sidebar": True,
            "bubble": True,
            "danmaku": True
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
        "fallback_provider": None
    },
    "game": {
        "capture_fps": 1,
        "silent_fps": 0.2,
        "silent_threshold": 5,
        "capture_region": "fullscreen"
    },
    "danmaku": {
        "auto_enabled": True,
        "encouragement_interval": 30,
        "style": "auto",
        "blocked_keywords": []
    },
    "search": {
        "engine": "google",
        "api_url": "",
        "api_key": "",
        "proxy": None
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


class Config:
    """配置管理器"""

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or (
            Path.home() / "AppData" / "Roaming" / "游戏伴侣" / "config.json"
        )
        self._data: dict = {}
        self.load()

    def load(self) -> None:
        """加载配置文件，不存在则创建默认配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                logger.info(f"配置已加载: {self.config_path}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"配置文件读取失败: {e}，使用默认配置")
                self._data = DEFAULT_CONFIG.copy()
                self.save()
        else:
            logger.info("配置文件不存在，创建默认配置")
            self._data = DEFAULT_CONFIG.copy()
            self.save()

    def save(self) -> None:
        """保存配置到文件"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        logger.info(f"配置已保存: {self.config_path}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项，支持点号分隔的路径（如 'ai.provider'）"""
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """设置配置项，支持点号分隔的路径"""
        keys = key.split(".")
        data = self._data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value

    def update(self, section: str, changes: dict) -> None:
        """更新配置的某个部分"""
        if section not in self._data:
            self._data[section] = {}
        self._data[section].update(changes)

    @property
    def data(self) -> dict:
        return self._data


# 全局配置实例
config = Config()
```

- [ ] **步骤 2：验证配置模块**

```bash
cd "D:/ai/游戏伴侣" && python -c "from backend.core.config import config; print(config.get('ai.provider')); print(config.get('ai.model'))"
```

预期输出：
```
openai
gpt-4o
```

- [ ] **步骤 3：提交**

```bash
git add backend/core/config.py
git commit -m "添加配置读取模块"
```

---

### 任务 4：Python 端口发现模块

**文件：**
- 创建：`backend/utils/port_file.py`

- [ ] **步骤 1：创建端口文件模块**

```python
# backend/utils/port_file.py
"""端口发现：将 WebSocket 服务器端口号写入临时文件"""

import os
from pathlib import Path

from backend.utils.logger import logger

# 端口文件路径
PORT_FILE = Path(os.environ.get("TEMP", "/tmp")) / "game-companion-port.txt"


def write_port(port: int) -> None:
    """将端口号写入临时文件"""
    try:
        PORT_FILE.write_text(str(port), encoding="utf-8")
        logger.info(f"端口号已写入: {PORT_FILE} -> {port}")
    except IOError as e:
        logger.error(f"写入端口文件失败: {e}")
        raise


def read_port() -> int | None:
    """从临时文件读取端口号"""
    try:
        if PORT_FILE.exists():
            port = int(PORT_FILE.read_text(encoding="utf-8").strip())
            logger.info(f"读取端口号: {port}")
            return port
        return None
    except (IOError, ValueError) as e:
        logger.error(f"读取端口文件失败: {e}")
        return None


def cleanup_port() -> None:
    """清理端口文件"""
    try:
        if PORT_FILE.exists():
            PORT_FILE.unlink()
            logger.info("端口文件已清理")
    except IOError as e:
        logger.error(f"清理端口文件失败: {e}")
```

- [ ] **步骤 2：验证端口文件模块**

```bash
cd "D:/ai/游戏伴侣" && python -c "
from backend.utils.port_file import write_port, read_port, cleanup_port
write_port(12345)
print(f'读取: {read_port()}')
cleanup_port()
print(f'清理后: {read_port()}')
"
```

预期输出：
```
读取: 12345
清理后: None
```

- [ ] **步骤 3：提交**

```bash
git add backend/utils/port_file.py
git commit -m "添加端口发现模块"
```

---

### 任务 5：Python WebSocket 服务器

**文件：**
- 创建：`backend/core/websocket_server.py`

- [ ] **步骤 1：创建 WebSocket 服务器**

```python
# backend/core/websocket_server.py
"""WebSocket 服务器：消息收发、路由"""

import asyncio
import json
from typing import Callable, Any

import websockets
from websockets.server import serve, WebSocketServerProtocol

from backend.utils.logger import logger


# 消息处理器类型
MessageHandler = Callable[[dict], dict | None]


class WebSocketServer:
    """WebSocket 服务器"""

    def __init__(self, host: str = "localhost"):
        self.host = host
        self.port: int = 0
        self.server = None
        self.clients: set[WebSocketServerProtocol] = set()
        self.handlers: dict[str, MessageHandler] = {}

    def on(self, message_type: str, handler: MessageHandler) -> None:
        """注册消息处理器"""
        self.handlers[message_type] = handler

    async def _handle_connection(self, websocket: WebSocketServerProtocol) -> None:
        """处理单个客户端连接"""
        self.clients.add(websocket)
        logger.info(f"客户端已连接，当前连接数: {len(self.clients)}")

        try:
            async for raw_message in websocket:
                try:
                    message = json.loads(raw_message)
                    logger.debug(f"收到消息: {message.get('type')}")

                    # 调用对应的处理器
                    response = await self._dispatch(message)
                    if response:
                        await websocket.send(json.dumps(response, ensure_ascii=False))

                except json.JSONDecodeError:
                    logger.error(f"无效的 JSON 消息: {raw_message}")
                except Exception as e:
                    logger.error(f"处理消息时出错: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("客户端断开连接")
        finally:
            self.clients.discard(websocket)
            logger.info(f"客户端已断开，当前连接数: {len(self.clients)}")

    async def _dispatch(self, message: dict) -> dict | None:
        """分发消息到对应的处理器"""
        msg_type = message.get("type")
        msg_id = message.get("id", "")

        if msg_type == "ping":
            return {"type": "pong", "id": msg_id, "payload": {}}

        handler = self.handlers.get(msg_type)
        if handler:
            try:
                result = handler(message.get("payload", {}))
                if result:
                    return {"type": f"{msg_type}.result", "id": msg_id, "payload": result}
            except Exception as e:
                logger.error(f"处理器 {msg_type} 出错: {e}")
                return {
                    "type": "error",
                    "id": msg_id,
                    "payload": {"code": "HANDLER_ERROR", "message": str(e)}
                }
        else:
            logger.warning(f"未知消息类型: {msg_type}")
            return {
                "type": "error",
                "id": msg_id,
                "payload": {"code": "UNKNOWN_TYPE", "message": f"未知消息类型: {msg_type}"}
            }

    async def send(self, message_type: str, payload: dict, msg_id: str = "") -> None:
        """向所有客户端广播消息"""
        message = json.dumps(
            {"type": message_type, "id": msg_id, "payload": payload},
            ensure_ascii=False
        )
        for client in self.clients.copy():
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                self.clients.discard(client)

    async def start(self) -> int:
        """启动服务器，返回端口号"""
        self.server = await serve(
            self._handle_connection,
            self.host,
            0  # 随机端口
        )
        # 获取实际端口号
        self.port = self.server.sockets[0].getsockname()[1]
        logger.info(f"WebSocket 服务器已启动: ws://{self.host}:{self.port}")
        return self.port

    async def stop(self) -> None:
        """停止服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket 服务器已停止")
```

- [ ] **步骤 2：验证服务器模块可导入**

```bash
cd "D:/ai/游戏伴侣" && python -c "from backend.core.websocket_server import WebSocketServer; print('WebSocket 服务器模块加载成功')"
```

预期输出：`WebSocket 服务器模块加载成功`

- [ ] **步骤 3：提交**

```bash
git add backend/core/websocket_server.py
git commit -m "添加 WebSocket 服务器模块"
```

---

### 任务 6：Python 后端入口

**文件：**
- 创建：`backend/main.py`
- 创建：`backend/requirements.txt`

- [ ] **步骤 1：创建 requirements.txt**

```
# backend/requirements.txt
websockets>=12.0
```

- [ ] **步骤 2：安装依赖**

```bash
cd "D:/ai/游戏伴侣/backend" && pip install -r requirements.txt
```

预期输出：成功安装 websockets

- [ ] **步骤 3：创建后端入口**

```python
# backend/main.py
"""Python 后端入口：启动 WebSocket 服务器"""

import asyncio
import signal
import sys

from backend.core.websocket_server import WebSocketServer
from backend.core.config import config
from backend.utils.port_file import write_port, cleanup_port
from backend.utils.logger import logger


async def main():
    """主函数"""
    logger.info("游戏伴侣后端启动中...")

    # 创建 WebSocket 服务器
    server = WebSocketServer()

    # 注册消息处理器（后续阶段扩展）
    def handle_question(payload: dict) -> dict:
        """处理用户提问（占位）"""
        return {"answer": "功能开发中...", "sources": []}

    server.on("question.ask", handle_question)

    # 启动服务器
    port = await server.start()

    # 写入端口文件
    write_port(port)

    logger.info("后端已就绪，等待前端连接...")

    # 等待关闭信号
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("收到关闭信号")
        stop_event.set()

    # Windows 下使用 SIGINT
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Windows 不支持 add_signal_handler
            pass

    # 等待关闭或 Ctrl+C
    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("收到 Ctrl+C")

    # 清理
    await server.stop()
    cleanup_port()
    logger.info("后端已关闭")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```

- [ ] **步骤 4：验证后端可启动**

```bash
cd "D:/ai/游戏伴侣" && timeout 3 python -m backend.main || true
```

预期输出：包含 "WebSocket 服务器已启动" 和端口号的日志

- [ ] **步骤 5：提交**

```bash
git add backend/main.py backend/requirements.txt
git commit -m "添加后端入口和依赖"
```

---

### 任务 7：Electron 项目初始化

**文件：**
- 创建：`frontend/package.json`

- [ ] **步骤 1：创建 package.json**

```json
{
  "name": "game-companion",
  "version": "0.1.0",
  "description": "游戏伴侣 - Windows 桌面游戏覆盖工具",
  "main": "main/main.js",
  "scripts": {
    "start": "electron .",
    "dev": "electron . --dev"
  },
  "author": "",
  "license": "MIT",
  "devDependencies": {
    "electron": "^33.0.0"
  }
}
```

- [ ] **步骤 2：安装 Electron 依赖**

```bash
cd "D:/ai/游戏伴侣/frontend" && npm install
```

预期输出：成功安装 electron

- [ ] **步骤 3：提交**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "初始化 Electron 项目"
```

---

### 任务 8：Electron Python 进程管理

**文件：**
- 创建：`frontend/main/python-manager.js`

- [ ] **步骤 1：创建 Python 进程管理模块**

```javascript
// frontend/main/python-manager.js
/**
 * Python 进程管理模块
 * 负责启动、监控、关闭 Python 子进程
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

class PythonManager {
  constructor() {
    this.process = null;
    this.portFile = path.join(process.env.TEMP || '/tmp', 'game-companion-port.txt');
    this.backendPath = path.join(__dirname, '..', '..', 'backend');
  }

  /**
   * 启动 Python 子进程
   * @returns {Promise<void>}
   */
  start() {
    return new Promise((resolve, reject) => {
      // 清理旧的端口文件
      if (fs.existsSync(this.portFile)) {
        fs.unlinkSync(this.portFile);
      }

      // 启动 Python 进程
      this.process = spawn('python', ['-m', 'backend.main'], {
        cwd: path.join(__dirname, '..', '..'),
        stdio: ['pipe', 'pipe', 'pipe'],
        shell: true
      });

      // 监听输出
      this.process.stdout.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          console.log(`[Python] ${output}`);
        }
      });

      this.process.stderr.on('data', (data) => {
        const output = data.toString().trim();
        if (output) {
          console.error(`[Python Error] ${output}`);
        }
      });

      // 监听进程退出
      this.process.on('exit', (code) => {
        console.log(`Python 进程已退出，退出码: ${code}`);
        this.process = null;
      });

      // 等待端口文件出现（最多 10 秒）
      let attempts = 0;
      const checkPort = setInterval(() => {
        attempts++;
        if (fs.existsSync(this.portFile)) {
          clearInterval(checkPort);
          resolve();
        } else if (attempts > 100) {
          clearInterval(checkPort);
          reject(new Error('Python 启动超时'));
        }
      }, 100);
    });
  }

  /**
   * 读取 Python 写入的端口号
   * @returns {number|null}
   */
  getPort() {
    try {
      if (fs.existsSync(this.portFile)) {
        return parseInt(fs.readFileSync(this.portFile, 'utf-8').trim());
      }
    } catch (e) {
      console.error('读取端口文件失败:', e);
    }
    return null;
  }

  /**
   * 关闭 Python 子进程
   */
  async shutdown() {
    if (this.process) {
      // 尝试发送关闭消息（通过 stdin）
      try {
        this.process.stdin.write('shutdown\n');
      } catch (e) {
        // 忽略
      }

      // 等待 2 秒，如果还没退出就强制 kill
      await new Promise((resolve) => {
        const timeout = setTimeout(() => {
          if (this.process) {
            this.process.kill('SIGTERM');
          }
          resolve();
        }, 2000);

        this.process.on('exit', () => {
          clearTimeout(timeout);
          resolve();
        });
      });

      this.process = null;
    }
  }

  /**
   * 检查 Python 进程是否在运行
   * @returns {boolean}
   */
  isRunning() {
    return this.process !== null;
  }
}

module.exports = PythonManager;
```

- [ ] **步骤 2：验证模块可加载**

```bash
cd "D:/ai/游戏伴侣/frontend" && node -e "const PM = require('./main/python-manager'); console.log('Python 管理模块加载成功')"
```

预期输出：`Python 管理模块加载成功`

- [ ] **步骤 3：提交**

```bash
git add frontend/main/python-manager.js
git commit -m "添加 Python 进程管理模块"
```

---

### 任务 9：Electron 主进程

**文件：**
- 创建：`frontend/main/main.js`

- [ ] **步骤 1：创建 Electron 主进程**

```javascript
// frontend/main/main.js
/**
 * Electron 主进程入口
 * 创建透明覆盖窗口，管理 Python 子进程
 */

const { app, BrowserWindow } = require('electron');
const path = require('path');
const PythonManager = require('./python-manager');

// Python 进程管理器
const pythonManager = new PythonManager();

// 主窗口
let mainWindow = null;

/**
 * 创建透明覆盖窗口
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1920,
    height: 1080,
    transparent: true,
    frame: false,
    alwaysOnTop: true,
    fullscreen: true,
    skipTaskbar: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));

  // 开发模式下打开 DevTools
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * 应用启动
 */
app.whenReady().then(async () => {
  console.log('Electron 已启动');

  // 启动 Python 子进程
  try {
    await pythonManager.start();
    const port = pythonManager.getPort();
    console.log(`Python 端口: ${port}`);

    // 创建窗口
    createWindow();

    // 通知渲染进程连接 WebSocket
    if (mainWindow) {
      mainWindow.webContents.on('did-finish-load', () => {
        mainWindow.webContents.send('python-ready', { port });
      });
    }
  } catch (e) {
    console.error('Python 启动失败:', e);
    app.quit();
  }
});

/**
 * 应用关闭
 */
app.on('window-all-closed', async () => {
  console.log('正在关闭...');
  await pythonManager.shutdown();
  app.quit();
});

app.on('before-quit', async () => {
  await pythonManager.shutdown();
});
```

- [ ] **步骤 2：验证主进程可加载**

```bash
cd "D:/ai/游戏伴侣/frontend" && node -e "require('./main/main'); console.log('主进程模块加载成功')" 2>&1 | head -5
```

预期输出：包含 "主进程模块加载成功"

- [ ] **步骤 3：提交**

```bash
git add frontend/main/main.js
git commit -m "添加 Electron 主进程"
```

---

### 任务 10：WebSocket 客户端模块

**文件：**
- 创建：`frontend/renderer/modules/web-socket.js`

- [ ] **步骤 1：创建 WebSocket 客户端**

```javascript
// frontend/renderer/modules/web-socket.js
/**
 * WebSocket 客户端模块
 * 负责连接、重连、消息收发
 */

class WebSocketClient {
  constructor() {
    this.ws = null;
    this.url = null;
    this.handlers = {};
    this.reconnectTimer = null;
    this.reconnectDelay = 3000; // 初始重连延迟 3 秒
    this.maxReconnectDelay = 30000; // 最大重连延迟 30 秒
    this.isConnected = false;
  }

  /**
   * 连接到 WebSocket 服务器
   * @param {number} port - 端口号
   */
  connect(port) {
    this.url = `ws://localhost:${port}`;
    console.log(`正在连接 WebSocket: ${this.url}`);

    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('WebSocket 已连接');
      this.isConnected = true;
      this.reconnectDelay = 3000; // 重置重连延迟
      this._emit('connected', {});
    };

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log(`收到消息: ${message.type}`);
        this._emit(message.type, message.payload || {});
        this._emit('message', message);
      } catch (e) {
        console.error('解析消息失败:', e);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket 已断开');
      this.isConnected = false;
      this._emit('disconnected', {});
      this._scheduleReconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket 错误:', error);
    };
  }

  /**
   * 发送消息
   * @param {string} type - 消息类型
   * @param {object} payload - 消息内容
   * @returns {string} 消息 ID
   */
  send(type, payload = {}) {
    if (!this.isConnected) {
      console.warn('WebSocket 未连接，无法发送消息');
      return null;
    }

    const id = crypto.randomUUID();
    const message = { type, id, payload };
    this.ws.send(JSON.stringify(message));
    return id;
  }

  /**
   * 注册消息处理器
   * @param {string} type - 消息类型
   * @param {function} handler - 处理函数
   */
  on(type, handler) {
    if (!this.handlers[type]) {
      this.handlers[type] = [];
    }
    this.handlers[type].push(handler);
  }

  /**
   * 触发事件
   */
  _emit(type, data) {
    const handlers = this.handlers[type] || [];
    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (e) {
        console.error(`处理器 ${type} 出错:`, e);
      }
    });
  }

  /**
   * 计划重连
   */
  _scheduleReconnect() {
    if (this.reconnectTimer) return;

    console.log(`${this.reconnectDelay / 1000} 秒后重连...`);
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (this.url) {
        this.connect(this.url.replace('ws://localhost:', ''));
      }
    }, this.reconnectDelay);

    // 指数退避
    this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
  }
}

// 导出单例
window.wsClient = new WebSocketClient();
```

- [ ] **步骤 2：提交**

```bash
git add frontend/renderer/modules/web-socket.js
git commit -m "添加 WebSocket 客户端模块"
```

---

### 任务 11：前端页面入口

**文件：**
- 创建：`frontend/renderer/index.html`
- 创建：`frontend/renderer/index.js`

- [ ] **步骤 1：创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>游戏伴侣</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      background: transparent;
      font-family: 'Microsoft YaHei', sans-serif;
      color: #fff;
      overflow: hidden;
      user-select: none;
    }

    /* 状态显示 */
    #status {
      position: fixed;
      top: 10px;
      left: 10px;
      padding: 8px 16px;
      background: rgba(0, 0, 0, 0.7);
      border-radius: 4px;
      font-size: 14px;
      z-index: 1000;
      pointer-events: none;
    }

    #status.connected {
      color: #4caf50;
    }

    #status.disconnected {
      color: #f44336;
    }

    /* 测试区域（开发用） */
    #test-area {
      position: fixed;
      top: 50px;
      left: 10px;
      padding: 16px;
      background: rgba(0, 0, 0, 0.8);
      border-radius: 8px;
      z-index: 1000;
    }

    #test-area button {
      padding: 8px 16px;
      margin: 4px;
      background: #2196f3;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }

    #test-area button:hover {
      background: #1976d2;
    }

    #test-result {
      margin-top: 8px;
      padding: 8px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 4px;
      font-size: 12px;
      max-width: 300px;
      word-break: break-all;
    }
  </style>
</head>
<body>
  <div id="status" class="disconnected">⏳ 等待连接...</div>

  <div id="test-area">
    <div>
      <button id="btn-ping">发送 Ping</button>
      <button id="btn-question">测试提问</button>
    </div>
    <div id="test-result">等待操作...</div>
  </div>

  <script src="modules/web-socket.js"></script>
  <script src="index.js"></script>
</body>
</html>
```

- [ ] **步骤 2：创建 index.js**

```javascript
// frontend/renderer/index.js
/**
 * 前端入口 JS
 * 初始化 WebSocket 连接，处理消息
 */

const { ipcRenderer } = require('electron');

const statusEl = document.getElementById('status');
const testResultEl = document.getElementById('test-result');

// 更新连接状态显示
function updateStatus(connected) {
  if (connected) {
    statusEl.textContent = '✅ 已连接';
    statusEl.className = 'connected';
  } else {
    statusEl.textContent = '❌ 已断开';
    statusEl.className = 'disconnected';
  }
}

// 监听 Python 就绪事件
ipcRenderer.on('python-ready', (event, { port }) => {
  console.log(`Python 端口: ${port}`);
  wsClient.connect(port);
});

// WebSocket 事件监听
wsClient.on('connected', () => {
  updateStatus(true);
  testResultEl.textContent = '已连接到后端';
});

wsClient.on('disconnected', () => {
  updateStatus(false);
});

// 收到 pong
wsClient.on('pong', (payload) => {
  testResultEl.textContent = `收到 Pong: ${JSON.stringify(payload)}`;
});

// 收到问题回答
wsClient.on('question.answer.result', (payload) => {
  testResultEl.textContent = `回答: ${JSON.stringify(payload)}`;
});

// 收到错误
wsClient.on('error', (payload) => {
  testResultEl.textContent = `错误: ${payload.message}`;
});

// 测试按钮
document.getElementById('btn-ping').addEventListener('click', () => {
  const id = wsClient.send('ping');
  testResultEl.textContent = `已发送 Ping (id: ${id})`;
});

document.getElementById('btn-question').addEventListener('click', () => {
  const id = wsClient.send('question.ask', { text: '测试问题' });
  testResultEl.textContent = `已发送提问 (id: ${id})`;
});

console.log('前端已加载');
```

- [ ] **步骤 3：提交**

```bash
git add frontend/renderer/index.html frontend/renderer/index.js
git commit -m "添加前端页面入口"
```

---

### 任务 12：启动脚本

**文件：**
- 创建：`start.bat`

- [ ] **步骤 1：创建启动脚本**

```bat
@echo off
chcp 65001 >nul
echo 启动游戏伴侣...
cd /d "%~dp0frontend"
npx electron .
```

- [ ] **步骤 2：提交**

```bash
git add start.bat
git commit -m "添加启动脚本"
```

---

### 任务 13：集成测试 — 通信验证

**文件：**
- 修改：无（手动测试）

- [ ] **步骤 1：启动应用**

```bash
cd "D:/ai/游戏伴侣" && start.bat
```

预期：Electron 窗口打开，状态显示 "✅ 已连接"

- [ ] **步骤 2：测试 Ping/Pong**

点击 "发送 Ping" 按钮。

预期：显示 "收到 Pong: {}"

- [ ] **步骤 3：测试提问**

点击 "测试提问" 按钮。

预期：显示 "回答: {"answer":"功能开发中...","sources":[]}"

- [ ] **步骤 4：测试关闭**

关闭 Electron 窗口。

预期：Python 进程退出，无残留进程（任务管理器确认）

- [ ] **步骤 5：最终提交**

```bash
git add -A
git commit -m "阶段 1 完成：项目脚手架 + WebSocket 通信层"
```

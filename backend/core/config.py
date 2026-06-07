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
        # 项目根目录下的 config.json
        self.config_path = config_path or (
            Path(__file__).parent.parent.parent / "config.json"
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

# backend/ai/providers/base.py
"""AI Provider 基类：统一接口、httpx 客户端复用、响应解析"""

import httpx
from typing import Optional

from backend.utils.logger import logger


class BaseProvider:
    """AI Provider 基类"""

    def __init__(self, api_url: str = "", api_key: str = "", model: str = "",
                 temperature: float = 0.7, max_tokens: int = 500, timeout: int = 30):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """获取或创建 httpx 客户端（复用连接）"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        """关闭 httpx 客户端"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def parse_response(self, content: str) -> dict:
        """解析 AI 回复为结构化数据（公共方法）"""
        lines = content.strip().split("\n")
        scene = "unknown"
        description = content
        suggestion = ""

        for line in lines:
            line = line.strip()
            if line.startswith("场景:") or line.startswith("场景："):
                scene = line.split(":", 1)[-1].split("：", 1)[-1].strip()
            elif line.startswith("建议:") or line.startswith("建议："):
                suggestion = line.split(":", 1)[-1].split("：", 1)[-1].strip()

        return {
            "scene": scene,
            "description": description,
            "suggestion": suggestion,
        }

    async def analyze_image(self, image_bytes: bytes, system_prompt: str = "",
                           user_prompt: str = "描述这张图片中的游戏场景") -> Optional[dict]:
        """分析图片（子类实现）"""
        raise NotImplementedError

    async def chat(self, messages: list[dict], system_prompt: str = "") -> Optional[str]:
        """文本对话（子类实现）"""
        raise NotImplementedError

# backend/ai/providers/claude.py
"""Claude Provider：Anthropic Claude API"""

import base64
from typing import Optional

import httpx

from backend.utils.logger import logger


class ClaudeProvider:
    """Claude Provider"""

    def __init__(
        self,
        api_url: str = "https://api.anthropic.com",
        api_key: str = "",
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        max_tokens: int = 500,
        timeout: int = 30,
    ):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    async def analyze_image(
        self,
        image_bytes: bytes,
        system_prompt: str = "",
        user_prompt: str = "描述这张图片中的游戏场景",
    ) -> Optional[dict]:
        """分析图片"""
        if not self.api_key:
            raise ValueError("API Key 未配置")

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_b64,
                    },
                },
                {"type": "text", "text": user_prompt},
            ],
        }]

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages,
        }
        if system_prompt:
            body["system"] = system_prompt

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}/v1/messages",
                headers=headers,
                json=body,
            )
            response.raise_for_status()
            data = response.json()

        content = data["content"][0]["text"]
        return self._parse_response(content)

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str = "",
    ) -> Optional[str]:
        """文本对话"""
        if not self.api_key:
            raise ValueError("API Key 未配置")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages,
        }
        if system_prompt:
            body["system"] = system_prompt

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}/v1/messages",
                headers=headers,
                json=body,
            )
            response.raise_for_status()
            data = response.json()

        return data["content"][0]["text"]

    def _parse_response(self, content: str) -> dict:
        """解析 AI 回复为结构化数据"""
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

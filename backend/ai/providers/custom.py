# backend/ai/providers/custom.py
"""自定义 Provider：用户自定义 API 格式"""

import base64
from typing import Optional

import httpx

from backend.utils.logger import logger


class CustomProvider:
    """自定义 Provider"""

    def __init__(
        self,
        api_url: str = "",
        api_key: str = "",
        model: str = "",
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
        """分析图片（使用 OpenAI 兼容格式）"""
        if not self.api_url:
            raise ValueError("API URL 未配置")

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_b64}",
                    },
                },
            ],
        })

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body = {
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.model:
            body["model"] = self.model

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=body,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return self._parse_response(content)

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str = "",
    ) -> Optional[str]:
        """文本对话"""
        if not self.api_url:
            raise ValueError("API URL 未配置")

        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        body = {
            "messages": full_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.model:
            body["model"] = self.model

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=body,
            )
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]

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

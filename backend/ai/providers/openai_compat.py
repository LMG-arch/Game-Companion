# backend/ai/providers/openai_compat.py
"""OpenAI 兼容 Provider：支持 OpenAI API 格式"""

import base64
from typing import Optional

from backend.ai.providers.base import BaseProvider
from backend.utils.logger import logger


class OpenAICompatProvider(BaseProvider):
    """OpenAI 兼容 Provider"""

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
                        "detail": "low",
                    },
                },
            ],
        })

        response = await self.client.post(
            f"{self.api_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
        )
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        return self.parse_response(content)

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str = "",
    ) -> Optional[str]:
        """文本对话"""
        if not self.api_key:
            raise ValueError("API Key 未配置")

        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        response = await self.client.post(
            f"{self.api_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": full_messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
        )
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

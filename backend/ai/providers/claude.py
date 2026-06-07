# backend/ai/providers/claude.py
"""Claude Provider：Anthropic Claude API"""

import base64
from typing import Optional

from backend.ai.providers.base import BaseProvider
from backend.utils.logger import logger


class ClaudeProvider(BaseProvider):
    """Claude Provider"""

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

        response = await self.client.post(
            f"{self.api_url}/v1/messages",
            headers=headers,
            json=body,
        )
        response.raise_for_status()
        data = response.json()

        content = data["content"][0]["text"]
        return self.parse_response(content)

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

        response = await self.client.post(
            f"{self.api_url}/v1/messages",
            headers=headers,
            json=body,
        )
        response.raise_for_status()
        data = response.json()

        return data["content"][0]["text"]

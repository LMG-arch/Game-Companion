# backend/ai/engine.py
"""AI 引擎统一入口：管理 Provider、重试、降级"""

import asyncio
from typing import Optional

from backend.utils.logger import logger


class AIEngine:
    """AI 引擎"""

    def __init__(self, config: dict):
        self.config = config
        self.providers = {}
        self.current_provider = None
        self.fallback_provider = None
        self._init_providers()

    def _init_providers(self) -> None:
        """初始化 AI Provider"""
        from backend.ai.providers.openai_compat import OpenAICompatProvider
        from backend.ai.providers.claude import ClaudeProvider
        from backend.ai.providers.custom import CustomProvider

        provider_name = self.config.get("provider", "openai")
        fallback_name = self.config.get("fallback_provider")

        # 创建 Provider 实例
        provider_configs = {
            "openai": {
                "class": OpenAICompatProvider,
                "config": {
                    "api_url": self.config.get("api_url", "https://api.openai.com/v1"),
                    "api_key": self.config.get("api_key", ""),
                    "model": self.config.get("model", "gpt-4o"),
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 500),
                    "timeout": self.config.get("timeout", 30),
                }
            },
            "claude": {
                "class": ClaudeProvider,
                "config": {
                    "api_url": self.config.get("api_url", "https://api.anthropic.com"),
                    "api_key": self.config.get("api_key", ""),
                    "model": self.config.get("model", "claude-sonnet-4-20250514"),
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 500),
                    "timeout": self.config.get("timeout", 30),
                }
            },
            "custom": {
                "class": CustomProvider,
                "config": {
                    "api_url": self.config.get("api_url", ""),
                    "api_key": self.config.get("api_key", ""),
                    "model": self.config.get("model", ""),
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 500),
                    "timeout": self.config.get("timeout", 30),
                }
            },
        }

        # 初始化当前 Provider（检查 API Key 是否配置）
        if provider_name in provider_configs:
            pc = provider_configs[provider_name]
            if pc["config"].get("api_key"):
                self.providers[provider_name] = pc["class"](**pc["config"])
                self.current_provider = provider_name
                logger.info(f"AI Provider 已加载: {provider_name}")
            else:
                logger.warning(f"AI Provider {provider_name} 未配置 API Key，跳过加载")

        # 初始化降级 Provider
        if fallback_name and fallback_name in provider_configs:
            pc = provider_configs[fallback_name]
            if pc["config"].get("api_key"):
                self.providers[fallback_name] = pc["class"](**pc["config"])
                self.fallback_provider = fallback_name
                logger.info(f"降级 Provider 已加载: {fallback_name}")

        # 检查是否有可用的 Provider
        if not self.providers:
            logger.warning("没有可用的 AI Provider，请在设置中配置 API Key")

    def is_available(self) -> bool:
        """检查 AI 引擎是否可用"""
        return len(self.providers) > 0

    def get_status(self) -> dict:
        """获取 AI 引擎状态"""
        if not self.providers:
            return {"status": "offline", "message": "未配置 API Key"}
        return {"status": "online", "message": f"当前 Provider: {self.current_provider}"}

    async def analyze_image(
        self,
        image_bytes: bytes,
        system_prompt: str = "",
        user_prompt: str = "描述这张图片中的游戏场景",
    ) -> Optional[dict]:
        """
        分析图片

        Returns:
            {"scene": str, "description": str, "suggestion": str} 或 None
        """
        # 尝试当前 Provider
        result = await self._try_provider(
            self.current_provider, image_bytes, system_prompt, user_prompt
        )
        if result:
            return result

        # 降级到备用 Provider
        if self.fallback_provider:
            logger.warning(f"主 Provider 失败，切换到: {self.fallback_provider}")
            result = await self._try_provider(
                self.fallback_provider, image_bytes, system_prompt, user_prompt
            )
            if result:
                return result

        logger.error("所有 AI Provider 均不可用")
        return None

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str = "",
    ) -> Optional[str]:
        """
        文本对话

        Returns:
            回复文本或 None
        """
        provider = self.providers.get(self.current_provider)
        if not provider:
            return None

        try:
            return await provider.chat(messages, system_prompt)
        except Exception as e:
            logger.error(f"对话失败: {e}")
            return None

    async def _try_provider(
        self,
        provider_name: str,
        image_bytes: bytes,
        system_prompt: str,
        user_prompt: str,
    ) -> Optional[dict]:
        """尝试使用指定 Provider 分析图片"""
        provider = self.providers.get(provider_name)
        if not provider:
            return None

        try:
            return await provider.analyze_image(image_bytes, system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"Provider {provider_name} 分析失败: {e}")
            return None

# backend/search/engine.py
"""搜索统一入口"""

from typing import Optional
from backend.utils.logger import logger


class SearchEngine:
    """搜索引擎"""

    def __init__(self, config: dict):
        self.config = config
        self.engine = config.get("engine", "duckduckgo")
        self.provider = None
        self._init_provider()

    def _init_provider(self) -> None:
        """初始化搜索 Provider"""
        if self.engine == "duckduckgo":
            from backend.search.providers.duckduckgo import DuckDuckGoProvider
            self.provider = DuckDuckGoProvider()
            logger.info("搜索引擎已加载: DuckDuckGo")
        elif self.engine == "searxng":
            from backend.search.providers.searxng import SearXNGProvider
            self.provider = SearXNGProvider(self.config)
            logger.info("搜索引擎已加载: SearXNG")
        else:
            from backend.search.providers.duckduckgo import DuckDuckGoProvider
            self.provider = DuckDuckGoProvider()
            logger.info("搜索引擎已加载: DuckDuckGo (默认)")

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        """
        搜索

        Returns:
            [{"title": str, "url": str, "snippet": str}]
        """
        if not self.provider:
            logger.error("搜索引擎未初始化")
            return []

        try:
            results = await self.provider.search(query, limit)
            logger.info(f"搜索完成: {query} -> {len(results)} 条结果")
            return results
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

# backend/search/providers/searxng.py
"""SearXNG 搜索 Provider（自托管，免费）"""

from typing import Optional
import httpx

from backend.utils.logger import logger


class SearXNGProvider:
    """SearXNG 搜索"""

    def __init__(self, config: dict):
        self.api_url = config.get("api_url", "http://localhost:8888")

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        """搜索"""
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(
                    f"{self.api_url}/search",
                    params={
                        "q": query,
                        "format": "json",
                        "pageno": 1,
                    },
                )
                response.raise_for_status()
                data = response.json()

            results = []
            for item in data.get("results", [])[:limit]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", ""),
                })

            return results

        except Exception as e:
            logger.error(f"SearXNG 搜索失败: {e}")
            return []

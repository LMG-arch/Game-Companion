# backend/memory/reranker.py
"""重排模块：远程 API 重排，无配置跳过"""

from typing import Optional

import httpx

from backend.utils.logger import logger


class Reranker:
    """重排器"""

    def __init__(self, config: dict):
        self.api_url = config.get("api_url", "")
        self.api_key = config.get("api_key", "")
        self.available = False
        self._check_availability()

    def _check_availability(self) -> None:
        """检查重排 API 可用性"""
        if not self.api_url or not self.api_key:
            logger.info("重排模型未配置，将跳过重排")
            self.available = False
            return

        self.available = True
        logger.info(f"重排模型已启用: {self.api_url}")

    async def rerank(
        self,
        query: str,
        documents: list[str],
        top_n: int = 8,
    ) -> list[dict]:
        """重排文档"""
        if not self.available:
            return [{"index": i, "relevance_score": 0.5} for i in range(len(documents))]

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.api_url}/rerank",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "query": query,
                        "documents": documents,
                        "top_n": top_n,
                    },
                )
                response.raise_for_status()
                data = response.json()

            return data.get("results", [])

        except Exception as e:
            logger.error(f"重排失败: {e}")
            return [{"index": i, "relevance_score": 0.5} for i in range(len(documents))]

# backend/memory/vector_store.py
"""向量检索模块：远程 API 向量检索，无配置降级关键词"""

import json
from typing import Optional

import httpx

from backend.utils.logger import logger


class VectorStore:
    """向量检索"""

    def __init__(self, config: dict):
        self.api_url = config.get("api_url", "")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "")
        self.available = False
        self._check_availability()

    def _check_availability(self) -> None:
        """检查向量 API 可用性"""
        if not self.api_url or not self.api_key:
            logger.info("向量检索未配置，将降级到关键词检索")
            self.available = False
            return

        self.available = True
        logger.info(f"向量检索已启用: {self.api_url}")

    async def get_embedding(self, text: str) -> Optional[list[float]]:
        """获取文本的向量嵌入"""
        if not self.available:
            return None

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.api_url}/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "input": text,
                        "model": self.model,
                    },
                )
                response.raise_for_status()
                data = response.json()

            return data["data"][0]["embedding"]

        except Exception as e:
            logger.error(f"向量嵌入失败: {e}")
            return None

    async def search(
        self,
        query: str,
        memories: list[dict],
        top_k: int = 20,
    ) -> list[dict]:
        """向量检索"""
        if not self.available:
            return []

        # 获取查询向量
        query_embedding = await self.get_embedding(query)
        if not query_embedding:
            return []

        # 计算相似度
        scored = []
        for mem in memories:
            if mem.get("embedding"):
                try:
                    mem_embedding = json.loads(mem["embedding"])
                    score = self._cosine_similarity(query_embedding, mem_embedding)
                    scored.append({**mem, "score": score})
                except Exception:
                    continue

        # 按相似度排序
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """计算余弦相似度"""
        import math
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

# backend/memory/manager.py
"""记忆管理器：写入/召回/维护/降级"""

import json
from datetime import datetime, timedelta
from typing import Optional

from backend.memory.store import MemoryStore
from backend.memory.vector_store import VectorStore
from backend.memory.reranker import Reranker
from backend.memory.extractor import MemoryExtractor
from backend.utils.logger import logger


class MemoryManager:
    """记忆管理器"""

    def __init__(self, config: dict, ai_engine=None):
        self.config = config
        self.store = MemoryStore()
        self.vector = VectorStore(config.get("vector", {}))
        self.reranker = Reranker(config.get("reranker", {}))
        self.extractor = MemoryExtractor(ai_engine) if ai_engine else None
        self.top_k = config.get("top_k", 20)
        self.top_n = config.get("top_n", 8)
        self.summary = ""

    async def write(self, text: str, context: str = "", game: str = "") -> bool:
        """写入记忆（三关筛选）"""
        if not self.extractor:
            logger.warning("记忆提取器未初始化，跳过写入")
            return False

        # 第一关：价值评估
        extracted = await self.extractor.extract(text, context)
        if not extracted:
            logger.debug("记忆无长期价值，丢弃")
            return False

        # 第二关：去重检测
        existing = self.store.search_by_keywords(
            extracted.get("tags", [])[:3], limit=10
        )
        if existing:
            # 检查是否重复
            for mem in existing:
                if self._is_duplicate(extracted["text"], mem["text"]):
                    logger.debug(f"记忆重复，合并: {mem['id']}")
                    self.store.update_access(mem["id"])
                    return False

            # 检查是否矛盾
            contradiction = await self.extractor.check_contradiction(
                extracted["text"], existing
            )
            if contradiction:
                contradicted_id = contradiction.get("contradicted_id")
                if contradicted_id:
                    self.store.mark_unverified(contradicted_id)
                    logger.info(f"发现矛盾记忆，标记待验证: {contradicted_id}")

        # 第三关：结构化存储
        memory = {
            "text": extracted["text"],
            "type": extracted.get("type", "general"),
            "game": game,
            "importance": extracted.get("importance", 0.5),
            "confidence": extracted.get("confidence", 0.8),
            "tags": extracted.get("tags", []),
        }

        mem_id = self.store.add(memory)
        logger.info(f"记忆已写入: {mem_id}")
        return True

    async def recall(self, query: str, game: str = "") -> list[dict]:
        """召回记忆（三阶段）"""
        # 阶段一：多路召回
        all_memories = []

        # 向量检索
        if self.vector.available:
            vector_results = await self.vector.search(
                query, self.store.get_all(), top_k=self.top_k
            )
            all_memories.extend(vector_results)

        # 关键词检索
        keywords = query.split()[:5]
        keyword_results = self.store.search_by_keywords(keywords, limit=10)
        all_memories.extend(keyword_results)

        # 时间优先
        time_results = self.store.search_by_time(limit=10)
        all_memories.extend(time_results)

        # 去重
        seen = set()
        unique = []
        for mem in all_memories:
            if mem["id"] not in seen:
                seen.add(mem["id"])
                unique.append(mem)

        if not unique:
            # 兜底：使用摘要
            if not self.summary:
                self.summary = await self._generate_summary()
            return [{"text": self.summary, "type": "summary"}] if self.summary else []

        # 阶段二：重排过滤
        if self.reranker.available and len(unique) > 1:
            documents = [m["text"] for m in unique]
            reranked = await self.reranker.rerank(query, documents, top_n=self.top_n)

            # 过滤低分
            filtered = []
            for r in reranked:
                if r.get("relevance_score", 0) >= 0.3:
                    idx = r.get("index", 0)
                    if idx < len(unique):
                        filtered.append(unique[idx])
            unique = filtered[:self.top_n]
        else:
            unique = unique[:self.top_n]

        # 更新访问记录
        for mem in unique:
            self.store.update_access(mem["id"])

        return unique

    async def maintain(self) -> None:
        """自动维护"""
        logger.info("开始记忆维护...")

        # 过期清理
        expired = self.store.get_expired()
        for mem in expired:
            self.store.delete(mem["id"])
            logger.info(f"过期记忆已删除: {mem['id']}")

        # 低频衰减（仅更新 importance，不覆盖 embedding 等字段）
        stale = self.store.get_stale(months=3)
        for mem in stale:
            new_importance = mem["importance"] * 0.8
            self.store.update_importance(mem["id"], new_importance)
            logger.info(f"低频记忆衰减: {mem['id']}")

        # 生成摘要
        self.summary = await self._generate_summary()

        stats = self.store.get_stats()
        logger.info(f"维护完成: 总计 {stats['total']} 条，活跃 {stats['active']} 条")

    def get_stats(self) -> dict:
        """获取记忆统计"""
        return self.store.get_stats()

    async def _generate_summary(self) -> str:
        """生成记忆摘要"""
        if not self.extractor:
            return ""
        memories = self.store.get_all()[:10]
        return await self.extractor.generate_summary(memories)

    def _is_duplicate(self, text1: str, text2: str) -> bool:
        """简单重复检测"""
        # 简单的文本相似度
        words1 = set(text1.split())
        words2 = set(text2.split())
        if not words1 or not words2:
            return False
        intersection = words1 & words2
        union = words1 | words2
        similarity = len(intersection) / len(union)
        return similarity > 0.7

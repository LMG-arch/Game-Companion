# backend/memory/extractor.py
"""LLM 记忆提取 + 价值评估"""

from typing import Optional

from backend.utils.logger import logger


class MemoryExtractor:
    """记忆提取器"""

    def __init__(self, ai_engine):
        self.ai_engine = ai_engine

    async def extract(self, text: str, context: str = "") -> Optional[dict]:
        """从文本中提取记忆"""
        prompt = f"""分析以下内容，判断是否值得作为长期记忆保存。

判断标准：
- 玩家偏好（喜欢用什么武器/角色/策略）
- 能力变化（技术提升/下降）
- 卡关事件（在某处反复失败）
- 重要成就（首次通关/获得稀有物品）

请用 JSON 格式回复：
{{
  "worth_saving": true/false,
  "text": "简洁的记忆描述",
  "type": "game_stuck/preference/achievement/skill_change/general",
  "importance": 0.0-1.0,
  "confidence": 0.0-1.0,
  "tags": ["标签1", "标签2"]
}}

内容：{text}
上下文：{context}"""

        try:
            result = await self.ai_engine.chat(
                messages=[{"role": "user", "content": prompt}],
            )
            if result:
                return self._parse_response(result)
        except Exception as e:
            logger.error(f"记忆提取失败: {e}")

        return None

    async def check_contradiction(self, new_text: str, existing_memories: list[dict]) -> Optional[dict]:
        """检查新记忆与现有记忆是否矛盾"""
        if not existing_memories:
            return None

        existing_texts = [m["text"] for m in existing_memories[:5]]
        prompt = f"""判断新记忆是否与现有记忆矛盾。

新记忆：{new_text}

现有记忆：
{chr(10).join(f'- {t}' for t in existing_texts)}

请用 JSON 格式回复：
{{
  "has_contradiction": true/false,
  "contradicted_memory_id": "矛盾的记忆ID（如有）",
  "reason": "原因"
}}"""

        try:
            result = await self.ai_engine.chat(
                messages=[{"role": "user", "content": prompt}],
            )
            if result:
                return self._parse_contradiction(result)
        except Exception as e:
            logger.error(f"矛盾检测失败: {e}")

        return None

    async def generate_summary(self, memories: list[dict]) -> str:
        """生成记忆摘要"""
        if not memories:
            return ""

        texts = [m["text"] for m in memories[:10]]
        prompt = f"""用 50 字以内概括以下记忆，总结对玩家的了解：

{chr(10).join(f'- {t}' for t in texts)}"""

        try:
            result = await self.ai_engine.chat(
                messages=[{"role": "user", "content": prompt}],
            )
            return result or ""
        except Exception as e:
            logger.error(f"摘要生成失败: {e}")
            return ""

    def _parse_response(self, content: str) -> Optional[dict]:
        """解析 AI 回复"""
        import json
        try:
            # 尝试提取 JSON
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(content[start:end])
                if data.get("worth_saving"):
                    return {
                        "text": data.get("text", ""),
                        "type": data.get("type", "general"),
                        "importance": min(1.0, max(0.0, data.get("importance", 0.5))),
                        "confidence": min(1.0, max(0.0, data.get("confidence", 0.8))),
                        "tags": data.get("tags", []),
                    }
        except Exception as e:
            logger.error(f"解析记忆提取结果失败: {e}")
        return None

    def _parse_contradiction(self, content: str) -> Optional[dict]:
        """解析矛盾检测结果"""
        import json
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(content[start:end])
                if data.get("has_contradiction"):
                    return {
                        "contradicted_id": data.get("contradicted_memory_id", ""),
                        "reason": data.get("reason", ""),
                    }
        except Exception as e:
            logger.error(f"解析矛盾检测结果失败: {e}")
        return None

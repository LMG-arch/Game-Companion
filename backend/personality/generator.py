# backend/personality/generator.py
"""LLM 人格生成：根据关键词生成完整人格设定"""

import json
from typing import Optional

from backend.personality.schema import create_personality
from backend.utils.logger import logger


class PersonalityGenerator:
    """人格生成器"""

    def __init__(self, ai_engine):
        self.ai_engine = ai_engine

    async def generate(self, keywords: str) -> Optional[dict]:
        """根据关键词生成人格"""
        prompt = f"""根据以下关键词，生成一个游戏伴侣的人格设定。

关键词：{keywords}

请用 JSON 格式回复，包含以下字段：
{{
  "name": "人格姓名（2-4个字）",
  "title": "称号（如：你的专属啦啦队）",
  "dimensions": {{
    "gentle_tsundere": 0.0-1.0（温柔←→傲娇）,
    "humor_serious": 0.0-1.0（幽默←→严肃）,
    "snark_kind": 0.0-1.0（毒舌←→温柔）,
    "active_calm": 0.0-1.0（活泼←→沉稳）,
    "talkative_quiet": 0.0-1.0（话多←→话少）
  }},
  "catchphrases": ["口癖1", "口癖2", "口癖3"],
  "background": "背景故事（2-3句话）",
  "danmaku_examples": ["弹幕1", "弹幕2", "弹幕3", "弹幕4", "弹幕5"],
  "system_prompt": "系统提示词（用于AI调用，描述人格特征和说话风格）"
}}"""

        try:
            result = await self.ai_engine.chat(
                messages=[{"role": "user", "content": prompt}],
            )
            if result:
                return self._parse_response(result)
        except Exception as e:
            logger.error(f"人格生成失败: {e}")

        return None

    def _parse_response(self, content: str) -> Optional[dict]:
        """解析 AI 回复"""
        try:
            # 提取 JSON
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(content[start:end])

                # 生成 ID
                import hashlib
                pid = "custom_" + hashlib.md5(
                    data.get("name", "").encode()
                ).hexdigest()[:8]

                return create_personality(
                    id=pid,
                    name=data.get("name", "未命名"),
                    title=data.get("title", ""),
                    dimensions=data.get("dimensions", {}),
                    catchphrases=data.get("catchphrases", []),
                    background=data.get("background", ""),
                    danmaku_examples=data.get("danmaku_examples", []),
                    system_prompt=data.get("system_prompt", ""),
                    is_preset=False,
                )
        except Exception as e:
            logger.error(f"解析人格生成结果失败: {e}")

        return None

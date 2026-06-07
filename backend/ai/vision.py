# backend/ai/vision.py
"""视觉理解模块：截图→文本描述→场景判断"""

import random
from backend.utils.logger import logger


# 场景类型


# 场景类型
SCENE_TYPES = {
    "combat": "战斗",
    "exploration": "探索",
    "menu": "菜单",
    "stuck": "卡关",
    "death": "死亡",
    "idle": "空闲",
    "unknown": "未知",
}

# 场景判断提示词
SCENE_PROMPT = """你是一个游戏场景分析助手。请分析这张游戏截图，判断当前场景类型。

请按以下格式回复：
场景: [场景类型]
描述: [简短描述当前画面]
建议: [如果适用，给出游戏建议]

场景类型必须是以下之一：
- combat（战斗中）
- exploration（探索中）
- menu（在菜单界面）
- stuck（卡关/反复失败）
- death（角色死亡）
- idle（空闲/暂停）"""


def get_scene_prompt() -> str:
    """获取场景分析提示词"""
    return SCENE_PROMPT


def get_danmaku_hint(scene: str, description: str) -> str:
    """根据场景生成弹幕提示"""
    hints = {
        "combat": [
            "加油！你可以的！",
            "注意闪避！",
            "集中火力！",
            "稳住，别慌！",
        ],
        "exploration": [
            "继续探索吧~",
            "看看那边有什么！",
            "慢慢来，不着急~",
        ],
        "menu": [
            "整理装备呢~",
            "准备好了吗？",
        ],
        "stuck": [
            "别灰心，再试一次！",
            "换个思路试试？",
            "休息一下再回来~",
        ],
        "death": [
            "没关系，再来一次！",
            "下次一定可以的！",
            "失败是成功之母~",
        ],
        "idle": [
            "在休息呢~",
            "准备好继续了吗？",
        ],
    }

    import random
    scene_hints = hints.get(scene, ["加油！"])
    return random.choice(scene_hints)

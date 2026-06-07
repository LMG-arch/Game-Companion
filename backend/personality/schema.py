# backend/personality/schema.py
"""人格 JSON 结构定义"""

# 人格数据结构
PERSONALITY_SCHEMA = {
    "id": "str",           # 唯一标识
    "name": "str",         # 姓名
    "title": "str",        # 称号
    "avatar": "str|null",  # 头像 URL
    "dimensions": {        # 性格维度 (0.0-1.0)
        "gentle_tsundere": 0.5,   # 温柔←→傲娇
        "humor_serious": 0.5,     # 幽默←→严肃
        "snark_kind": 0.5,        # 毒舌←→温柔
        "active_calm": 0.5,       # 活泼←→沉稳
        "talkative_quiet": 0.5,   # 话多←→话少
    },
    "catchphrases": [],    # 口癖列表
    "background": "",      # 背景故事
    "danmaku_examples": [],# 弹幕示例
    "system_prompt": "",   # 系统提示词
    "is_preset": False,    # 是否预设
}


def create_personality(
    id: str,
    name: str,
    title: str,
    dimensions: dict,
    catchphrases: list,
    background: str,
    danmaku_examples: list,
    system_prompt: str,
    is_preset: bool = False,
) -> dict:
    """创建人格数据"""
    return {
        "id": id,
        "name": name,
        "title": title,
        "avatar": None,
        "dimensions": {
            "gentle_tsundere": max(0.0, min(1.0, dimensions.get("gentle_tsundere", 0.5))),
            "humor_serious": max(0.0, min(1.0, dimensions.get("humor_serious", 0.5))),
            "snark_kind": max(0.0, min(1.0, dimensions.get("snark_kind", 0.5))),
            "active_calm": max(0.0, min(1.0, dimensions.get("active_calm", 0.5))),
            "talkative_quiet": max(0.0, min(1.0, dimensions.get("talkative_quiet", 0.5))),
        },
        "catchphrases": catchphrases,
        "background": background,
        "danmaku_examples": danmaku_examples,
        "system_prompt": system_prompt,
        "is_preset": is_preset,
    }

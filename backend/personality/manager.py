# backend/personality/manager.py
"""人格管理器：加载/切换/持久化"""

import json
from pathlib import Path
from typing import Optional

from backend.personality.presets import get_preset, get_all_presets
from backend.personality.schema import create_personality
from backend.utils.logger import logger


class PersonalityManager:
    """人格管理器"""

    def __init__(self, config: dict):
        self.config = config
        self.data_dir = Path.home() / "AppData" / "Roaming" / "游戏伴侣" / "personalities"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.active_id = config.get("active", "preset_soft")
        self.active_personality = None
        self._load_active()

    def _load_active(self) -> None:
        """加载当前活跃人格"""
        # 先尝试加载自定义人格
        custom_path = self.data_dir / f"{self.active_id}.json"
        if custom_path.exists():
            try:
                with open(custom_path, "r", encoding="utf-8") as f:
                    self.active_personality = json.load(f)
                logger.info(f"已加载自定义人格: {self.active_id}")
                return
            except Exception as e:
                logger.error(f"加载自定义人格失败: {e}")

        # 尝试加载预设人格
        preset = get_preset(self.active_id)
        if preset:
            self.active_personality = preset
            logger.info(f"已加载预设人格: {preset['name']}")
            return

        # 默认使用软萌甜心
        self.active_personality = get_preset("preset_soft")
        logger.info("使用默认人格: 软萌甜心")

    def get_active(self) -> dict:
        """获取当前活跃人格"""
        return self.active_personality or get_preset("preset_soft")

    def get_system_prompt(self) -> str:
        """获取当前人格的系统提示词"""
        personality = self.get_active()
        return personality.get("system_prompt", "")

    def switch(self, personality_id: str) -> bool:
        """切换人格"""
        # 检查预设
        preset = get_preset(personality_id)
        if preset:
            self.active_personality = preset
            self.active_id = personality_id
            self._save_config()
            logger.info(f"已切换到预设人格: {preset['name']}")
            return True

        # 检查自定义
        custom_path = self.data_dir / f"{personality_id}.json"
        if custom_path.exists():
            try:
                with open(custom_path, "r", encoding="utf-8") as f:
                    self.active_personality = json.load(f)
                self.active_id = personality_id
                self._save_config()
                logger.info(f"已切换到自定义人格: {personality_id}")
                return True
            except Exception as e:
                logger.error(f"加载自定义人格失败: {e}")

        logger.error(f"人格不存在: {personality_id}")
        return False

    def save_custom(self, personality: dict) -> bool:
        """保存自定义人格"""
        pid = personality.get("id", "")
        if not pid:
            logger.error("人格 ID 不能为空")
            return False

        # 不允许覆盖预设
        if pid.startswith("preset_"):
            logger.error("不能覆盖预设人格")
            return False

        custom_path = self.data_dir / f"{pid}.json"
        try:
            with open(custom_path, "w", encoding="utf-8") as f:
                json.dump(personality, f, ensure_ascii=False, indent=2)
            logger.info(f"自定义人格已保存: {pid}")
            return True
        except Exception as e:
            logger.error(f"保存人格失败: {e}")
            return False

    def delete_custom(self, personality_id: str) -> bool:
        """删除自定义人格"""
        if personality_id.startswith("preset_"):
            logger.error("不能删除预设人格")
            return False

        custom_path = self.data_dir / f"{personality_id}.json"
        if custom_path.exists():
            custom_path.unlink()
            logger.info(f"自定义人格已删除: {personality_id}")
            return True
        return False

    def list_all(self) -> list[dict]:
        """列出所有可用人格"""
        result = []

        # 预设人格
        for pid, preset in get_all_presets().items():
            result.append({
                "id": pid,
                "name": preset["name"],
                "title": preset["title"],
                "is_preset": True,
            })

        # 自定义人格
        for f in self.data_dir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                result.append({
                    "id": data.get("id", f.stem),
                    "name": data.get("name", "未命名"),
                    "title": data.get("title", ""),
                    "is_preset": False,
                })
            except Exception:
                continue

        return result

    def _save_config(self) -> None:
        """保存当前选择到配置"""
        from backend.core.config import config
        config.set("personality.active", self.active_id)
        config.save()

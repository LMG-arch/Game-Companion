# backend/utils/logger.py
"""日志模块：统一日志格式和输出"""

import logging
import sys
from pathlib import Path


def setup_logger(name: str = "game-companion") -> logging.Logger:
    """创建并配置日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 控制台输出（Windows 下强制 UTF-8）
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)

    # 文件输出
    log_dir = Path.home() / "AppData" / "Roaming" / "游戏伴侣" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "game-companion.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] %(levelname)s %(name)s:%(lineno)d: %(message)s"
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 全局日志器
logger = setup_logger()

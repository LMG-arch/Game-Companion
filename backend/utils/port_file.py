# backend/utils/port_file.py
"""端口发现：将 WebSocket 服务器端口号写入临时文件"""

import os
from pathlib import Path

from backend.utils.logger import logger

# 端口文件路径
PORT_FILE = Path(os.environ.get("TEMP", "/tmp")) / "game-companion-port.txt"


def write_port(port: int) -> None:
    """将端口号写入临时文件"""
    try:
        PORT_FILE.write_text(str(port), encoding="utf-8")
        logger.info(f"端口号已写入: {PORT_FILE} -> {port}")
    except IOError as e:
        logger.error(f"写入端口文件失败: {e}")
        raise


def read_port() -> int | None:
    """从临时文件读取端口号"""
    try:
        if PORT_FILE.exists():
            port = int(PORT_FILE.read_text(encoding="utf-8").strip())
            logger.info(f"读取端口号: {port}")
            return port
        return None
    except (IOError, ValueError) as e:
        logger.error(f"读取端口文件失败: {e}")
        return None


def cleanup_port() -> None:
    """清理端口文件"""
    try:
        if PORT_FILE.exists():
            PORT_FILE.unlink()
            logger.info("端口文件已清理")
    except IOError as e:
        logger.error(f"清理端口文件失败: {e}")

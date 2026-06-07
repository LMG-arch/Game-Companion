# backend/main.py
"""Python 后端入口：启动 WebSocket 服务器"""

import asyncio
import signal
import sys

from backend.core.websocket_server import WebSocketServer
from backend.core.config import config
from backend.utils.port_file import write_port, cleanup_port
from backend.utils.logger import logger


async def main():
    """主函数"""
    logger.info("游戏伴侣后端启动中...")

    # 创建 WebSocket 服务器
    server = WebSocketServer()

    # 注册消息处理器（后续阶段扩展）
    def handle_question(payload: dict) -> dict:
        """处理用户提问（占位）"""
        return {"answer": "功能开发中...", "sources": []}

    server.on("question.ask", handle_question)

    # 启动服务器
    port = await server.start()

    # 写入端口文件
    write_port(port)

    logger.info("后端已就绪，等待前端连接...")

    # 等待关闭信号
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("收到关闭信号")
        stop_event.set()

    # Windows 下使用 SIGINT
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Windows 不支持 add_signal_handler
            pass

    # 等待关闭或 Ctrl+C
    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("收到 Ctrl+C")

    # 清理
    await server.stop()
    cleanup_port()
    logger.info("后端已关闭")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

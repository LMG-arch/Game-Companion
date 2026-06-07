# backend/main.py
"""Python 后端入口：启动 WebSocket 服务器 + 屏幕捕获 + AI 分析"""

import asyncio
import signal

from backend.core.websocket_server import WebSocketServer
from backend.core.config import config
from backend.screen.capturer import ScreenCapturer
from backend.ai.engine import AIEngine
from backend.ai.vision import get_scene_prompt, get_danmaku_hint
from backend.utils.port_file import write_port, cleanup_port
from backend.utils.logger import logger


async def main():
    """主函数"""
    logger.info("游戏伴侣后端启动中...")

    # 加载配置
    ai_config = config.get("ai", {})
    game_config = config.get("game", {})

    # 创建 AI 引擎
    ai_engine = AIEngine(ai_config)

    # 创建 WebSocket 服务器
    server = WebSocketServer()

    # 注册消息处理器
    def handle_question(payload: dict) -> dict:
        """处理用户提问"""
        return {"answer": "功能开发中...", "sources": []}

    server.on("question.ask", handle_question)

    # 帧回调：发送到 AI 分析
    async def on_frame(jpeg_bytes: bytes):
        """截图帧回调"""
        try:
            result = await ai_engine.analyze_image(
                jpeg_bytes,
                system_prompt=get_scene_prompt(),
            )
            if result:
                scene = result.get("scene", "unknown")
                description = result.get("description", "")
                suggestion = result.get("suggestion", "")

                # 生成弹幕提示
                danmaku_hint = get_danmaku_hint(scene, description)

                # 广播分析结果到前端
                await server.send("screen.analyzed", {
                    "scene": scene,
                    "confidence": 0.8,
                    "description": description,
                    "suggestion": suggestion,
                    "danmaku_hint": danmaku_hint,
                })

                # 发送弹幕
                await server.send("danmaku.send", {
                    "text": danmaku_hint,
                    "priority": "normal",
                    "style": "encouragement",
                })

        except Exception as e:
            logger.error(f"AI 分析失败: {e}")

    # 创建屏幕捕获器
    capturer = ScreenCapturer(
        on_frame=on_frame,
        fps=game_config.get("capture_fps", 1.0),
        silent_fps=game_config.get("silent_fps", 0.2),
        silent_threshold=game_config.get("silent_threshold", 5),
    )

    # 启动服务器
    port = await server.start()
    write_port(port)

    # 启动截图循环（后台任务）
    capture_task = asyncio.create_task(capturer.start())

    logger.info("后端已就绪，等待前端连接...")

    # 等待关闭信号
    stop_event = asyncio.Event()

    def signal_handler():
        logger.info("收到关闭信号")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            pass

    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("收到 Ctrl+C")

    # 清理
    await capturer.stop()
    capture_task.cancel()
    await server.stop()
    cleanup_port()
    logger.info("后端已关闭")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

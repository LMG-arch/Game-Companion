# backend/main.py
"""Python 后端入口：启动 WebSocket 服务器 + 屏幕捕获 + AI 分析 + 记忆系统 + 人格系统 + 弹幕引擎 + 搜索系统"""

import asyncio
import signal
import sys
import time

from backend.core.websocket_server import WebSocketServer
from backend.core.config import config
from backend.screen.capturer import ScreenCapturer
from backend.ai.engine import AIEngine
from backend.ai.vision import get_scene_prompt, get_danmaku_hint
from backend.memory.manager import MemoryManager
from backend.personality.manager import PersonalityManager
from backend.personality.generator import PersonalityGenerator
from backend.danmaku.history import DanmakuHistory
from backend.search.engine import SearchEngine
from backend.utils.port_file import write_port, cleanup_port
from backend.utils.logger import logger


async def main():
    """主函数"""
    logger.info("游戏伴侣后端启动中...")

    # 加载配置
    ai_config = config.get("ai", {})
    game_config = config.get("game", {})
    memory_config = config.get("memory", {})
    personality_config = config.get("personality", {})
    search_config = config.get("search", {})

    # 创建 AI 引擎
    ai_engine = AIEngine(ai_config)

    # 创建记忆管理器
    memory_manager = MemoryManager(memory_config, ai_engine)

    # 创建人格管理器
    personality_manager = PersonalityManager(personality_config)
    personality_generator = PersonalityGenerator(ai_engine)

    # 创建弹幕历史
    danmaku_history = DanmakuHistory()

    # 创建搜索引擎
    search_engine = SearchEngine(search_config)

    # 启动时执行记忆维护
    await memory_manager.maintain()

    # 创建 WebSocket 服务器
    server = WebSocketServer()

    # 注册消息处理器
    async def handle_question(payload: dict) -> dict:
        """处理用户提问（搜索 + AI 回答）"""
        text = payload.get("text", "")

        # 搜索相关攻略
        search_results = await search_engine.search(text, limit=3)

        # 构建上下文
        context = ""
        if search_results:
            context = "搜索结果:\n"
            for r in search_results:
                context += f"- {r['title']}: {r['snippet']}\n"

        # AI 回答
        answer = await ai_engine.chat(
            messages=[{"role": "user", "content": f"问题: {text}\n\n{context}\n\n请根据以上信息回答问题。"}],
            system_prompt=personality_manager.get_system_prompt(),
        )

        return {
            "answer": answer or "抱歉，我暂时无法回答这个问题。",
            "sources": search_results,
        }

    server.on("question.ask", handle_question)

    # 人格列表处理器
    def handle_personality_list(payload: dict) -> dict:
        """获取人格列表"""
        return {
            "list": personality_manager.list_all(),
            "active_id": personality_manager.active_id,
        }

    server.on("personality.list", handle_personality_list)

    # 人格切换处理器
    def handle_personality_switch(payload: dict) -> dict:
        """切换人格"""
        pid = payload.get("id", "")
        success = personality_manager.switch(pid)
        return {"success": success, "active_id": personality_manager.active_id}

    server.on("personality.switch", handle_personality_switch)

    # 人格生成处理器
    async def handle_personality_generate(payload: dict) -> dict:
        """生成人格"""
        keywords = payload.get("keywords", "")
        result = await personality_generator.generate(keywords)
        if result:
            personality_manager.save_custom(result)
            return {"success": True, "personality": result}
        return {"success": False, "error": "生成失败"}

    server.on("personality.generate", handle_personality_generate)

    # 设置获取处理器
    def handle_settings_get(payload: dict) -> dict:
        """获取配置"""
        return config.data

    server.on("settings.get", handle_settings_get)

    # AI 状态处理器
    def handle_ai_status(payload: dict) -> dict:
        """获取 AI 状态"""
        return ai_engine.get_status()

    server.on("ai.status", handle_ai_status)

    # 设置保存处理器
    def handle_settings_save(payload: dict) -> dict:
        """保存配置"""
        new_config = payload.get("config", {})

        # 深度合并配置
        def deep_merge(base: dict, update: dict) -> dict:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        # 合并到当前配置
        current = config.data
        deep_merge(current, new_config)
        config.save()
        return {"success": True}

    server.on("settings.save", handle_settings_save)

    # 记忆测试处理器
    async def handle_memory_test(payload: dict) -> dict:
        """处理记忆检索测试"""
        query = payload.get("query", "")
        results = await memory_manager.recall(query)
        stats = memory_manager.get_stats()
        return {
            "query": query,
            "results": results,
            "stats": stats,
        }

    server.on("memory.test", handle_memory_test)

    # 帧回调：发送到 AI 分析
    last_memory_write = 0  # 上次记忆写入时间

    async def on_frame(jpeg_bytes: bytes):
        """截图帧回调"""
        nonlocal last_memory_write
        # 检查 AI 是否可用
        if not ai_engine.is_available():
            return

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

                # 保存弹幕历史
                danmaku_history.add(
                    text=danmaku_hint,
                    priority="normal",
                    style="encouragement",
                    scene=scene,
                    personality_id=personality_manager.active_id,
                )

                # 记录到记忆系统（限制频率，每 30 秒最多一次）
                now = time.time()
                if now - last_memory_write >= 30:
                    last_memory_write = now
                    await memory_manager.write(
                        text=f"场景: {scene}, {description}",
                        context=suggestion,
                        game="",
                    )

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

    # 监听 stdin 的 shutdown 命令（Windows 兼容）
    async def watch_stdin():
        while not stop_event.is_set():
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line or 'shutdown' in line.strip().lower():
                    logger.info("收到 stdin shutdown 命令或 stdin 关闭")
                    stop_event.set()
                    break
            except Exception:
                break

    stdin_task = asyncio.create_task(watch_stdin())

    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        logger.info("收到 Ctrl+C")

    stdin_task.cancel()

    # 清理
    await capturer.stop()
    capture_task.cancel()
    memory_manager.store.close()
    danmaku_history.cleanup()
    danmaku_history.close()
    await server.stop()
    cleanup_port()
    logger.info("后端已关闭")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

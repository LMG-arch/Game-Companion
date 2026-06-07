# backend/core/websocket_server.py
"""WebSocket 服务器：消息收发、路由"""

import asyncio
import json
from typing import Callable, Any

import websockets
from websockets.server import serve, WebSocketServerProtocol

from backend.utils.logger import logger


# 消息处理器类型
MessageHandler = Callable[[dict], dict | None]


class WebSocketServer:
    """WebSocket 服务器"""

    def __init__(self, host: str = "localhost"):
        self.host = host
        self.port: int = 0
        self.server = None
        self.clients: set[WebSocketServerProtocol] = set()
        self.handlers: dict[str, MessageHandler] = {}

    def on(self, message_type: str, handler: MessageHandler) -> None:
        """注册消息处理器"""
        self.handlers[message_type] = handler

    async def _handle_connection(self, websocket: WebSocketServerProtocol) -> None:
        """处理单个客户端连接"""
        self.clients.add(websocket)
        logger.info(f"客户端已连接，当前连接数: {len(self.clients)}")

        try:
            async for raw_message in websocket:
                try:
                    message = json.loads(raw_message)
                    logger.debug(f"收到消息: {message.get('type')}")

                    # 调用对应的处理器
                    response = await self._dispatch(message)
                    if response:
                        await websocket.send(json.dumps(response, ensure_ascii=False))

                except json.JSONDecodeError:
                    logger.error(f"无效的 JSON 消息: {raw_message}")
                except Exception as e:
                    logger.error(f"处理消息时出错: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("客户端断开连接")
        finally:
            self.clients.discard(websocket)
            logger.info(f"客户端已断开，当前连接数: {len(self.clients)}")

    async def _dispatch(self, message: dict) -> dict | None:
        """分发消息到对应的处理器"""
        msg_type = message.get("type")
        msg_id = message.get("id", "")

        if msg_type == "ping":
            return {"type": "pong", "id": msg_id, "payload": {}}

        handler = self.handlers.get(msg_type)
        if handler:
            try:
                result = handler(message.get("payload", {}))
                if result:
                    return {"type": f"{msg_type}.result", "id": msg_id, "payload": result}
            except Exception as e:
                logger.error(f"处理器 {msg_type} 出错: {e}")
                return {
                    "type": "error",
                    "id": msg_id,
                    "payload": {"code": "HANDLER_ERROR", "message": str(e)}
                }
        else:
            logger.warning(f"未知消息类型: {msg_type}")
            return {
                "type": "error",
                "id": msg_id,
                "payload": {"code": "UNKNOWN_TYPE", "message": f"未知消息类型: {msg_type}"}
            }

    async def send(self, message_type: str, payload: dict, msg_id: str = "") -> None:
        """向所有客户端广播消息"""
        message = json.dumps(
            {"type": message_type, "id": msg_id, "payload": payload},
            ensure_ascii=False
        )
        for client in self.clients.copy():
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                self.clients.discard(client)

    async def start(self) -> int:
        """启动服务器，返回端口号"""
        self.server = await serve(
            self._handle_connection,
            self.host,
            0  # 随机端口
        )
        # 获取实际端口号
        self.port = self.server.sockets[0].getsockname()[1]
        logger.info(f"WebSocket 服务器已启动: ws://{self.host}:{self.port}")
        return self.port

    async def stop(self) -> None:
        """停止服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket 服务器已停止")

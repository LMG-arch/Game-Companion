# backend/screen/capturer.py
"""屏幕捕获模块：dxcam 截图 + GDI 备用方案 + 变化检测 + 静默降频"""

import asyncio
import hashlib
import io
import time
from typing import Callable, Awaitable, Optional

import numpy as np
from PIL import Image, ImageGrab

from backend.utils.logger import logger


class ScreenCapturer:
    """屏幕捕获器"""

    def __init__(
        self,
        on_frame: Callable[[bytes], Awaitable[None]],
        fps: float = 1.0,
        silent_fps: float = 0.2,
        silent_threshold: int = 5,
    ):
        self.on_frame = on_frame
        self.fps = fps
        self.silent_fps = silent_fps
        self.silent_threshold = silent_threshold

        self._camera = None
        self._use_gdi = False  # 是否使用 GDI 备用方案
        self._running = False
        self._last_hash: Optional[str] = None
        self._unchanged_count = 0
        self._silent_mode = False

    async def start(self) -> None:
        """启动截图循环"""
        # 尝试初始化 dxcam
        try:
            import dxcam
            self._camera = dxcam.create(output_color="BGR")
            logger.info("屏幕捕获已初始化（dxcam/DXGI）")
        except Exception as e:
            logger.warning(f"dxcam 初始化失败: {e}")
            logger.info("切换到 GDI 备用方案（性能较低）")
            self._use_gdi = True

        self._running = True
        fps = self.silent_fps if self._silent_mode else self.fps
        logger.info(f"截图循环启动: {fps} FPS")

        while self._running:
            try:
                await self._capture_frame()
            except Exception as e:
                logger.error(f"截图异常: {e}")

            # 计算等待时间
            current_fps = self.silent_fps if self._silent_mode else self.fps
            wait_time = 1.0 / current_fps if current_fps > 0 else 1.0
            await asyncio.sleep(wait_time)

    async def stop(self) -> None:
        """停止截图循环"""
        self._running = False
        self._camera = None
        logger.info("截图循环已停止")

    async def _capture_frame(self) -> None:
        """捕获一帧"""
        try:
            if self._use_gdi:
                frame = self._capture_gdi()
            else:
                frame = self._capture_dxcam()

            if frame is None:
                return

            # 计算帧哈希
            frame_hash = self._compute_hash(frame)

            # 变化检测
            if frame_hash == self._last_hash:
                self._unchanged_count += 1
                if not self._silent_mode and self._unchanged_count >= self.silent_threshold:
                    self._silent_mode = True
                    logger.info(f"进入静默模式: {self.silent_fps} FPS")
                return
            else:
                if self._silent_mode:
                    self._silent_mode = False
                    logger.info(f"退出静默模式: {self.fps} FPS")
                self._unchanged_count = 0
                self._last_hash = frame_hash

            # 转换为 JPEG 字节
            jpeg_bytes = self._frame_to_jpeg(frame)

            # 调用回调
            await self.on_frame(jpeg_bytes)

        except Exception as e:
            logger.error(f"帧捕获失败: {e}")

    def _capture_dxcam(self):
        """使用 dxcam 截图"""
        if not self._camera:
            return None
        return self._camera.grab()

    def _capture_gdi(self):
        """使用 PIL GDI 截图（备用方案）"""
        try:
            screenshot = ImageGrab.grab()
            # PIL.Image -> numpy array (BGR)
            frame = np.array(screenshot)
            # RGB -> BGR
            frame = frame[:, :, ::-1].copy()
            return frame
        except Exception as e:
            logger.error(f"GDI 截图失败: {e}")
            return None

    def _compute_hash(self, frame) -> str:
        """计算帧哈希（降采样加速）"""
        # 降采样到 1/4 分辨率
        small = frame[::4, ::4]
        return hashlib.md5(small.tobytes()).hexdigest()

    def _frame_to_jpeg(self, frame) -> bytes:
        """将帧转换为 JPEG 字节"""
        # BGR -> RGB
        rgb_frame = frame[:, :, ::-1]
        img = Image.fromarray(rgb_frame)

        # 压缩为 JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        return buffer.getvalue()

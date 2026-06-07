# backend/danmaku/history.py
"""弹幕历史记录"""

import json
import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime

from backend.utils.logger import logger


class DanmakuHistory:
    """弹幕历史"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (
            Path.home() / "AppData" / "Roaming" / "游戏伴侣" / "danmaku_history.db"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库表"""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS danmaku_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                priority TEXT DEFAULT 'normal',
                style TEXT DEFAULT 'encouragement',
                scene TEXT DEFAULT '',
                personality_id TEXT DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_history_created ON danmaku_history(created_at);
            CREATE INDEX IF NOT EXISTS idx_history_scene ON danmaku_history(scene);
        """)
        self.conn.commit()

    def add(self, text: str, priority: str = 'normal', style: str = 'encouragement',
            scene: str = '', personality_id: str = '') -> None:
        """添加弹幕记录"""
        now = datetime.now().isoformat()
        self.conn.execute("""
            INSERT INTO danmaku_history (text, priority, style, scene, personality_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (text, priority, style, scene, personality_id, now))
        self.conn.commit()

    def get_recent(self, limit: int = 50) -> list[dict]:
        """获取最近的弹幕"""
        rows = self.conn.execute("""
            SELECT * FROM danmaku_history
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]

    def get_by_scene(self, scene: str, limit: int = 20) -> list[dict]:
        """按场景获取弹幕"""
        rows = self.conn.execute("""
            SELECT * FROM danmaku_history
            WHERE scene = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (scene, limit)).fetchall()
        return [dict(row) for row in rows]

    def get_stats(self) -> dict:
        """获取统计信息"""
        total = self.conn.execute("SELECT COUNT(*) FROM danmaku_history").fetchone()[0]
        scenes = self.conn.execute("""
            SELECT scene, COUNT(*) as count
            FROM danmaku_history
            GROUP BY scene
            ORDER BY count DESC
        """).fetchall()

        return {
            "total": total,
            "scenes": {row["scene"]: row["count"] for row in scenes},
        }

    def cleanup(self, keep_count: int = 1000) -> None:
        """清理旧记录，保留最近 N 条"""
        self.conn.execute("""
            DELETE FROM danmaku_history
            WHERE id NOT IN (
                SELECT id FROM danmaku_history
                ORDER BY created_at DESC
                LIMIT ?
            )
        """, (keep_count,))
        self.conn.commit()

    def close(self) -> None:
        """关闭数据库连接"""
        self.conn.close()

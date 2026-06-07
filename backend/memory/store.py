# backend/memory/store.py
"""SQLite 存储层：记忆数据持久化"""

import json
import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime

from backend.utils.logger import logger


class MemoryStore:
    """记忆存储"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (
            Path.home() / "AppData" / "Roaming" / "游戏伴侣" / "memory" / "raw_memory.db"
        )
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库表"""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                type TEXT DEFAULT 'general',
                game TEXT DEFAULT '',
                importance REAL DEFAULT 0.5,
                confidence REAL DEFAULT 0.8,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                expire_at TEXT,
                verified INTEGER DEFAULT 1,
                tags TEXT DEFAULT '[]',
                embedding TEXT DEFAULT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
            CREATE INDEX IF NOT EXISTS idx_memories_game ON memories(game);
            CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance);
            CREATE INDEX IF NOT EXISTS idx_memories_created ON memories(created_at);
        """)
        self.conn.commit()
        logger.info(f"记忆数据库已初始化: {self.db_path}")

    def add(self, memory: dict) -> str:
        """添加记忆"""
        mem_id = memory.get("id", f"mem_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        now = datetime.now().isoformat()

        self.conn.execute("""
            INSERT OR REPLACE INTO memories
            (id, text, type, game, importance, confidence, created_at, last_accessed, access_count, expire_at, verified, tags, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mem_id,
            memory.get("text", ""),
            memory.get("type", "general"),
            memory.get("game", ""),
            memory.get("importance", 0.5),
            memory.get("confidence", 0.8),
            memory.get("created_at", now),
            memory.get("last_accessed", now),
            memory.get("access_count", 0),
            memory.get("expire_at"),
            1 if memory.get("verified", True) else 0,
            json.dumps(memory.get("tags", []), ensure_ascii=False),
            memory.get("embedding"),
        ))
        self.conn.commit()
        return mem_id

    def get(self, mem_id: str) -> Optional[dict]:
        """获取记忆"""
        row = self.conn.execute("SELECT * FROM memories WHERE id = ?", (mem_id,)).fetchone()
        if row:
            return self._row_to_dict(row)
        return None

    def search_by_keywords(self, keywords: list[str], limit: int = 10) -> list[dict]:
        """关键词搜索"""
        conditions = " OR ".join(["text LIKE ?" for _ in keywords])
        params = [f"%{kw}%" for kw in keywords]
        params.append(limit)

        rows = self.conn.execute(f"""
            SELECT * FROM memories
            WHERE {conditions}
            ORDER BY importance DESC, last_accessed DESC
            LIMIT ?
        """, params).fetchall()

        return [self._row_to_dict(row) for row in rows]

    def search_by_time(self, limit: int = 10) -> list[dict]:
        """按时间优先搜索"""
        rows = self.conn.execute("""
            SELECT * FROM memories
            WHERE verified = 1
            ORDER BY last_accessed DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [self._row_to_dict(row) for row in rows]

    def get_all(self, verified_only: bool = True) -> list[dict]:
        """获取所有记忆"""
        if verified_only:
            rows = self.conn.execute("SELECT * FROM memories WHERE verified = 1").fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM memories").fetchall()
        return [self._row_to_dict(row) for row in rows]

    def update_access(self, mem_id: str) -> None:
        """更新访问记录"""
        now = datetime.now().isoformat()
        self.conn.execute("""
            UPDATE memories
            SET last_accessed = ?, access_count = access_count + 1
            WHERE id = ?
        """, (now, mem_id))
        self.conn.commit()

    def mark_unverified(self, mem_id: str) -> None:
        """标记为待验证"""
        self.conn.execute("UPDATE memories SET verified = 0 WHERE id = ?", (mem_id,))
        self.conn.commit()

    def delete(self, mem_id: str) -> None:
        """删除记忆"""
        self.conn.execute("DELETE FROM memories WHERE id = ?", (mem_id,))
        self.conn.commit()

    def get_expired(self) -> list[dict]:
        """获取过期记忆"""
        now = datetime.now().isoformat()
        rows = self.conn.execute("""
            SELECT * FROM memories WHERE expire_at IS NOT NULL AND expire_at < ?
        """, (now,)).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_stale(self, months: int = 3) -> list[dict]:
        """获取长期未访问的记忆"""
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=months * 30)).isoformat()
        rows = self.conn.execute("""
            SELECT * FROM memories WHERE last_accessed < ? AND verified = 1
        """, (cutoff,)).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_stats(self) -> dict:
        """获取统计信息"""
        total = self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        active = self.conn.execute("SELECT COUNT(*) FROM memories WHERE verified = 1").fetchone()[0]
        unverified = self.conn.execute("SELECT COUNT(*) FROM memories WHERE verified = 0").fetchone()[0]

        return {
            "total": total,
            "active": active,
            "unverified": unverified,
        }

    def _row_to_dict(self, row) -> dict:
        """将数据库行转为字典"""
        return {
            "id": row["id"],
            "text": row["text"],
            "type": row["type"],
            "game": row["game"],
            "importance": row["importance"],
            "confidence": row["confidence"],
            "created_at": row["created_at"],
            "last_accessed": row["last_accessed"],
            "access_count": row["access_count"],
            "expire_at": row["expire_at"],
            "verified": bool(row["verified"]),
            "tags": json.loads(row["tags"]) if row["tags"] else [],
        }

    def close(self) -> None:
        """关闭数据库连接"""
        self.conn.close()

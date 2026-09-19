"""
Memory Service - Redis buffer + SQLite persistent storage
Pattern from customer-support-chatbot:
  - Redis buffer (TTL: 1h)  → Recent messages
  - Redis summary (TTL: 24h) → Compressed context
  - SQLite                   → Full persistent history
"""
import sqlite3
import json
import logging
import os
import time
from typing import List, Dict, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client = None
REDIS_AVAILABLE = False
_REDIS_RETRY_AFTER_SECONDS = 60.0
_next_redis_retry_at = 0.0


def _connect_redis(max_attempts: int = 5, initial_delay: float = 1.0):
    """Best-effort Redis connection with retries to avoid startup races."""
    try:
        import redis
    except Exception as e:
        logger.warning("Redis package not available, using SQLite-only mode: %s", e)
        return None

    delay = initial_delay
    last_error: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        try:
            client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
            )
            client.ping()
            logger.info("Redis connected successfully on attempt %s.", attempt)
            return client
        except Exception as e:
            last_error = e
            if attempt < max_attempts:
                time.sleep(delay)
                delay = min(delay * 2, 5.0)

    logger.warning("Redis not available, falling back to SQLite-only mode: %s", last_error)
    return None


def _refresh_redis_state():
    global _redis_client, REDIS_AVAILABLE, _next_redis_retry_at
    if REDIS_AVAILABLE or _redis_client is not None:
        return

    now = time.time()
    if now < _next_redis_retry_at:
        return

    _redis_client = _connect_redis()
    REDIS_AVAILABLE = _redis_client is not None
    if not REDIS_AVAILABLE:
        _next_redis_retry_at = now + _REDIS_RETRY_AFTER_SECONDS


_refresh_redis_state()


class MemoryService:
    def __init__(self):
        db_dir = os.path.dirname(settings.SQLITE_DB_PATH)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.db_path = settings.SQLITE_DB_PATH
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON chat_history(session_id)")
            conn.commit()

    # ── Redis helpers ──────────────────────────────────────────────────────────

    def _buffer_key(self, session_id: str) -> str:
        return f"session:{session_id}:buffer"

    def _summary_key(self, session_id: str) -> str:
        return f"session:{session_id}:summary"

    def _get_redis_buffer(self, session_id: str) -> List[Dict]:
        _refresh_redis_state()
        if not REDIS_AVAILABLE:
            return []
        try:
            raw = _redis_client.lrange(self._buffer_key(session_id), 0, -1)
            return [json.loads(m) for m in raw]
        except Exception as e:
            logger.error(f"Redis get_buffer error: {e}")
            return []

    def _append_redis_buffer(self, session_id: str, role: str, content: str):
        _refresh_redis_state()
        if not REDIS_AVAILABLE:
            return
        try:
            key = self._buffer_key(session_id)
            msg = json.dumps({"role": role, "content": content})
            _redis_client.rpush(key, msg)
            _redis_client.expire(key, settings.REDIS_BUFFER_TTL)
        except Exception as e:
            logger.error(f"Redis append_buffer error: {e}")

    def _get_redis_summary(self, session_id: str) -> Optional[str]:
        _refresh_redis_state()
        if not REDIS_AVAILABLE:
            return None
        try:
            return _redis_client.get(self._summary_key(session_id))
        except Exception as e:
            logger.error(f"Redis get_summary error: {e}")
            return None

    def _set_redis_summary(self, session_id: str, summary: str):
        _refresh_redis_state()
        if not REDIS_AVAILABLE:
            return
        try:
            key = self._summary_key(session_id)
            _redis_client.set(key, summary, ex=settings.REDIS_SUMMARY_TTL)
        except Exception as e:
            logger.error(f"Redis set_summary error: {e}")

    def _trim_redis_buffer(self, session_id: str, keep_last: int = 2):
        """Keep only the last N messages in buffer after summarization"""
        _refresh_redis_state()
        if not REDIS_AVAILABLE:
            return
        try:
            key = self._buffer_key(session_id)
            _redis_client.ltrim(key, -keep_last, -1)
        except Exception as e:
            logger.error(f"Redis trim_buffer error: {e}")

    # ── Public API ─────────────────────────────────────────────────────────────

    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Return conversation history.
        Priority: Redis buffer (fast) → SQLite fallback
        """
        buffer = self._get_redis_buffer(session_id)
        if buffer:
            return buffer[-limit:]

        # Fallback to SQLite
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content FROM (
                    SELECT id, role, content FROM chat_history
                    WHERE session_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
                ORDER BY id ASC
            """, (session_id, limit))
            rows = cursor.fetchall()
            return [{"role": row[0], "content": row[1]} for row in rows]

    def get_summary(self, session_id: str) -> Optional[str]:
        """Get compressed conversation summary from Redis"""
        return self._get_redis_summary(session_id)

    def add_message(self, session_id: str, role: str, content: str):
        """
        Add message to:
        1. Redis buffer (fast, TTL-based)
        2. SQLite (persistent)
        Then check if buffer needs summarization.
        """
        # 1. Redis buffer
        self._append_redis_buffer(session_id, role, content)

        # 2. SQLite persistent
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (session_id, role, content)
                VALUES (?, ?, ?)
            """, (session_id, role, content))
            conn.commit()

        # 3. Auto-summarize if buffer exceeds threshold
        if REDIS_AVAILABLE:
            buffer = self._get_redis_buffer(session_id)
            if len(buffer) > settings.REDIS_BUFFER_THRESHOLD:
                self._auto_summarize(session_id, buffer)

    def _auto_summarize(self, session_id: str, buffer: List[Dict]):
        """Simple summarization: keep last 2 messages, compress the rest"""
        try:
            # Simple concatenation summary (can be replaced with LLM summarizer later)
            old_msgs = buffer[:-2]
            summary_text = " | ".join(
                f"{m['role']}: {m['content'][:100]}" for m in old_msgs
            )
            existing = self._get_redis_summary(session_id)
            if existing:
                summary_text = existing + " | " + summary_text

            self._set_redis_summary(session_id, summary_text)
            self._trim_redis_buffer(session_id, keep_last=2)
            logger.info(f"Auto-summarized buffer for session {session_id}")
        except Exception as e:
            logger.error(f"Auto-summarize error: {e}")

    def clear_history(self, session_id: str):
        """Clear all history for a session (Redis + SQLite)"""
        _refresh_redis_state()
        if REDIS_AVAILABLE:
            try:
                _redis_client.delete(
                    self._buffer_key(session_id),
                    self._summary_key(session_id)
                )
            except Exception as e:
                logger.error(f"Redis clear error: {e}")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
            conn.commit()

    def health_check(self) -> Dict:
        _refresh_redis_state()
        sqlite_ok = False
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
            sqlite_ok = True
        except sqlite3.Error as e:
            logger.error(f"SQLite health check failed: {e}")

        return {
            "redis_available": REDIS_AVAILABLE,
            "sqlite_ok": sqlite_ok,
        }


# Singleton instance
memory_service = MemoryService()

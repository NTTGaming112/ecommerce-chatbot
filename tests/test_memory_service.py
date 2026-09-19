import sqlite3

from app.core.config import settings
from app.services.memory_service import MemoryService


def test_sqlite_history_returns_most_recent_messages_in_order(tmp_path, monkeypatch):
    database_path = tmp_path / "history.db"
    monkeypatch.setattr(settings, "SQLITE_DB_PATH", str(database_path))
    service = MemoryService()

    with sqlite3.connect(database_path) as connection:
        for index in range(12):
            connection.execute(
                "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
                ("session-1", "user", f"message-{index}"),
            )
        connection.commit()

    history = service.get_history("session-1", limit=3)

    assert [message["content"] for message in history] == ["message-9", "message-10", "message-11"]
    assert service.health_check()["sqlite_ok"] is True

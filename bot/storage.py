import json
import sqlite3
from typing import Any, Dict, Mapping, Optional

from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StateType, StorageKey

# A row is "empty" once its conversation is over: no state and no data.
# aiogram's FSMContext.clear() sets state=None then data={}, so deleting empty
# rows keeps the table holding only in-progress conversations (0 rows at rest).
_EMPTY_ROW = (
    "DELETE FROM fsm WHERE key=? AND state IS NULL "
    "AND (data IS NULL OR data IN ('', '{}'))"
)


def _key_str(key: StorageKey) -> str:
    """Serialize a StorageKey to a stable primary-key string."""
    return ":".join(
        str(part)
        for part in (
            key.bot_id,
            key.chat_id,
            key.user_id,
            key.thread_id,
            key.business_connection_id,
            key.destiny,
        )
    )


class SQLiteStorage(BaseStorage):
    """
    File-backed FSM storage for aiogram.

    Unlike the default MemoryStorage, state survives process restarts/reloads,
    which is required because this bot runs as a stateless Flask webhook where
    each Telegram update is a separate request handled by a (possibly recycled)
    worker process.

    Data is stored as JSON, so only JSON-serializable values may be placed in
    FSM data (no Enums/objects — pass those explicitly in handlers instead).
    Finished conversations are deleted, so the table stays empty at rest.
    """

    def __init__(self, path: str):
        self.path = path
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS fsm ("
                "key TEXT PRIMARY KEY, state TEXT, data TEXT)"
            )

    def _connect(self) -> sqlite3.Connection:
        # Short-lived connection per operation; safe under the per-request
        # asyncio.run() lifecycle. busy_timeout avoids 'database is locked'.
        conn = sqlite3.connect(self.path, timeout=10)
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        value = state.state if isinstance(state, State) else state
        k = _key_str(key)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO fsm(key, state, data) "
                "VALUES(?, ?, COALESCE((SELECT data FROM fsm WHERE key=?), '{}')) "
                "ON CONFLICT(key) DO UPDATE SET state=excluded.state",
                (k, value, k),
            )
            conn.execute(_EMPTY_ROW, (k,))

    async def get_state(self, key: StorageKey) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT state FROM fsm WHERE key=?", (_key_str(key),)
            ).fetchone()
        return row[0] if row else None

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        k = _key_str(key)
        payload = json.dumps(dict(data))
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO fsm(key, state, data) "
                "VALUES(?, (SELECT state FROM fsm WHERE key=?), ?) "
                "ON CONFLICT(key) DO UPDATE SET data=excluded.data",
                (k, k, payload),
            )
            conn.execute(_EMPTY_ROW, (k,))

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT data FROM fsm WHERE key=?", (_key_str(key),)
            ).fetchone()
        if row and row[0]:
            return json.loads(row[0])
        return {}

    async def close(self) -> None:
        pass

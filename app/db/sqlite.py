import aiosqlite
from datetime import datetime, timedelta, UTC

class DB:
    def __init__(self, path: str):
        self.path = path

    async def init(self):
        async with aiosqlite.connect(self.path) as db:
            await db.execute("""CREATE TABLE IF NOT EXISTS results (
            user_id INTEGER, session_id TEXT, category TEXT, proxy TEXT, created_at TEXT
            )""")
            await db.commit()

    async def save_results(self, user_id: int, session_id: str, categorized: dict[str, list[str]]):
        now = datetime.now(UTC).isoformat()
        async with aiosqlite.connect(self.path) as db:
            for cat, items in categorized.items():
                await db.executemany(
                    "INSERT INTO results (user_id, session_id, category, proxy, created_at) VALUES (?, ?, ?, ?, ?)",
                    [(user_id, session_id, cat, p, now) for p in items],
                )
            await db.commit()

    async def get_category(self, user_id: int, session_id: str, category: str, ttl_hours: int):
        since = (datetime.now(UTC) - timedelta(hours=ttl_hours)).isoformat()
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(
                "SELECT proxy FROM results WHERE user_id=? AND session_id=? AND category=? AND created_at>?",
                (user_id, session_id, category, since),
            )
            rows = await cur.fetchall()
        return [r[0] for r in rows]

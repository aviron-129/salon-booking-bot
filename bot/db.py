from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT,
    username TEXT,
    lang TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    master_id INTEGER NOT NULL,
    starts_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    reminded_24h INTEGER NOT NULL DEFAULT 0,
    reminded_2h INTEGER NOT NULL DEFAULT 0,
    review_asked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_bookings_master_start ON bookings(master_id, starts_at);
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER UNIQUE,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    text TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS days_off (
    master_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    PRIMARY KEY (master_id, day)
);
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS relay (
    owner_msg_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL
);
"""


@dataclass
class Booking:
    id: int
    user_id: int
    service_id: int
    master_id: int
    start: datetime
    end: datetime
    status: str
    user_name: str | None = None
    user_phone: str | None = None
    user_lang: str | None = None


class DB:
    def __init__(self, path: str, tz):
        self.path, self.tz = path, tz
        self.conn: aiosqlite.Connection | None = None
        self.on_change: Callable[[int], None] | None = None

    def _changed(self, booking_id: int):
        if self.on_change:
            self.on_change(booking_id)

    async def connect(self):
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self):
        if self.conn:
            await self.conn.close()

    def now(self) -> datetime:
        return datetime.now(self.tz)

    # ---------- users ----------
    async def get_user(self, user_id: int):
        async with self.conn.execute("SELECT * FROM users WHERE id=?", (user_id,)) as cur:
            return await cur.fetchone()

    async def upsert_user(self, user_id: int, **fields):
        row = await self.get_user(user_id)
        if row is None:
            await self.conn.execute("INSERT INTO users(id, created_at) VALUES (?, ?)",
                                    (user_id, self.now().isoformat()))
        if fields:
            cols = ", ".join(f"{k}=?" for k in fields)
            await self.conn.execute(f"UPDATE users SET {cols} WHERE id=?", (*fields.values(), user_id))
        await self.conn.commit()

    async def all_user_ids(self) -> list[int]:
        async with self.conn.execute("SELECT id FROM users") as cur:
            return [r[0] for r in await cur.fetchall()]

    # ---------- bookings ----------
    def _booking(self, r) -> Booking:
        keys = r.keys()
        return Booking(
            id=r["id"], user_id=r["user_id"], service_id=r["service_id"], master_id=r["master_id"],
            start=datetime.fromisoformat(r["starts_at"]).astimezone(self.tz),
            end=datetime.fromisoformat(r["ends_at"]).astimezone(self.tz), status=r["status"],
            user_name=r["name"] if "name" in keys else None,
            user_phone=r["phone"] if "phone" in keys else None,
            user_lang=r["lang"] if "lang" in keys else None,
        )

    async def busy_for_master(self, master_id: int, day: date, exclude_booking: int | None = None):
        start = datetime.combine(day, datetime.min.time(), self.tz)
        end = start + timedelta(days=1)
        async with self.conn.execute(
            "SELECT starts_at, ends_at FROM bookings WHERE master_id=? AND status='active' AND starts_at<? AND ends_at>? AND id!=?",
            (master_id, end.isoformat(), start.isoformat(), exclude_booking or -1),
        ) as cur:
            rows = await cur.fetchall()
        return [(datetime.fromisoformat(a).astimezone(self.tz), datetime.fromisoformat(b).astimezone(self.tz))
                for a, b in rows]

    async def is_free(self, master_id: int, start: datetime, end: datetime, exclude_booking: int | None = None):
        async with self.conn.execute(
            "SELECT 1 FROM bookings WHERE master_id=? AND status='active' AND starts_at<? AND ends_at>? AND id!=? LIMIT 1",
            (master_id, end.isoformat(), start.isoformat(), exclude_booking or -1),
        ) as cur:
            return await cur.fetchone() is None

    async def create_booking(self, user_id: int, service_id: int, master_id: int, start: datetime, end: datetime):
        cur = await self.conn.execute(
            "INSERT INTO bookings(user_id, service_id, master_id, starts_at, ends_at, created_at) VALUES (?,?,?,?,?,?)",
            (user_id, service_id, master_id, start.isoformat(), end.isoformat(), self.now().isoformat()),
        )
        await self.conn.commit()
        self._changed(cur.lastrowid)
        return cur.lastrowid

    async def move_booking(self, booking_id: int, master_id: int, start: datetime, end: datetime):
        await self.conn.execute(
            "UPDATE bookings SET master_id=?, starts_at=?, ends_at=?, reminded_24h=0, reminded_2h=0 WHERE id=?",
            (master_id, start.isoformat(), end.isoformat(), booking_id),
        )
        await self.conn.commit()
        self._changed(booking_id)

    async def set_status(self, booking_id: int, status: str):
        await self.conn.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
        await self.conn.commit()
        self._changed(booking_id)

    async def get_booking(self, booking_id: int) -> Booking | None:
        async with self.conn.execute(
            "SELECT b.*, u.name, u.phone, u.lang FROM bookings b LEFT JOIN users u ON u.id=b.user_id WHERE b.id=?",
            (booking_id,),
        ) as cur:
            r = await cur.fetchone()
        return self._booking(r) if r else None

    async def user_upcoming(self, user_id: int) -> list[Booking]:
        async with self.conn.execute(
            "SELECT * FROM bookings WHERE user_id=? AND status='active' AND ends_at>? ORDER BY starts_at",
            (user_id, self.now().isoformat()),
        ) as cur:
            return [self._booking(r) for r in await cur.fetchall()]

    async def bookings_on(self, day: date) -> list[Booking]:
        start = datetime.combine(day, datetime.min.time(), self.tz)
        async with self.conn.execute(
            "SELECT b.*, u.name, u.phone, u.lang FROM bookings b LEFT JOIN users u ON u.id=b.user_id "
            "WHERE b.starts_at>=? AND b.starts_at<? AND b.status!='cancelled' ORDER BY b.starts_at",
            (start.isoformat(), (start + timedelta(days=1)).isoformat()),
        ) as cur:
            return [self._booking(r) for r in await cur.fetchall()]

    async def due_reminders(self, column: str, hours: int) -> list[Booking]:
        assert column in ("reminded_24h", "reminded_2h")
        now = self.now()
        async with self.conn.execute(
            f"SELECT b.*, u.name, u.phone, u.lang FROM bookings b LEFT JOIN users u ON u.id=b.user_id "
            f"WHERE b.status='active' AND b.{column}=0 AND b.starts_at>? AND b.starts_at<=?",
            (now.isoformat(), (now + timedelta(hours=hours)).isoformat()),
        ) as cur:
            return [self._booking(r) for r in await cur.fetchall()]

    async def mark(self, booking_id: int, column: str):
        assert column in ("reminded_24h", "reminded_2h", "review_asked")
        await self.conn.execute(f"UPDATE bookings SET {column}=1 WHERE id=?", (booking_id,))
        await self.conn.commit()

    async def due_reviews(self) -> list[Booking]:
        cutoff = self.now() - timedelta(hours=2)
        async with self.conn.execute(
            "SELECT b.*, u.name, u.phone, u.lang FROM bookings b LEFT JOIN users u ON u.id=b.user_id "
            "WHERE b.status IN ('active','done') AND b.review_asked=0 AND b.ends_at<=?",
            (cutoff.isoformat(),),
        ) as cur:
            return [self._booking(r) for r in await cur.fetchall()]

    async def stats(self, days: int) -> dict:
        since = (self.now() - timedelta(days=days)).isoformat()
        q = "SELECT service_id, master_id, status FROM bookings WHERE created_at>=?"
        async with self.conn.execute(q, (since,)) as cur:
            rows = await cur.fetchall()
        async with self.conn.execute("SELECT AVG(rating), COUNT(*) FROM reviews") as cur:
            avg, n_reviews = await cur.fetchone()
        async with self.conn.execute("SELECT COUNT(*) FROM users") as cur:
            (n_users,) = await cur.fetchone()
        return {"rows": [tuple(r) for r in rows], "avg": avg, "n_reviews": n_reviews, "n_users": n_users}

    # ---------- days off ----------
    async def days_off(self, master_id: int) -> set[date]:
        async with self.conn.execute("SELECT day FROM days_off WHERE master_id=?", (master_id,)) as cur:
            return {date.fromisoformat(r[0]) for r in await cur.fetchall()}

    async def toggle_day_off(self, master_id: int, day: date) -> bool:
        if day in await self.days_off(master_id):
            await self.conn.execute("DELETE FROM days_off WHERE master_id=? AND day=?", (master_id, day.isoformat()))
            state = False
        else:
            await self.conn.execute("INSERT INTO days_off VALUES (?, ?)", (master_id, day.isoformat()))
            state = True
        await self.conn.commit()
        return state

    # ---------- reviews ----------
    async def add_review(self, booking_id: int, user_id: int, rating: int):
        await self.conn.execute(
            "INSERT OR REPLACE INTO reviews(booking_id, user_id, rating, created_at) VALUES (?,?,?,?)",
            (booking_id, user_id, rating, self.now().isoformat()),
        )
        await self.conn.commit()

    async def set_review_text(self, booking_id: int, text: str):
        await self.conn.execute("UPDATE reviews SET text=? WHERE booking_id=?", (text[:500], booking_id))
        await self.conn.commit()

    async def latest_reviews(self, limit: int = 5):
        async with self.conn.execute(
            "SELECT r.rating, r.text, u.name FROM reviews r LEFT JOIN users u ON u.id=r.user_id "
            "ORDER BY r.id DESC LIMIT ?", (limit,),
        ) as cur:
            return await cur.fetchall()

    # ---------- leads / relay ----------
    async def add_lead(self, user_id: int, text: str):
        await self.conn.execute("INSERT INTO leads(user_id, text, created_at) VALUES (?,?,?)",
                                (user_id, text, self.now().isoformat()))
        await self.conn.commit()

    async def has_lead(self, user_id: int) -> bool:
        async with self.conn.execute("SELECT 1 FROM leads WHERE user_id=? LIMIT 1", (user_id,)) as cur:
            return await cur.fetchone() is not None

    async def remember_relay(self, owner_msg_id: int, user_id: int):
        await self.conn.execute("INSERT OR REPLACE INTO relay VALUES (?, ?)", (owner_msg_id, user_id))
        await self.conn.commit()

    async def relay_target(self, owner_msg_id: int) -> int | None:
        async with self.conn.execute("SELECT user_id FROM relay WHERE owner_msg_id=?", (owner_msg_id,)) as cur:
            r = await cur.fetchone()
        return r[0] if r else None

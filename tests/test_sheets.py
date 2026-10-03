import asyncio
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from bot.catalog import MASTERS, SERVICES
from bot.db import DB
from bot.sheets import HEADER, SheetSync

TZ = ZoneInfo("Asia/Tashkent")


class FakeWS:
    def __init__(self):
        self.rows: list[list[str]] = []

    def row_values(self, n):
        return self.rows[n - 1] if len(self.rows) >= n else []

    def col_values(self, n):
        return [r[n - 1] for r in self.rows]

    def update(self, values, cell):
        r = int(cell[1:]) - 1
        while len(self.rows) <= r:
            self.rows.append([])
        self.rows[r] = list(values[0])

    def append_row(self, row, value_input_option=None):
        self.rows.append(list(row))


class FakeClient:
    def __init__(self):
        self.ws = FakeWS()

    def open_by_key(self, key):
        return self

    def worksheet(self, title):
        return self.ws


async def _scenario(tmp_path):
    db = DB(str(tmp_path / "t.db"), TZ)
    await db.connect()
    client = FakeClient()
    sync = SheetSync(db, "sheet", "unused.json", client=client)
    db.on_change = sync.schedule

    await db.upsert_user(1, name="Аня", phone="+998901112233")
    s, m = SERVICES[0], MASTERS[0]
    start = datetime.combine(datetime.now(TZ).date() + timedelta(days=1), time(12, 0), TZ)
    bid = await db.create_booking(1, s.id, m.id, start, start + timedelta(minutes=60))
    await asyncio.sleep(0.1)
    await db.move_booking(bid, m.id, start + timedelta(hours=2), start + timedelta(hours=3))
    await asyncio.sleep(0.1)
    await db.set_status(bid, "cancelled")
    await asyncio.sleep(0.1)
    await db.close()
    return client.ws.rows, bid


def test_booking_lifecycle_updates_single_row(tmp_path):
    rows, bid = asyncio.run(_scenario(tmp_path))
    assert rows[0] == HEADER
    assert len(rows) == 2
    row = rows[1]
    assert row[0] == str(bid)
    assert row[2].startswith("14:00")
    assert row[5:8] == ["Аня", "+998901112233", "Отменён"]

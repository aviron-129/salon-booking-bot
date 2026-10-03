import asyncio
import logging
from datetime import datetime

from .catalog import MASTER_BY_ID, SERVICE_BY_ID, name
from .db import DB, Booking

log = logging.getLogger(__name__)

HEADER = ["ID", "Дата", "Время", "Услуга", "Мастер", "Клиент", "Телефон", "Статус", "Обновлено"]
STATUS = {"active": "Записан", "done": "Пришёл", "noshow": "Не пришёл", "cancelled": "Отменён"}


def booking_row(b: Booking, now: datetime) -> list[str]:
    s, m = SERVICE_BY_ID.get(b.service_id), MASTER_BY_ID.get(b.master_id)
    return [
        str(b.id),
        b.start.strftime("%d.%m.%Y"),
        f"{b.start:%H:%M}–{b.end:%H:%M}",
        name(s, "ru") if s else str(b.service_id),
        name(m, "ru") if m else str(b.master_id),
        b.user_name or "",
        b.user_phone or "",
        STATUS.get(b.status, b.status),
        now.strftime("%d.%m.%Y %H:%M"),
    ]


class SheetSync:
    """Mirrors bookings into a Google Sheet: one row per booking, matched by ID in column A."""

    def __init__(self, db: DB, sheet_id: str, creds_file: str, worksheet: str = "Записи", client=None):
        self.db, self.sheet_id, self.creds_file, self.worksheet = db, sheet_id, creds_file, worksheet
        self._client, self._ws = client, None
        self._lock = asyncio.Lock()
        self._tasks: set[asyncio.Task] = set()

    def _open(self):
        if self._ws is None:
            if self._client is None:
                import gspread
                self._client = gspread.service_account(filename=self.creds_file)
            book = self._client.open_by_key(self.sheet_id)
            try:
                self._ws = book.worksheet(self.worksheet)
            except Exception:
                self._ws = book.add_worksheet(self.worksheet, rows=1000, cols=len(HEADER))
            if self._ws.row_values(1) != HEADER:
                self._ws.update([HEADER], "A1")
        return self._ws

    def _upsert(self, row: list[str]):
        ws = self._open()
        ids = ws.col_values(1)
        if row[0] in ids:
            r = ids.index(row[0]) + 1
            ws.update([row], f"A{r}")
        else:
            ws.append_row(row, value_input_option="RAW")

    async def push(self, booking_id: int):
        b = await self.db.get_booking(booking_id)
        if b is None:
            return
        row = booking_row(b, self.db.now())
        async with self._lock:
            try:
                await asyncio.to_thread(self._upsert, row)
            except Exception:
                self._ws = None
                log.exception("Google Sheets sync failed for booking %s", booking_id)

    def schedule(self, booking_id: int):
        task = asyncio.create_task(self.push(booking_id))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

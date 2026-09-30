import logging
from datetime import date, datetime, timedelta

from aiogram import Bot

from .catalog import BOOKING_DAYS_AHEAD, MASTER_BY_ID, SALON, SERVICE_BY_ID, Service, masters_for, name
from .config import Config
from .db import DB, Booking
from .slots import free_slots, working_day
from .texts import fmt_date, t

log = logging.getLogger(__name__)


def is_admin(cfg: Config, user_id: int) -> bool:
    return cfg.demo or user_id == cfg.owner_id


def can_manage(cfg: Config, user_id: int, booking: Booking) -> bool:
    return user_id == cfg.owner_id or not cfg.demo or booking.user_id == user_id


def client_label(cfg: Config, viewer_id: int, b: Booking) -> str:
    if cfg.demo and viewer_id != cfg.owner_id and b.user_id != viewer_id:
        return "👤 •••"
    return f"👤 {b.user_name or '—'} · {b.user_phone or '—'}"


async def slots_for(db: DB, service: Service, master_id: int, day: date,
                    exclude: int | None = None) -> list[tuple[datetime, int]]:
    masters = [MASTER_BY_ID[master_id]] if master_id else masters_for(service)
    found: dict[datetime, int] = {}
    for m in masters:
        if not working_day(day, m.weekly_off, await db.days_off(m.id)):
            continue
        busy = await db.busy_for_master(m.id, day, exclude)
        for s in free_slots(day, service.minutes, busy, db.now(), SALON["opens"], SALON["closes"]):
            found.setdefault(s, m.id)
    return sorted(found.items())


async def day_options(db: DB, service: Service, master_id: int, exclude: int | None = None):
    today = db.now().date()
    result = []
    for i in range(BOOKING_DAYS_AHEAD):
        d = today + timedelta(days=i)
        result.append((d, bool(await slots_for(db, service, master_id, d, exclude))))
    return result


def booking_fields(b: Booking, lang: str) -> dict:
    s, m = SERVICE_BY_ID[b.service_id], MASTER_BY_ID[b.master_id]
    return {
        "service": name(s, lang), "master": name(m, lang), "date": fmt_date(b.start.date(), lang),
        "time": b.start.strftime("%H:%M"), "end": b.end.strftime("%H:%M"),
    }


async def notify_admins(bot: Bot, cfg: Config, db: DB, key: str, booking: Booking, actor_id: int):
    """Send an admin notification to the owner; in demo mode also show it to the visitor who triggered it."""
    targets: list[tuple[int, str, bool]] = []
    if cfg.owner_id:
        owner = await db.get_user(cfg.owner_id)
        targets.append((cfg.owner_id, (owner["lang"] if owner else None) or "ru", False))
    if cfg.demo and actor_id != cfg.owner_id:
        actor = await db.get_user(actor_id)
        targets.append((actor_id, (actor["lang"] if actor else None) or "ru", True))
    for chat_id, lang, demo_note in targets:
        text = t(lang, key, client=client_label(cfg, chat_id, booking), **booking_fields(booking, lang))
        if demo_note:
            text += t(lang, "admin_demo_note")
        try:
            await bot.send_message(chat_id, text)
        except Exception as e:
            log.warning("admin notify to %s failed: %s", chat_id, e)


async def reminder_flags(db: DB, booking_id: int, start: datetime):
    left = start - db.now()
    if left <= timedelta(hours=24):
        await db.mark(booking_id, "reminded_24h")
    if left <= timedelta(hours=2):
        await db.mark(booking_id, "reminded_2h")

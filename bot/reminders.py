import asyncio
import logging

from aiogram import Bot

from .common import booking_fields
from .db import DB
from .keyboards import rating_kb, reminder_kb
from .texts import t

log = logging.getLogger(__name__)


async def reminder_loop(bot: Bot, db: DB, every: int = 60):
    while True:
        try:
            await tick(bot, db)
        except Exception:
            log.exception("reminder tick failed")
        await asyncio.sleep(every)


async def tick(bot: Bot, db: DB):
    for column, hours, key in (("reminded_24h", 24, "remind_24h"), ("reminded_2h", 2, "remind_2h")):
        for b in await db.due_reminders(column, hours):
            lang = b.user_lang or "ru"
            f = booking_fields(b, lang)
            kb = reminder_kb(lang, b.id) if column == "reminded_24h" else None
            await _safe_send(bot, b.user_id, t(lang, key, time=f["time"], master=f["master"], service=f["service"]), kb)
            await db.mark(b.id, column)
    for b in await db.due_reviews():
        lang = b.user_lang or "ru"
        f = booking_fields(b, lang)
        await _safe_send(bot, b.user_id, t(lang, "ask_review", service=f["service"], master=f["master"]),
                         rating_kb(b.id))
        await db.mark(b.id, "review_asked")


async def _safe_send(bot: Bot, chat_id: int, text: str, kb=None):
    try:
        await bot.send_message(chat_id, text, reply_markup=kb)
    except Exception as e:
        log.warning("send to %s failed: %s", chat_id, e)

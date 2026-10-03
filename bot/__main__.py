import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from .config import load_config
from .db import DB
from .handlers import admin, booking, lead, my, start
from .middlewares import UserMiddleware
from .reminders import reminder_loop
from .sheets import SheetSync


async def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg = load_config()
    db = DB(cfg.db_path, cfg.tz)
    await db.connect()
    if cfg.gsheet_id:
        db.on_change = SheetSync(db, cfg.gsheet_id, cfg.google_creds).schedule

    bot = Bot(cfg.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(db=db, cfg=cfg)
    dp.message.outer_middleware(UserMiddleware())
    dp.callback_query.outer_middleware(UserMiddleware())
    dp.include_routers(start.router, booking.router, my.router, admin.router, lead.router)

    await bot.set_my_commands([BotCommand(command="start", description="Main menu / Главное меню")])
    reminders = asyncio.create_task(reminder_loop(bot, db))
    try:
        await dp.start_polling(bot)
    finally:
        reminders.cancel()
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())

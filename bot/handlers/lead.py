"""'I want this bot' requests and a two-way relay between visitors and the bot owner (the developer)."""
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from ..config import Config
from ..db import DB
from ..texts import all_variants, t

router = Router()


class Lead(StatesGroup):
    text = State()


def _who(message: Message, user) -> str:
    u = message.from_user
    parts = [u.full_name]
    if u.username:
        parts.append(f"@{u.username}")
    if user and user["phone"]:
        parts.append(user["phone"])
    parts.append(f"id {u.id}")
    return " · ".join(parts)


async def _to_owner(bot: Bot, cfg: Config, db: DB, message: Message, user, header: str):
    sent = await bot.send_message(cfg.owner_id, f"{header}\n{_who(message, user)}\n\n{message.text}\n\n"
                                                f"<i>Ответьте реплаем на это сообщение — бот перешлёт ответ.</i>")
    await db.remember_relay(sent.message_id, message.from_user.id)


@router.message(F.text.in_(all_variants("menu_order")))
async def order(message: Message, state: FSMContext, lang: str):
    await state.set_state(Lead.text)
    await message.answer(t(lang, "order_intro"))


@router.message(Lead.text, F.text & ~F.text.startswith("/"))
async def order_text(message: Message, state: FSMContext, db: DB, cfg: Config, bot: Bot, user, lang: str):
    await state.clear()
    await db.add_lead(message.from_user.id, message.text)
    if cfg.owner_id:
        await _to_owner(bot, cfg, db, message, user, "💼 <b>Новая заявка на бота</b>")
    await message.answer(t(lang, "order_sent"))


@router.message(F.text)
async def fallback(message: Message, db: DB, cfg: Config, bot: Bot, user, lang: str):
    if message.from_user.id == cfg.owner_id and message.reply_to_message:
        target = await db.relay_target(message.reply_to_message.message_id)
        if target:
            target_user = await db.get_user(target)
            await bot.send_message(target, t((target_user["lang"] if target_user else None) or "ru", "dev_reply",
                                             text=message.text))
            await message.reply("✅ Отправлено")
            return
    if cfg.owner_id and message.from_user.id != cfg.owner_id and await db.has_lead(message.from_user.id):
        await _to_owner(bot, cfg, db, message, user, "💬 <b>Сообщение от клиента</b>")
        await message.answer(t(lang, "sent_to_dev"))
        return
    await message.answer(t(lang, "unknown"))

from aiogram import Bot, F, Router
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from ..catalog import MASTER_BY_ID, SERVICE_BY_ID, name
from ..common import booking_fields, client_label, notify_admins
from ..config import Config
from ..db import DB
from ..keyboards import MyCb, RateCb, cancel_confirm_kb, my_booking_kb
from ..texts import all_variants, t
from .booking import start_reschedule

router = Router()


class ReviewText(StatesGroup):
    waiting = State()


@router.message(F.text.in_(all_variants("menu_my")))
async def my_bookings(message: Message, db: DB, lang: str):
    items = await db.user_upcoming(message.from_user.id)
    if not items:
        await message.answer(t(lang, "my_empty"))
        return
    for b in items:
        f = booking_fields(b, lang)
        await message.answer(t(lang, "my_item", date=f["date"], time=f["time"], service=f["service"],
                               master=f["master"]), reply_markup=my_booking_kb(lang, b.id))


async def _own_active(db: DB, call: CallbackQuery, booking_id: int):
    b = await db.get_booking(booking_id)
    if not b or b.user_id != call.from_user.id or b.status != "active":
        return None
    return b


@router.callback_query(MyCb.filter(F.action == "cancel"))
async def ask_cancel(call: CallbackQuery, callback_data: MyCb, db: DB, lang: str):
    b = await _own_active(db, call, callback_data.id)
    await call.answer()
    if not b:
        await call.message.edit_reply_markup(reply_markup=None)
        return
    f = booking_fields(b, lang)
    await call.message.edit_text(t(lang, "ask_cancel", date=f["date"], time=f["time"]),
                                 reply_markup=cancel_confirm_kb(lang, b.id))


@router.callback_query(MyCb.filter(F.action == "cancel_yes"))
async def do_cancel(call: CallbackQuery, callback_data: MyCb, db: DB, cfg: Config, bot: Bot, lang: str):
    b = await _own_active(db, call, callback_data.id)
    await call.answer()
    if not b:
        await call.message.edit_reply_markup(reply_markup=None)
        return
    await db.set_status(b.id, "cancelled")
    await call.message.edit_text(t(lang, "cancelled"))
    await notify_admins(bot, cfg, db, "admin_cancel", b, call.from_user.id)


@router.callback_query(MyCb.filter(F.action == "keep"))
async def keep(call: CallbackQuery, callback_data: MyCb, db: DB, lang: str):
    b = await _own_active(db, call, callback_data.id)
    await call.answer()
    if not b:
        await call.message.edit_reply_markup(reply_markup=None)
        return
    f = booking_fields(b, lang)
    await call.message.edit_text(t(lang, "my_item", date=f["date"], time=f["time"], service=f["service"],
                                   master=f["master"]), reply_markup=my_booking_kb(lang, b.id))


@router.callback_query(MyCb.filter(F.action == "resched"))
async def reschedule(call: CallbackQuery, callback_data: MyCb, db: DB, state: FSMContext, lang: str):
    b = await _own_active(db, call, callback_data.id)
    await call.answer()
    if not b:
        await call.message.edit_reply_markup(reply_markup=None)
        return
    await start_reschedule(call.message, state, db, lang, b)


@router.callback_query(MyCb.filter(F.action == "coming"))
async def coming(call: CallbackQuery, lang: str):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer(t(lang, "coming_ok"), show_alert=True)


@router.callback_query(RateCb.filter())
async def rate(call: CallbackQuery, callback_data: RateCb, db: DB, cfg: Config, bot: Bot, state: FSMContext,
               lang: str):
    b = await db.get_booking(callback_data.id)
    if not b or b.user_id != call.from_user.id:
        await call.answer()
        return
    await db.add_review(b.id, call.from_user.id, callback_data.stars)
    await call.message.edit_text(f"{call.message.text}\n\n{'⭐' * callback_data.stars}")
    await call.message.answer(t(lang, "review_thanks"))
    await state.set_state(ReviewText.waiting)
    await state.update_data(review_booking=b.id)
    await call.answer()
    if callback_data.stars <= 3 and cfg.owner_id:
        await bot.send_message(cfg.owner_id, t("ru", "admin_low_rating", rating=callback_data.stars,
                                               client=client_label(cfg, cfg.owner_id, b),
                                               service=name(SERVICE_BY_ID[b.service_id], "ru"),
                                               master=name(MASTER_BY_ID[b.master_id], "ru")))


@router.message(ReviewText.waiting, F.text & ~F.text.startswith("/"))
async def review_text(message: Message, state: FSMContext, db: DB, lang: str):
    menu_buttons = set().union(*(all_variants(k) for k in (
        "menu_book", "menu_my", "menu_prices", "menu_masters", "menu_contacts", "menu_reviews", "menu_admin",
        "menu_order", "menu_lang")))
    data = await state.get_data()
    await state.clear()
    if message.text in menu_buttons:
        raise SkipHandler()
    await db.set_review_text(data["review_booking"], message.text)
    await message.answer(t(lang, "review_text_thanks"))

from datetime import datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from ..catalog import MASTER_BY_ID, SALON, SERVICE_BY_ID, masters_for, name
from ..common import day_options, notify_admins, reminder_flags, slots_for
from ..config import Config
from ..db import DB
from ..keyboards import (CatCb, DayCb, FlowCb, MasterCb, SvcCb, TimeCb, categories_kb, confirm_kb, contact_kb,
                         days_kb, masters_kb, services_kb, times_kb)
from ..texts import all_variants, fmt_date, fmt_price, t
from .start import show_menu

router = Router()


class Book(StatesGroup):
    active = State()


@router.message(F.text.in_(all_variants("menu_book")))
async def begin(message: Message, state: FSMContext, user, lang: str):
    if not user or not user["phone"]:
        await message.answer(t(lang, "ask_contact"), reply_markup=contact_kb(lang))
        return
    await state.clear()
    await state.set_state(Book.active)
    await message.answer(t(lang, "pick_category"), reply_markup=categories_kb(lang))


async def start_reschedule(message: Message, state: FSMContext, db: DB, lang: str, booking):
    """Entry point used by 'my bookings' and reminders: keep service and stylist, choose a new date."""
    await state.clear()
    await state.set_state(Book.active)
    await state.update_data(service=booking.service_id, master=booking.master_id, resched=booking.id,
                            fixed_master=True)
    service = SERVICE_BY_ID[booking.service_id]
    await message.answer(
        t(lang, "reschedule_start", service=name(service, lang)),
        reply_markup=days_kb(lang, await day_options(db, service, booking.master_id, booking.id)),
    )


@router.callback_query(Book.active, CatCb.filter())
async def pick_category(call: CallbackQuery, callback_data: CatCb, state: FSMContext, lang: str):
    await state.update_data(cat=callback_data.cat)
    await call.message.edit_text(t(lang, "pick_service"), reply_markup=services_kb(lang, callback_data.cat))
    await call.answer()


async def _show_days(call: CallbackQuery, state: FSMContext, db: DB, lang: str):
    data = await state.get_data()
    service = SERVICE_BY_ID[data["service"]]
    days = await day_options(db, service, data["master"], data.get("resched"))
    await call.message.edit_text(t(lang, "pick_date"), reply_markup=days_kb(lang, days))


@router.callback_query(Book.active, SvcCb.filter())
async def pick_service(call: CallbackQuery, callback_data: SvcCb, state: FSMContext, db: DB, lang: str):
    service = SERVICE_BY_ID[callback_data.id]
    masters = masters_for(service)
    await state.update_data(service=service.id)
    if len(masters) == 1:
        await state.update_data(master=masters[0].id)
        await _show_days(call, state, db, lang)
    else:
        await call.message.edit_text(t(lang, "pick_master"), reply_markup=masters_kb(lang, masters))
    await call.answer()


@router.callback_query(Book.active, MasterCb.filter())
async def pick_master(call: CallbackQuery, callback_data: MasterCb, state: FSMContext, db: DB, lang: str):
    await state.update_data(master=callback_data.id)
    await _show_days(call, state, db, lang)
    await call.answer()


@router.callback_query(Book.active, DayCb.filter())
async def pick_day(call: CallbackQuery, callback_data: DayCb, state: FSMContext, db: DB, lang: str):
    data = await state.get_data()
    day = datetime.strptime(callback_data.d, "%Y%m%d").date()
    slots = await slots_for(db, SERVICE_BY_ID[data["service"]], data["master"], day, data.get("resched"))
    if not slots:
        await call.answer(t(lang, "no_slots"), show_alert=True)
        return
    await state.update_data(day=callback_data.d)
    await call.message.edit_text(t(lang, "pick_time", date=fmt_date(day, lang)), reply_markup=times_kb(lang, slots))
    await call.answer()


@router.callback_query(Book.active, TimeCb.filter())
async def pick_time(call: CallbackQuery, callback_data: TimeCb, state: FSMContext, db: DB, lang: str):
    data = await state.get_data()
    start = datetime.strptime(data["day"] + callback_data.hm, "%Y%m%d%H%M").replace(tzinfo=db.tz)
    await state.update_data(start=start.isoformat(), chosen_master=callback_data.m)
    service, master = SERVICE_BY_ID[data["service"]], MASTER_BY_ID[callback_data.m]
    await call.message.edit_text(
        t(lang, "confirm", service=name(service, lang), master=name(master, lang), date=fmt_date(start.date(), lang),
          time=start.strftime("%H:%M"), minutes=service.minutes, price=fmt_price(service.price, lang)),
        reply_markup=confirm_kb(lang),
    )
    await call.answer()


@router.callback_query(Book.active, FlowCb.filter(F.action == "confirm"))
async def confirm(call: CallbackQuery, state: FSMContext, db: DB, cfg: Config, bot: Bot, lang: str):
    data = await state.get_data()
    service = SERVICE_BY_ID[data["service"]]
    master_id = data["chosen_master"]
    start = datetime.fromisoformat(data["start"])
    end = start + timedelta(minutes=service.minutes)
    resched = data.get("resched")
    if not await db.is_free(master_id, start, end, resched):
        await call.answer(t(lang, "slot_taken"), show_alert=True)
        slots = await slots_for(db, service, data["master"], start.date(), resched)
        await call.message.edit_text(t(lang, "pick_time", date=fmt_date(start.date(), lang)),
                                     reply_markup=times_kb(lang, slots))
        return
    if resched:
        await db.move_booking(resched, master_id, start, end)
        booking_id = resched
    else:
        booking_id = await db.create_booking(call.from_user.id, service.id, master_id, start, end)
    await reminder_flags(db, booking_id, start)
    await state.clear()
    booking = await db.get_booking(booking_id)
    fields = dict(service=name(service, lang), master=name(MASTER_BY_ID[master_id], lang),
                  date=fmt_date(start.date(), lang), time=start.strftime("%H:%M"))
    if resched:
        await call.message.edit_text(t(lang, "rescheduled", date=fields["date"], time=fields["time"]))
    else:
        await call.message.edit_text(t(lang, "booked", address=SALON[f"address_{lang}"], **fields))
    await call.answer()
    await notify_admins(bot, cfg, db, "admin_moved" if resched else "admin_new", booking, call.from_user.id)


@router.callback_query(Book.active, FlowCb.filter())
async def navigate(call: CallbackQuery, callback_data: FlowCb, state: FSMContext, db: DB, cfg: Config, lang: str):
    data = await state.get_data()
    action = callback_data.action
    await call.answer()
    if action == "cancel":
        await state.clear()
        await call.message.edit_text(t(lang, "flow_cancelled"))
        await show_menu(call.message, cfg, lang)
    elif action == "back_cat" or (action == "back_svc" and "cat" not in data):
        await call.message.edit_text(t(lang, "pick_category"), reply_markup=categories_kb(lang))
    elif action == "back_svc":
        await call.message.edit_text(t(lang, "pick_service"), reply_markup=services_kb(lang, data["cat"]))
    elif action == "back_master":
        service = SERVICE_BY_ID[data["service"]]
        masters = masters_for(service)
        if data.get("fixed_master") or len(masters) == 1:
            if "cat" in data:
                await call.message.edit_text(t(lang, "pick_service"), reply_markup=services_kb(lang, data["cat"]))
            else:
                await state.clear()
                await call.message.edit_text(t(lang, "flow_cancelled"))
        else:
            await call.message.edit_text(t(lang, "pick_master"), reply_markup=masters_kb(lang, masters))
    elif action == "back_day":
        await _show_days(call, state, db, lang)


@router.callback_query(F.data.startswith(("cat:", "svc:", "mst:", "day:", "tm:", "flow:")))
async def stale_button(call: CallbackQuery, lang: str):
    await call.answer(t(lang, "flow_cancelled"), show_alert=False)

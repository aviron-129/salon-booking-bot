import asyncio
from collections import Counter
from datetime import datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..catalog import BOOKING_DAYS_AHEAD, MASTER_BY_ID, MASTERS, SERVICE_BY_ID, name
from ..common import booking_fields, can_manage, client_label, is_admin
from ..config import Config
from ..db import DB
from ..keyboards import AdmCb, admin_kb, back_to_admin_row
from ..texts import WEEKDAYS, all_variants, fmt_date, fmt_price, t

router = Router()


class Broadcast(StatesGroup):
    text = State()


def _title(cfg: Config, user_id: int, lang: str) -> str:
    hint = t(lang, "admin_demo_hint") if cfg.demo and user_id != cfg.owner_id else ""
    return t(lang, "admin_title") + hint


@router.callback_query(AdmCb.filter(F.action == "noop"))
async def noop(call: CallbackQuery):
    await call.answer()


@router.message(F.text.in_(all_variants("menu_admin")))
async def open_admin(message: Message, cfg: Config, lang: str, state: FSMContext):
    if not is_admin(cfg, message.from_user.id):
        return
    await state.clear()
    await message.answer(_title(cfg, message.from_user.id, lang), reply_markup=admin_kb(lang))


@router.callback_query(AdmCb.filter())
async def admin_actions(call: CallbackQuery, callback_data: AdmCb, db: DB, cfg: Config, bot: Bot,
                        state: FSMContext, lang: str):
    uid = call.from_user.id
    if not is_admin(cfg, uid):
        await call.answer()
        return
    action, arg = callback_data.action, callback_data.arg
    today = db.now().date()

    if action == "menu":
        await call.message.edit_text(_title(cfg, uid, lang), reply_markup=admin_kb(lang))

    elif action == "day":
        day = today + timedelta(days=int(arg)) if len(arg) < 8 else datetime.strptime(arg, "%Y%m%d").date()
        await _show_day(call, db, cfg, lang, day)

    elif action == "pick_day":
        kb = InlineKeyboardBuilder()
        for i in range(BOOKING_DAYS_AHEAD):
            d = today + timedelta(days=i)
            kb.button(text=f"{WEEKDAYS[lang][d.weekday()]} {d.day:02d}.{d.month:02d}",
                      callback_data=AdmCb(action="day", arg=d.strftime("%Y%m%d")))
        kb.adjust(3)
        back_to_admin_row(kb, lang)
        await call.message.edit_text(t(lang, "adm_pick_day"), reply_markup=kb.as_markup())

    elif action == "bk":
        b = await db.get_booking(int(arg))
        if not b:
            await call.answer()
            return
        f = booking_fields(b, lang)
        kb = InlineKeyboardBuilder()
        if b.status == "active":
            for st, key in (("done", "adm_done"), ("noshow", "adm_noshow"), ("cancelled", "adm_cancel")):
                kb.button(text=t(lang, key), callback_data=AdmCb(action="st", arg=f"{b.id}:{st}"))
        kb.adjust(2, 1)
        kb.row(InlineKeyboardButton(text=t(lang, "btn_back"),
                                    callback_data=AdmCb(action="day", arg=b.start.strftime("%Y%m%d")).pack()))
        text = t(lang, "adm_booking_line", client=client_label(cfg, uid, b), status=t(lang, f"st_{b.status}"), **f)
        await call.message.edit_text(f"📅 {f['date']}\n{text}", reply_markup=kb.as_markup())

    elif action == "st":
        booking_id, status = arg.split(":")
        b = await db.get_booking(int(booking_id))
        if not b or b.status != "active":
            await call.answer()
            return
        if not can_manage(cfg, uid, b):
            await call.answer(t(lang, "adm_only_own"), show_alert=True)
            return
        await db.set_status(b.id, status)
        if status == "cancelled":
            client_lang = b.user_lang or "ru"
            f = booking_fields(b, client_lang)
            try:
                await bot.send_message(b.user_id, t(client_lang, "adm_cancelled_by_salon", date=f["date"], time=f["time"]))
            except Exception:
                pass
        await call.answer(t(lang, "adm_status_set"))
        await _show_day(call, db, cfg, lang, b.start.date())
        return

    elif action == "off_master":
        kb = InlineKeyboardBuilder()
        for m in MASTERS:
            kb.button(text=name(m, lang), callback_data=AdmCb(action="off_m", arg=str(m.id)))
        kb.adjust(2)
        back_to_admin_row(kb, lang)
        await call.message.edit_text(t(lang, "adm_pick_master"), reply_markup=kb.as_markup())

    elif action in ("off_m", "off_d"):
        if action == "off_d":
            mid, d = arg.split(":")
            if uid != cfg.owner_id and cfg.demo:
                await call.answer(t(lang, "adm_off_only_owner"), show_alert=True)
                return
            day = datetime.strptime(d, "%Y%m%d").date()
            state_on = await db.toggle_day_off(int(mid), day)
            await call.answer(t(lang, "adm_off_set", date=fmt_date(day, lang),
                                state=t(lang, "off_on" if state_on else "off_off")))
        else:
            mid = arg
        master = MASTER_BY_ID[int(mid)]
        offs = await db.days_off(master.id)
        kb = InlineKeyboardBuilder()
        for i in range(BOOKING_DAYS_AHEAD):
            d = today + timedelta(days=i)
            off = d.weekday() in master.weekly_off or d in offs
            kb.button(text=f"{'🚫' if off else '✅'} {WEEKDAYS[lang][d.weekday()]} {d.day:02d}.{d.month:02d}",
                      callback_data=AdmCb(action="off_d", arg=f"{master.id}:{d.strftime('%Y%m%d')}"))
        kb.adjust(3)
        back_to_admin_row(kb, lang)
        await call.message.edit_text(t(lang, "adm_pick_off_day", master=name(master, lang)), reply_markup=kb.as_markup())
        if action == "off_d":
            return

    elif action == "broadcast":
        await state.set_state(Broadcast.text)
        await call.message.answer(t(lang, "adm_broadcast_ask"))

    elif action == "stats":
        st = await db.stats(30)
        rows = st["rows"]
        live = [r for r in rows if r[2] != "cancelled"]
        revenue = sum(SERVICE_BY_ID[r[0]].price for r in live)
        top_s = Counter(r[0] for r in live).most_common(1)
        top_m = Counter(r[1] for r in live).most_common(1)
        kb = InlineKeyboardBuilder()
        back_to_admin_row(kb, lang)
        await call.message.edit_text(t(
            lang, "adm_stats_text", total=len(rows), cancelled=len(rows) - len(live),
            revenue=fmt_price(revenue, lang),
            top_service=name(SERVICE_BY_ID[top_s[0][0]], lang) if top_s else "—",
            top_master=name(MASTER_BY_ID[top_m[0][0]], lang) if top_m else "—",
            users=st["n_users"], avg=f"{st['avg']:.1f}" if st["avg"] else "—", n_reviews=st["n_reviews"],
        ), reply_markup=kb.as_markup())

    await call.answer()


async def _show_day(call: CallbackQuery, db: DB, cfg: Config, lang: str, day):
    items = await db.bookings_on(day)
    kb = InlineKeyboardBuilder()
    if not items:
        text = t(lang, "adm_day_empty", date=fmt_date(day, lang))
    else:
        lines = [t(lang, "adm_day_title", date=fmt_date(day, lang), n=len(items))]
        for b in items:
            f = booking_fields(b, lang)
            lines.append(t(lang, "adm_booking_line", client=client_label(cfg, call.from_user.id, b),
                           status=t(lang, f"st_{b.status}"), **f))
            kb.button(text=f"{f['time']} · {f['master']}", callback_data=AdmCb(action="bk", arg=str(b.id)))
        lines.append("\n" + t(lang, "adm_pick_booking"))
        text = "\n".join(lines)
        kb.adjust(2)
    back_to_admin_row(kb, lang)
    await call.message.edit_text(text, reply_markup=kb.as_markup())


@router.message(Broadcast.text, F.text)
async def do_broadcast(message: Message, state: FSMContext, db: DB, cfg: Config, bot: Bot, lang: str):
    await state.clear()
    uid = message.from_user.id
    if cfg.demo and uid != cfg.owner_id:
        await message.answer(f"📣 {message.text}")
        await message.answer(t(lang, "adm_broadcast_demo"))
        return
    sent = 0
    for user_id in await db.all_user_ids():
        try:
            await bot.send_message(user_id, f"📣 {message.text}")
            sent += 1
        except Exception:
            pass
        await asyncio.sleep(0.05)
    await message.answer(t(lang, "adm_broadcast_done", n=sent))

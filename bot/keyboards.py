from datetime import date, datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from . import catalog
from .catalog import CATEGORIES, SERVICES, Master, Service, name
from .texts import LANG_LABELS, WEEKDAYS, fmt_price, t


class LangCb(CallbackData, prefix="lang"):
    code: str


class CatCb(CallbackData, prefix="cat"):
    cat: str


class SvcCb(CallbackData, prefix="svc"):
    id: int


class MasterCb(CallbackData, prefix="mst"):
    id: int


class DayCb(CallbackData, prefix="day"):
    d: str  # YYYYMMDD


class TimeCb(CallbackData, prefix="tm"):
    hm: str  # HHMM
    m: int


class FlowCb(CallbackData, prefix="flow"):
    action: str  # confirm | cancel | back_cat | back_svc | back_master | back_day


class MyCb(CallbackData, prefix="my"):
    action: str  # resched | cancel | cancel_yes | keep | coming
    id: int


class RateCb(CallbackData, prefix="rate"):
    id: int
    stars: int


class AdmCb(CallbackData, prefix="adm"):
    action: str
    arg: str = ""


def main_menu(lang: str, is_admin: bool) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(KeyboardButton(text=t(lang, "menu_book")))
    kb.row(KeyboardButton(text=t(lang, "menu_my")), KeyboardButton(text=t(lang, "menu_prices")))
    kb.row(KeyboardButton(text=t(lang, "menu_masters")), KeyboardButton(text=t(lang, "menu_contacts")))
    kb.row(KeyboardButton(text=t(lang, "menu_reviews")), KeyboardButton(text=t(lang, "menu_lang")))
    last = [] if catalog.SALON.get("hide_order") else [KeyboardButton(text=t(lang, "menu_order"))]
    if is_admin:
        last.insert(0, KeyboardButton(text=t(lang, "menu_admin")))
    if last:
        kb.row(*last)
    return kb.as_markup(resize_keyboard=True)


def contact_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "btn_share_contact"), request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True,
    )


def lang_kb():
    kb = InlineKeyboardBuilder()
    for code in catalog.langs():
        kb.button(text=LANG_LABELS[code], callback_data=LangCb(code=code))
    return kb.as_markup()


def _cancel_row(kb: InlineKeyboardBuilder, lang: str, back: str | None):
    buttons = []
    if back:
        buttons.append(("btn_back", FlowCb(action=back)))
    buttons.append(("btn_cancel_flow", FlowCb(action="cancel")))
    from aiogram.types import InlineKeyboardButton
    kb.row(*[InlineKeyboardButton(text=t(lang, k), callback_data=cb.pack()) for k, cb in buttons])


def categories_kb(lang: str):
    kb = InlineKeyboardBuilder()
    for c in CATEGORIES:
        kb.button(text=f"{c.emoji} {name(c, lang)}", callback_data=CatCb(cat=c.id))
    kb.adjust(2)
    _cancel_row(kb, lang, None)
    return kb.as_markup()


def services_kb(lang: str, cat: str):
    kb = InlineKeyboardBuilder()
    for s in SERVICES:
        if s.category == cat:
            kb.button(text=f"{name(s, lang)} · {fmt_price(s.price, lang)}", callback_data=SvcCb(id=s.id))
    kb.adjust(1)
    _cancel_row(kb, lang, "back_cat")
    return kb.as_markup()


def masters_kb(lang: str, masters: list[Master]):
    kb = InlineKeyboardBuilder()
    if len(masters) > 1:
        kb.button(text=t(lang, "any_master"), callback_data=MasterCb(id=0))
    for m in masters:
        kb.button(text=name(m, lang), callback_data=MasterCb(id=m.id))
    kb.adjust(1)
    _cancel_row(kb, lang, "back_svc")
    return kb.as_markup()


def days_kb(lang: str, days: list[tuple[date, bool]]):
    kb = InlineKeyboardBuilder()
    for d, available in days:
        label = f"{WEEKDAYS[lang][d.weekday()]} {d.day:02d}.{d.month:02d}"
        if available:
            kb.button(text=label, callback_data=DayCb(d=d.strftime("%Y%m%d")))
        else:
            kb.button(text=f"🚫 {label}", callback_data=AdmCb(action="noop"))
    kb.adjust(3)
    _cancel_row(kb, lang, "back_master")
    return kb.as_markup()


def times_kb(lang: str, slots: list[tuple[datetime, int]]):
    kb = InlineKeyboardBuilder()
    for dt, master_id in slots:
        kb.button(text=dt.strftime("%H:%M"), callback_data=TimeCb(hm=dt.strftime("%H%M"), m=master_id))
    kb.adjust(4)
    _cancel_row(kb, lang, "back_day")
    return kb.as_markup()


def confirm_kb(lang: str):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_confirm"), callback_data=FlowCb(action="confirm"))
    kb.adjust(1)
    _cancel_row(kb, lang, "back_day")
    return kb.as_markup()


def my_booking_kb(lang: str, booking_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_reschedule"), callback_data=MyCb(action="resched", id=booking_id))
    kb.button(text=t(lang, "btn_cancel_booking"), callback_data=MyCb(action="cancel", id=booking_id))
    return kb.as_markup()


def cancel_confirm_kb(lang: str, booking_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_yes_cancel"), callback_data=MyCb(action="cancel_yes", id=booking_id))
    kb.button(text=t(lang, "btn_no"), callback_data=MyCb(action="keep", id=booking_id))
    return kb.as_markup()


def reminder_kb(lang: str, booking_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_im_coming"), callback_data=MyCb(action="coming", id=booking_id))
    kb.button(text=t(lang, "btn_reschedule"), callback_data=MyCb(action="resched", id=booking_id))
    kb.button(text=t(lang, "btn_cancel_booking"), callback_data=MyCb(action="cancel", id=booking_id))
    kb.adjust(1, 2)
    return kb.as_markup()


def rating_kb(booking_id: int):
    kb = InlineKeyboardBuilder()
    for s in range(1, 6):
        kb.button(text="⭐" * s, callback_data=RateCb(id=booking_id, stars=s))
    kb.adjust(1)
    return kb.as_markup()


def admin_kb(lang: str):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "adm_today"), callback_data=AdmCb(action="day", arg="0"))
    kb.button(text=t(lang, "adm_tomorrow"), callback_data=AdmCb(action="day", arg="1"))
    kb.button(text=t(lang, "adm_pick_day"), callback_data=AdmCb(action="pick_day"))
    kb.button(text=t(lang, "adm_days_off"), callback_data=AdmCb(action="off_master"))
    kb.button(text=t(lang, "adm_broadcast"), callback_data=AdmCb(action="broadcast"))
    kb.button(text=t(lang, "adm_stats"), callback_data=AdmCb(action="stats"))
    kb.adjust(2, 1, 1, 2)
    return kb.as_markup()


def back_to_admin_row(kb: InlineKeyboardBuilder, lang: str):
    from aiogram.types import InlineKeyboardButton
    kb.row(InlineKeyboardButton(text=t(lang, "btn_back"), callback_data=AdmCb(action="menu").pack()))


def service_label(s: Service, lang: str) -> str:
    return name(s, lang)

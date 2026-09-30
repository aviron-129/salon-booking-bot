from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..catalog import CATEGORIES, MASTERS, SALON, SERVICES, name
from ..common import is_admin
from ..config import Config
from ..db import DB
from ..keyboards import LangCb, contact_kb, lang_kb, main_menu
from ..texts import all_variants, fmt_price, t

router = Router()


async def show_menu(message: Message, cfg: Config, lang: str, text: str | None = None):
    await message.answer(text or t(lang, "menu_hint"), reply_markup=main_menu(lang, is_admin(cfg, message.chat.id)))


@router.message(CommandStart())
async def start(message: Message, db: DB, cfg: Config, user, lang: str, state: FSMContext):
    await state.clear()
    await db.upsert_user(message.from_user.id, username=message.from_user.username)
    if not user or not user["lang"]:
        await message.answer(t("ru", "choose_lang"), reply_markup=lang_kb())
    elif not user["phone"]:
        await message.answer(t(lang, "ask_contact"), reply_markup=contact_kb(lang))
    else:
        await show_menu(message, cfg, lang, t(lang, "welcome", salon=SALON["name"]))


@router.callback_query(LangCb.filter())
async def set_lang(call: CallbackQuery, callback_data: LangCb, db: DB, cfg: Config, user):
    lang = callback_data.code
    await db.upsert_user(call.from_user.id, lang=lang)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    if user and user["phone"]:
        await show_menu(call.message, cfg, lang)
        return
    await call.message.answer(t(lang, "welcome", salon=SALON["name"]))
    if cfg.demo:
        await call.message.answer(t(lang, "demo_banner"))
    await call.message.answer(t(lang, "ask_contact"), reply_markup=contact_kb(lang))


@router.message(F.contact)
async def got_contact(message: Message, db: DB, cfg: Config, lang: str):
    if message.contact.user_id != message.from_user.id:
        await message.answer(t(lang, "not_own_contact"), reply_markup=contact_kb(lang))
        return
    first = message.contact.first_name or message.from_user.first_name or ""
    await db.upsert_user(message.from_user.id, phone=message.contact.phone_number, name=first)
    await show_menu(message, cfg, lang, t(lang, "contact_saved", name=first))


@router.message(F.text.in_(all_variants("menu_lang")))
async def change_lang(message: Message):
    await message.answer(t("ru", "choose_lang"), reply_markup=lang_kb())


@router.message(F.text.in_(all_variants("menu_prices")))
async def prices(message: Message, lang: str):
    lines = [t(lang, "prices_title")]
    for c in CATEGORIES:
        lines.append(f"\n{c.emoji} <b>{name(c, lang)}</b>")
        for s in SERVICES:
            if s.category == c.id:
                lines.append(f"• {name(s, lang)} — {fmt_price(s.price, lang)} · {s.minutes} min")
    await message.answer("\n".join(lines).replace(" min", " мин" if lang == "ru" else " min"))


@router.message(F.text.in_(all_variants("menu_masters")))
async def masters(message: Message, lang: str):
    lines = [t(lang, "masters_title")]
    for m in MASTERS:
        lines.append(f"\n<b>{name(m, lang)}</b>\n{m.about_ru if lang == 'ru' else m.about_en}")
    await message.answer("\n".join(lines))


@router.message(F.text.in_(all_variants("menu_contacts")))
async def contacts(message: Message, lang: str):
    await message.answer(t(lang, "contacts", salon=SALON["name"], address=SALON[f"address_{lang}"],
                           phone=SALON["phone"], opens=SALON["opens"].strftime("%H:%M"),
                           closes=SALON["closes"].strftime("%H:%M")))
    await message.answer_location(SALON["lat"], SALON["lon"])


@router.message(F.text.in_(all_variants("menu_reviews")))
async def reviews(message: Message, db: DB, lang: str):
    rows = await db.latest_reviews()
    if not rows:
        await message.answer(t(lang, "reviews_empty"))
        return
    st = await db.stats(3650)
    lines = [t(lang, "reviews_title", avg=f"{st['avg']:.1f}", n=st["n_reviews"])]
    for r in rows:
        text = f" — «{r['text']}»" if r["text"] else ""
        lines.append(f"{'⭐' * r['rating']} {r['name'] or ''}{text}")
    await message.answer("\n".join(lines))

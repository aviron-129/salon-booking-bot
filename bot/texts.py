TEXTS = {
    "ru": {
        "choose_lang": "Пожалуйста, выберите язык / Please choose a language:",
        "welcome": ("🌸 Добро пожаловать в <b>{salon}</b>!\n\n"
                    "Здесь можно записаться к мастеру за минуту — без звонков и ожидания ответа.\n"
                    "Я напомню о визите заранее, а перенести или отменить запись можно в пару нажатий."),
        "ask_contact": ("Чтобы мастер знал, кого ждать, поделитесь, пожалуйста, номером телефона — "
                        "кнопкой ниже. Номер нужен только для связи по записи."),
        "btn_share_contact": "📱 Поделиться номером",
        "contact_saved": "Спасибо, {name}! Готово — выбирайте, что вас интересует 👇",
        "not_own_contact": "Пожалуйста, отправьте свой номер кнопкой ниже 🙏",
        "demo_banner": ("ℹ️ Это демонстрационный бот. Записи тестовые, салон вымышленный. "
                        "Можно открыть и админ-панель — посмотреть, как всё выглядит для владельца."),
        "menu_book": "📅 Записаться",
        "menu_my": "🗓 Мои записи",
        "menu_prices": "💇 Услуги и цены",
        "menu_masters": "👩‍🎨 Мастера",
        "menu_contacts": "📍 Контакты",
        "menu_reviews": "⭐ Отзывы",
        "menu_admin": "👑 Админ-панель",
        "menu_order": "💼 Хочу такой бот",
        "menu_lang": "🌐 Язык",
        "menu_hint": "Главное меню 👇",
        "pick_category": "Шаг 1 из 4. Выберите направление:",
        "pick_service": "Шаг 1 из 4. Выберите услугу:",
        "pick_master": "Шаг 2 из 4. Выберите мастера:",
        "any_master": "✨ Любой свободный мастер",
        "pick_date": "Шаг 3 из 4. Выберите дату:",
        "pick_time": "Шаг 4 из 4. Свободное время на {date}:",
        "no_slots": "На эту дату свободного времени нет 😔 Пожалуйста, выберите другой день.",
        "confirm": ("Проверьте, пожалуйста, запись:\n\n"
                    "💇 {service}\n👩‍🎨 Мастер: {master}\n📅 {date}, {time}\n⏱ {minutes} мин\n💰 {price}\n\n"
                    "Всё верно?"),
        "btn_confirm": "✅ Подтвердить",
        "btn_back": "« Назад",
        "btn_cancel_flow": "✖️ Отмена",
        "booked": ("🎉 Вы записаны!\n\n💇 {service}\n👩‍🎨 {master}\n📅 {date}, {time}\n📍 {address}\n\n"
                   "Я напомню за день и за 2 часа до визита. Ждём вас!"),
        "slot_taken": "Ой, это время только что заняли 😔 Пожалуйста, выберите другое.",
        "flow_cancelled": "Хорошо, запись не создана. Возвращаю в меню.",
        "my_empty": "У вас пока нет предстоящих записей. Нажмите «📅 Записаться», чтобы выбрать время.",
        "my_item": "📅 {date}, {time}\n💇 {service}\n👩‍🎨 {master}",
        "btn_reschedule": "🔁 Перенести",
        "btn_cancel_booking": "❌ Отменить",
        "ask_cancel": "Точно отменить запись на {date}, {time}?",
        "btn_yes_cancel": "Да, отменить",
        "btn_no": "Нет, оставить",
        "cancelled": "Запись отменена. Будем рады видеть вас в другой раз 🌸",
        "reschedule_start": "Выберите новую дату для записи «{service}»:",
        "rescheduled": "✅ Запись перенесена на {date}, {time}. Спасибо, что предупредили!",
        "prices_title": "💇 <b>Услуги и цены</b>\n",
        "masters_title": "👩‍🎨 <b>Наши мастера</b>\n",
        "contacts": ("📍 <b>{salon}</b>\n{address}\n📞 {phone}\n🕙 Ежедневно {opens}–{closes}\n\n"
                     "Ниже — точка на карте 👇"),
        "reviews_title": "⭐ <b>Отзывы</b> — средняя оценка {avg} из 5 ({n})\n",
        "reviews_empty": "Отзывов пока нет — ваш может стать первым 🙂",
        "remind_24h": "🔔 Напоминаем: завтра в {time} вас ждёт {master} — «{service}».\nВсё в силе?",
        "remind_2h": "⏰ Через 2 часа, в {time}, — «{service}» у мастера {master}. До встречи!",
        "btn_im_coming": "👍 Приду",
        "coming_ok": "Отлично, ждём вас! 🌸",
        "ask_review": "Как вам визит «{service}» у мастера {master}? Оцените, пожалуйста:",
        "review_thanks": "Спасибо за оценку! Если хотите, напишите пару слов о визите одним сообщением — или просто продолжайте пользоваться ботом.",
        "review_text_thanks": "Спасибо за отзыв, это очень помогает мастерам 💜",
        "admin_new": "🆕 <b>Новая запись</b>\n{client}\n💇 {service}\n👩‍🎨 {master}\n📅 {date}, {time}",
        "admin_cancel": "❌ <b>Клиент отменил запись</b>\n{client}\n💇 {service}\n📅 {date}, {time}",
        "admin_moved": "🔁 <b>Запись перенесена</b>\n{client}\n💇 {service}\n📅 {date}, {time}",
        "admin_low_rating": "⚠️ Низкая оценка {rating}/5 от {client} ({service}, {master}). Стоит связаться с клиентом.",
        "admin_demo_note": "\n\n<i>Так это уведомление увидит администратор салона.</i>",
        "admin_title": "👑 <b>Админ-панель</b>\nВыберите раздел:",
        "admin_demo_hint": "\n<i>Демо-режим: данные других клиентов скрыты, управлять можно своими записями.</i>",
        "adm_today": "📋 Сегодня",
        "adm_tomorrow": "📋 Завтра",
        "adm_pick_day": "📆 Выбрать дату",
        "adm_days_off": "🚫 Выходные мастеров",
        "adm_broadcast": "📣 Рассылка",
        "adm_stats": "📊 Статистика",
        "adm_day_empty": "На {date} записей нет.",
        "adm_day_title": "📋 <b>Записи на {date}</b> ({n})\n",
        "adm_booking_line": "{time}–{end} · {master} · {service}\n   {client} · {status}",
        "st_active": "ожидается", "st_done": "пришёл ✅", "st_noshow": "не пришёл 🚫", "st_cancelled": "отменена",
        "adm_pick_booking": "Нажмите на запись, чтобы изменить статус:",
        "adm_done": "✅ Пришёл",
        "adm_noshow": "🚫 Не пришёл",
        "adm_cancel": "❌ Отменить",
        "adm_only_own": "В демо-режиме можно управлять только своими записями 🙂",
        "adm_status_set": "Статус обновлён.",
        "adm_cancelled_by_salon": "К сожалению, салон отменил вашу запись на {date}, {time}. Приносим извинения — выберите, пожалуйста, другое время.",
        "adm_pick_master": "Выберите мастера:",
        "adm_pick_off_day": "Нажмите на дату, чтобы поставить или снять выходной у мастера {master}:",
        "adm_off_only_owner": "В демо-режиме выходные меняет только владелец бота — чтобы не мешать другим посетителям. Вот как выглядит расписание:",
        "adm_off_set": "Готово: {date} — {state}.",
        "off_on": "выходной", "off_off": "рабочий день",
        "adm_broadcast_ask": "Напишите текст рассылки одним сообщением (например, акция недели):",
        "adm_broadcast_demo": "Демо-режим: рассылка отправлена только вам, чтобы не беспокоить других.",
        "adm_broadcast_done": "Рассылка отправлена: {n} получателей.",
        "adm_stats_text": ("📊 <b>Статистика за 30 дней</b>\n"
                           "Записей: {total} (отмен: {cancelled})\n"
                           "Ожидаемая выручка: {revenue}\n"
                           "Популярная услуга: {top_service}\n"
                           "Самый загруженный мастер: {top_master}\n"
                           "Клиентов в базе: {users}\n"
                           "Средняя оценка: {avg} ({n_reviews} отзывов)"),
        "order_intro": ("💼 Такой бот можно сделать и для вашего бизнеса — салона, клиники, студии, автосервиса.\n\n"
                        "Опишите, пожалуйста, одним сообщением: чем вы занимаетесь и что хотите автоматизировать. "
                        "Разработчик ответит вам прямо здесь, в этом чате."),
        "order_sent": "Спасибо! Заявка передана разработчику, он ответит здесь в течение дня 🙌",
        "dev_reply": "💬 <b>Ответ разработчика:</b>\n\n{text}",
        "sent_to_dev": "✉️ Сообщение передано разработчику.",
        "unknown": "Пожалуйста, воспользуйтесь кнопками меню 👇",
    },
    "en": {
        "choose_lang": "Please choose a language / Пожалуйста, выберите язык:",
        "welcome": ("🌸 Welcome to <b>{salon}</b>!\n\n"
                    "Book an appointment in under a minute — no calls, no waiting for a reply.\n"
                    "I'll remind you before the visit, and you can reschedule or cancel in a couple of taps."),
        "ask_contact": ("So your stylist knows who to expect, please share your phone number using the button "
                        "below. It is used only to contact you about your booking."),
        "btn_share_contact": "📱 Share my number",
        "contact_saved": "Thank you, {name}! All set — pick what you need 👇",
        "not_own_contact": "Please send your own number with the button below 🙏",
        "demo_banner": ("ℹ️ This is a demo bot. Bookings are for testing and the salon is fictional. "
                        "You can also open the admin panel to see how everything looks for the owner."),
        "menu_book": "📅 Book",
        "menu_my": "🗓 My bookings",
        "menu_prices": "💇 Services & prices",
        "menu_masters": "👩‍🎨 Stylists",
        "menu_contacts": "📍 Contacts",
        "menu_reviews": "⭐ Reviews",
        "menu_admin": "👑 Admin panel",
        "menu_order": "💼 I want this bot",
        "menu_lang": "🌐 Language",
        "menu_hint": "Main menu 👇",
        "pick_category": "Step 1 of 4. Choose a category:",
        "pick_service": "Step 1 of 4. Choose a service:",
        "pick_master": "Step 2 of 4. Choose a stylist:",
        "any_master": "✨ Any available stylist",
        "pick_date": "Step 3 of 4. Choose a date:",
        "pick_time": "Step 4 of 4. Available times on {date}:",
        "no_slots": "No free time on this date 😔 Please choose another day.",
        "confirm": ("Please check your booking:\n\n"
                    "💇 {service}\n👩‍🎨 Stylist: {master}\n📅 {date}, {time}\n⏱ {minutes} min\n💰 {price}\n\n"
                    "Is everything correct?"),
        "btn_confirm": "✅ Confirm",
        "btn_back": "« Back",
        "btn_cancel_flow": "✖️ Cancel",
        "booked": ("🎉 You're booked!\n\n💇 {service}\n👩‍🎨 {master}\n📅 {date}, {time}\n📍 {address}\n\n"
                   "I'll remind you a day before and 2 hours before. See you soon!"),
        "slot_taken": "Oops, someone has just taken this time 😔 Please choose another one.",
        "flow_cancelled": "No problem, the booking was not created. Back to the menu.",
        "my_empty": "You have no upcoming bookings yet. Tap “📅 Book” to pick a time.",
        "my_item": "📅 {date}, {time}\n💇 {service}\n👩‍🎨 {master}",
        "btn_reschedule": "🔁 Reschedule",
        "btn_cancel_booking": "❌ Cancel",
        "ask_cancel": "Cancel your booking on {date} at {time}?",
        "btn_yes_cancel": "Yes, cancel",
        "btn_no": "No, keep it",
        "cancelled": "Your booking has been cancelled. We'd be glad to see you another time 🌸",
        "reschedule_start": "Choose a new date for “{service}”:",
        "rescheduled": "✅ Your booking has been moved to {date}, {time}. Thank you for letting us know!",
        "prices_title": "💇 <b>Services & prices</b>\n",
        "masters_title": "👩‍🎨 <b>Our stylists</b>\n",
        "contacts": ("📍 <b>{salon}</b>\n{address}\n📞 {phone}\n🕙 Daily {opens}–{closes}\n\n"
                     "The location is below 👇"),
        "reviews_title": "⭐ <b>Reviews</b> — average rating {avg} of 5 ({n})\n",
        "reviews_empty": "No reviews yet — yours could be the first 🙂",
        "remind_24h": "🔔 A friendly reminder: tomorrow at {time} {master} is expecting you for “{service}”.\nStill on?",
        "remind_2h": "⏰ In 2 hours, at {time}: “{service}” with {master}. See you soon!",
        "btn_im_coming": "👍 I'll be there",
        "coming_ok": "Great, see you soon! 🌸",
        "ask_review": "How was your “{service}” with {master}? Please rate your visit:",
        "review_thanks": "Thank you for the rating! If you like, send a few words about your visit in one message — or just keep using the bot.",
        "review_text_thanks": "Thank you for your review, it really helps our stylists 💜",
        "admin_new": "🆕 <b>New booking</b>\n{client}\n💇 {service}\n👩‍🎨 {master}\n📅 {date}, {time}",
        "admin_cancel": "❌ <b>Client cancelled</b>\n{client}\n💇 {service}\n📅 {date}, {time}",
        "admin_moved": "🔁 <b>Booking moved</b>\n{client}\n💇 {service}\n📅 {date}, {time}",
        "admin_low_rating": "⚠️ Low rating {rating}/5 from {client} ({service}, {master}). Worth reaching out.",
        "admin_demo_note": "\n\n<i>This is how the salon administrator will see this notification.</i>",
        "admin_title": "👑 <b>Admin panel</b>\nChoose a section:",
        "admin_demo_hint": "\n<i>Demo mode: other clients' data is hidden, and you can manage your own bookings.</i>",
        "adm_today": "📋 Today",
        "adm_tomorrow": "📋 Tomorrow",
        "adm_pick_day": "📆 Pick a date",
        "adm_days_off": "🚫 Stylists' days off",
        "adm_broadcast": "📣 Broadcast",
        "adm_stats": "📊 Statistics",
        "adm_day_empty": "No bookings on {date}.",
        "adm_day_title": "📋 <b>Bookings on {date}</b> ({n})\n",
        "adm_booking_line": "{time}–{end} · {master} · {service}\n   {client} · {status}",
        "st_active": "expected", "st_done": "came ✅", "st_noshow": "no-show 🚫", "st_cancelled": "cancelled",
        "adm_pick_booking": "Tap a booking to change its status:",
        "adm_done": "✅ Came",
        "adm_noshow": "🚫 No-show",
        "adm_cancel": "❌ Cancel",
        "adm_only_own": "In demo mode you can manage only your own bookings 🙂",
        "adm_status_set": "Status updated.",
        "adm_cancelled_by_salon": "Unfortunately, the salon had to cancel your booking on {date} at {time}. We apologise — please choose another time.",
        "adm_pick_master": "Choose a stylist:",
        "adm_pick_off_day": "Tap a date to set or remove a day off for {master}:",
        "adm_off_only_owner": "In demo mode only the bot owner can change days off, so other visitors aren't affected. This is how the schedule looks:",
        "adm_off_set": "Done: {date} is now a {state}.",
        "off_on": "day off", "off_off": "working day",
        "adm_broadcast_ask": "Send the broadcast text in one message (for example, this week's offer):",
        "adm_broadcast_demo": "Demo mode: the broadcast was sent only to you, so no one else is disturbed.",
        "adm_broadcast_done": "Broadcast sent to {n} recipients.",
        "adm_stats_text": ("📊 <b>Last 30 days</b>\n"
                           "Bookings: {total} (cancelled: {cancelled})\n"
                           "Expected revenue: {revenue}\n"
                           "Top service: {top_service}\n"
                           "Busiest stylist: {top_master}\n"
                           "Clients in database: {users}\n"
                           "Average rating: {avg} ({n_reviews} reviews)"),
        "order_intro": ("💼 A bot like this can be built for your business too — a salon, clinic, studio or car service.\n\n"
                        "Please describe in one message what your business does and what you'd like to automate. "
                        "The developer will reply right here in this chat."),
        "order_sent": "Thank you! Your request has been passed to the developer, who will reply here within a day 🙌",
        "dev_reply": "💬 <b>Developer's reply:</b>\n\n{text}",
        "sent_to_dev": "✉️ Your message has been passed to the developer.",
        "unknown": "Please use the menu buttons 👇",
    },
}

WEEKDAYS = {"ru": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"], "en": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]}
MONTHS = {
    "ru": ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября",
           "ноября", "декабря"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}


def t(lang: str | None, key: str, **kw) -> str:
    lang = lang if lang in TEXTS else "ru"
    return TEXTS[lang][key].format(**kw) if kw else TEXTS[lang][key]


def all_variants(key: str) -> set[str]:
    return {TEXTS[lang][key] for lang in TEXTS}


def fmt_date(d, lang: str | None) -> str:
    lang = lang if lang in TEXTS else "ru"
    if lang == "ru":
        return f"{WEEKDAYS['ru'][d.weekday()]}, {d.day} {MONTHS['ru'][d.month - 1]}"
    return f"{WEEKDAYS['en'][d.weekday()]}, {MONTHS['en'][d.month - 1]} {d.day}"


def fmt_price(amount: int, lang: str | None) -> str:
    from .catalog import SALON
    cur = SALON["currency_en"] if lang == "en" else SALON["currency_ru"]
    return f"{amount:,}".replace(",", " ") + f" {cur}"

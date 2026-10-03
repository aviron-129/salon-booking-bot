# Lavanda Beauty — Telegram booking bot for a beauty salon

A production-style Telegram bot that lets clients of a hair & beauty salon book appointments in under a minute,
and gives the owner a simple admin panel right inside Telegram.

**Live demo:** [@lavanda_beauty_demo_bot](https://t.me/lavanda_beauty_demo_bot) — the salon is fictional, feel free
to book, reschedule, cancel and open the admin panel.

## Features

**For clients**
- Russian / English interface, onboarding with one-tap phone sharing
- 4-step booking: category → service → stylist (or "any available") → date → free time slot
- Real availability: working hours, service duration, stylists' weekly and one-off days off, existing bookings
- Race-safe confirmation (the slot is re-checked right before saving)
- "My bookings": reschedule or cancel in two taps
- Reminders 24 h and 2 h before the visit, with "I'll be there / Reschedule / Cancel" buttons
- Rating request after the visit, optional text review; public reviews page with the average rating
- Services & prices, stylists, contacts with a map pin

**For the salon owner**
- Instant notifications about new, moved and cancelled bookings; alert on low ratings
- Bookings for today / tomorrow / any date, mark as *came* / *no-show* / *cancel* (the client is notified)
- Stylists' days off calendar
- Broadcast to all clients
- 30-day statistics: bookings, cancellations, expected revenue, top service, busiest stylist, average rating

**Demo mode** (`DEMO_MODE=1`): any visitor can open the admin panel; other clients' names and phones are masked and
visitors can manage only their own bookings. A built-in "I want this bot" form sends requests to the developer,
who can reply through the bot.

## Tech stack

Python 3.12 · aiogram 3 · SQLite (aiosqlite) · asyncio background worker for reminders · pytest ·
Docker / Docker Compose

```
bot/
  __main__.py      entry point, dispatcher and routers
  config.py        settings from environment
  catalog.py       services, stylists, salon info
  slots.py         pure scheduling logic (covered by tests)
  db.py            SQLite data layer
  common.py        availability, notifications, demo masking
  reminders.py     reminders and review requests
  handlers/        start & info, booking flow, my bookings & reviews, admin panel, leads/relay
tests/             pytest
```

## Run locally

```bash
python -m venv .venv && .venv/Scripts/activate   # Windows; use bin/activate on Linux/macOS
pip install -r requirements.txt
cp .env.example .env   # put your BOT_TOKEN and OWNER_ID
python -m bot
```

With Docker:

```bash
docker compose up -d --build
```

Tests:

```bash
pip install pytest && pytest -q
```

## Adapting for a real salon

Edit `bot/catalog.py` (services, prices, durations, stylists, working hours, address), set `DEMO_MODE=0` and your
Telegram id in `OWNER_ID`.

---
Built by Mahmud Aliev — Python developer, Tashkent. Telegram: [@mahmud_py_dev](https://t.me/mahmud_py_dev)

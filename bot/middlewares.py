from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class UserMiddleware(BaseMiddleware):
    """Loads the user row once per update and exposes `user` and `lang` to handlers."""

    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject, data: dict[str, Any]) -> Any:
        tg_user = data.get("event_from_user")
        db = data["db"]
        user = await db.get_user(tg_user.id) if tg_user else None
        data["user"] = user
        data["lang"] = (user["lang"] if user else None) or "ru"
        return await handler(event, data)

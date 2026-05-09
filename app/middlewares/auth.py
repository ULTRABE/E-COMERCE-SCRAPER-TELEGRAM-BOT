from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Any, Callable, Awaitable
from app.config import settings

class OwnerOnlyMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]], event: TelegramObject, data: dict[str, Any]) -> Any:
        user = data.get("event_from_user")
        if not user or user.id != settings.owner_id:
            if hasattr(event, "answer"):
                await event.answer("⛔ Access denied. Owner-only bot.")
            return
        return await handler(event, data)

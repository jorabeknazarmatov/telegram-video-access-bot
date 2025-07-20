from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any
import os


class RoleCheckerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = message.from_user.id
        admin_ids = set(map(int, os.getenv("ADMIN_ID").split(',')))
        data["role"] = "admin" if user_id in admin_ids else "user"
        return await handler(message, data)

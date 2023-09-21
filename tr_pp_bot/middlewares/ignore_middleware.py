import logging
from typing import Callable, Any, Awaitable

from aiogram.types import Message, Update

from tr_pp_bot.config import env

logger = logging.getLogger('AUTH')


async def ignore_middleware(
    handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
    update: Update,
    data: dict[str, Any]
) -> Any:
    supported_chats = [env.MAIN_CHAT_ID, env.ADMIN_CHAT_ID, env.FLOOD_CHAT_ID]

    if update.message and update.message.chat.id in supported_chats or \
        update.callback_query and update.callback_query.message.chat.id in supported_chats or \
            update.event.chat and update.event.chat.id in supported_chats:
        return await handler(update, data)
    else:
        logger.warning(f'Unknown chat is attempting to use the bot. Ignoring...')

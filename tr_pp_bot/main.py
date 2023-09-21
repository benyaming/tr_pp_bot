import asyncio

import betterlogging
from aiogram import Bot, Dispatcher

from tr_pp_bot.config import env
from tr_pp_bot.apps import get_apps_router
from tr_pp_bot.apps.base_command import COMMANDS, clean_my_commands
from tr_pp_bot.middlewares.ignore_middleware import ignore_middleware


ALLOWED_UPDATES = ['chat_member', 'message', 'callback_query']

betterlogging.basic_colorized_config(level=betterlogging.INFO)


async def main() -> None:
    bot = Bot(env.BOT_TOKEN, parse_mode='HTML')
    dp = Dispatcher()

    dp.include_router(get_apps_router())
    dp.update.outer_middleware.register(ignore_middleware)

    await clean_my_commands(bot)

    for scope, commands in COMMANDS.items():
        await bot.set_my_commands(commands, scope)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)


asyncio.run(main())

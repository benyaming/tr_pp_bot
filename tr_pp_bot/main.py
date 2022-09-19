from aiogram.types import BotCommandScope, BotCommandScopeAllChatAdministrators, BotCommandScopeAllGroupChats, \
    BotCommandScopeChatAdministrators, BotCommandScopeChat

from config import env

import aiogram_metrics
import betterlogging as bl
from aiogram.utils.executor import start_polling

from tr_pp_bot.misc import dp, bot
from tr_pp_bot.apps.commands import register_commands, PUBLIC_COMMANDS, ADMIN_COMMANDS
from tr_pp_bot.apps.events import register_events

bl.basic_colorized_config(level=bl.INFO)
logger = bl.getLogger(__name__)


async def on_start(_):
    logger.info('Starting {{PROJECT NAME}} tr_pp_bot...')

    if env.METRICS_DSN:
        await aiogram_metrics.register(env.METRICS_DSN, env.METRICS_TABLE_NAME)

    register_commands(dp)
    register_events(dp)
    ADMIN_COMMANDS.extend(PUBLIC_COMMANDS)

    await bot.delete_my_commands()
    await bot.delete_my_commands(BotCommandScopeAllGroupChats())
    await bot.delete_my_commands(BotCommandScopeAllChatAdministrators())

    await bot.set_my_commands(PUBLIC_COMMANDS, scope=BotCommandScopeAllGroupChats())
    await bot.set_my_commands(ADMIN_COMMANDS, scope=BotCommandScopeAllChatAdministrators())


async def on_down(_):
    from aiogram_metrics.api import close
    await close()


if __name__ == '__main__':
    start_polling(dp, on_startup=on_start, skip_updates=True)

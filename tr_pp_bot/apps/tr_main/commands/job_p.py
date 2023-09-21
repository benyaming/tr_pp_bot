from aiogram.types import Message
from aiogram import Bot

from tr_pp_bot.apps.base_command import BaseCommand
from tr_pp_bot.config import env


class JobCommand(BaseCommand):
    command_text = 'job_p'
    command_description = 'Запостить в фид 2'
    chat_id = env.MAIN_CHAT_ID

    async def execute(self, message: Message, bot: Bot) -> None:
        await bot.send_message(message.chat.id, 'command works')

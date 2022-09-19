from aiogram.types import Message

from ..base_command import BasePublicCommand
from tr_pp_bot.misc import bot


class TestCommand(BasePublicCommand):

    is_admin_required = False
    command_text = 'test'
    command_description = 'a public command'

    async def execute(self, msg: Message) -> None:
        target_user = msg.reply_to_message.from_user
        await bot.send_message(msg.chat.id, f'User {target_user.first_name} banned (no)')

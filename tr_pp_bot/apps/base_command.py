from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Iterable

from aiogram import Router, Bot
from aiogram.filters import Filter, Command
from aiogram.types import Message, BotCommand, BotCommandScope
from aiogram.types.bot_command_scope_chat import BotCommandScopeChat
from aiogram.types.bot_command_scope_all_group_chats import BotCommandScopeAllGroupChats
from aiogram.types.bot_command_scope_chat_administrators import BotCommandScopeChatAdministrators
from aiogram.types.bot_command_scope_all_chat_administrators import BotCommandScopeAllChatAdministrators

from tr_pp_bot.config import env


COMMANDS: dict[BotCommandScope, list[BotCommand]] = defaultdict(list)


async def clean_my_commands(bot: Bot):
    chats = [env.MAIN_CHAT_ID]

    for chat in chats:
        await bot.delete_my_commands(BotCommandScopeChat(chat_id=chat))
        await bot.delete_my_commands(BotCommandScopeChatAdministrators(chat_id=chat))

    await bot.delete_my_commands(BotCommandScopeAllGroupChats())
    await bot.delete_my_commands(BotCommandScopeAllChatAdministrators())


class MyCommand:
    chat_id: int
    command: Command


class AdminFilter(Filter):

    def __init__(self, *_, **__):
        super().__init__()

    async def __call__(self, message: Message, bot: Bot) -> bool:
        admins = await bot.get_chat_administrators(message.chat.id)
        if message.from_user.id not in [a.user.id for a in admins]:
            await message.reply('<i>Эта команда доступна только администраторам</i>')
            return False
        return True


class BaseCommand(ABC):

    command_text: str
    command_description: str
    command_args: ...
    is_admin_required: bool = False
    chat_id: int | None = None

    def __init__(
            self,
            router: Router,
            extra_filters: Iterable[Filter] | None = None
    ) -> None:
        filters = [
            Command(self.command_text)
        ]

        if self.is_admin_required:
            filters.append(AdminFilter())
        if extra_filters:
            filters.extend(extra_filters)

        router.message.register(self.execute, *filters)

        command = BotCommand(command=self.command_text, description=self.command_description)

        if self.is_admin_required:
            if self.chat_id:
                COMMANDS[BotCommandScopeChatAdministrators(chat_id=self.chat_id)].append(command)
            else:
                COMMANDS[BotCommandScopeAllChatAdministrators()].append(command)
        else:
            if self.chat_id:
                COMMANDS[BotCommandScopeChat(chat_id=self.chat_id)].append(command)
                COMMANDS[BotCommandScopeChatAdministrators(chat_id=self.chat_id)].append(command)
            else:
                COMMANDS[BotCommandScopeAllGroupChats()].append(command)
                COMMANDS[BotCommandScopeAllChatAdministrators()].append(command)

    @abstractmethod
    async def execute(self, msg: Message, bot: Bot) -> None:
        raise NotImplemented()

from abc import ABC, abstractmethod
from typing import Iterable

from aiogram import Dispatcher
from aiogram.dispatcher.filters.builtin import Command, AdminFilter, Filter
from aiogram.types import Message, BotCommand

PUBLIC_COMMANDS: list[BotCommand] = []
ADMIN_COMMANDS: list[BotCommand] = []


class BasePublicCommand(ABC):

    command_text: str
    command_description: str
    command_args: ...
    is_admin_required: bool

    def register(self, dp: Dispatcher, extra_filters: Iterable[Filter] | None) -> None:
        filters = [
            Command([self.command_text])
        ]

        if self.is_admin_required:
            filters.append(AdminFilter())
        if extra_filters:
            filters.extend(extra_filters)

        dp.register_message_handler(self.execute, *filters)

    @abstractmethod
    async def execute(self, msg: Message) -> None:
        ...

    def __init__(self, dp: Dispatcher, extra_filters: Iterable[Filter] | None = None):
        self.register(dp, extra_filters)

    def __init_subclass__(cls, **kwargs):
        target = ADMIN_COMMANDS if cls.is_admin_required else PUBLIC_COMMANDS
        target.append(BotCommand(cls.command_text, cls.command_description))

from abc import ABC, abstractmethod
from typing import Iterable

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Filter, AdminFilter
from aiogram.types import Message


class BaseEvent(ABC):

    filters: list[Filter]
    is_admin_required: bool = False

    def register(self, dp: Dispatcher) -> None:
        if self.is_admin_required:
            self.filters.append(AdminFilter())

        dp.register_message_handler(self.execute, *self.filters)

    @abstractmethod
    async def execute(self, msg: Message) -> None:
        ...

    def __init__(self, dp: Dispatcher):
        self.register(dp)



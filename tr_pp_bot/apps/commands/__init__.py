from aiogram import Dispatcher

from .test import TestCommand
from .test_admin import TestAdminCommand
from ..base_command import PUBLIC_COMMANDS, ADMIN_COMMANDS


__all__ = [
    'PUBLIC_COMMANDS',
    'ADMIN_COMMANDS',
    'register_commands'
]


def register_commands(dp: Dispatcher):
    TestCommand(dp)
    TestAdminCommand(dp)

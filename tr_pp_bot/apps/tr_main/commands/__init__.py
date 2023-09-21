from typing import Type

from .job import JobCommand
from ...base_command import BaseCommand


def get_commands() -> list[Type[BaseCommand]]:
    return []

from typing import Type

from .job import JobCommand
from .job_p import JobCommand as J2
from ...base_command import BaseCommand


def get_commands() -> list[Type[BaseCommand]]:
    return [JobCommand, J2]

from aiogram import Dispatcher

from . import captcha


def register_events(dp: Dispatcher) -> None:
    captcha.register(dp)

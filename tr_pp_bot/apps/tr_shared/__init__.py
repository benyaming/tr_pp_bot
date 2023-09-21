from aiogram import Router, F

from tr_pp_bot.config import env


def get_shared_router() -> Router:
    router = Router()
    router.message.register()

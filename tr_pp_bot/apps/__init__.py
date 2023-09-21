from aiogram import Router

from .tr_main import get_main_router


def get_apps_router() -> Router:
    router = Router()

    router.include_router(get_main_router())

    return router


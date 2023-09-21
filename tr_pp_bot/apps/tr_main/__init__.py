from aiogram import Bot, Router, F

from ...config import env
from .events import get_events_routers
from .commands import get_commands


_MAIN_FILTER = F.chat.id == env.MAIN_CHAT_ID


def get_main_router() -> Router:
    router = Router()
    [router.include_router(r) for r in get_events_routers()]

    for command in get_commands():
        command(router)

    return router

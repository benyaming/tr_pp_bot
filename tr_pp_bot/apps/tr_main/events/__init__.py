from aiogram import Router

from . import capcha


def get_events_routers() -> list[Router]:
    events = [capcha]
    return [event.get_router() for event in events]

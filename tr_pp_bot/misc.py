import asyncio

from aiogram import Bot, Dispatcher, types

from .config import env


loop = asyncio.get_event_loop()
bot = Bot(env.BOT_TOKEN, loop, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

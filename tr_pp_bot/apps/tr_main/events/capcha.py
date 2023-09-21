import random
import logging
from typing import Tuple
from asyncio import sleep, create_task

from aiogram import Bot, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    ChatPermissions,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ChatMemberRestricted,
    CallbackQuery,
    ChatMemberUpdated
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER

from tr_pp_bot.config import env


logger = logging.getLogger('captcha')

STORAGE = {}
ATTEMPTS = []

RESTRICT_PERMISSIONS = ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_other_messages=False
    )
ALLOW_PERMISSIONS = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_send_polls=True,
        can_invite_users=True,
        can_pin_messages=True,
        can_change_info=True
    )


def get_keyboard(user_id: int, button_options: list[str]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    random.shuffle(button_options)

    row = []
    line_length = 0
    for answer in button_options:
        if (line_length + len(answer) > 20) or (line_length + len(answer) > 5 and len(row) > 2):
            kb.row(*row)
            line_length = 0
            row = []

        row.append(InlineKeyboardButton(
            text=answer,
            callback_data=f'{user_id}:{answer}'
        ))
        line_length += len(answer)

    if row:
        kb.row(*row)

    return kb.as_markup()


async def on_shutdown(bot: Bot):
    for token in STORAGE:
        await stop_user_track(bot, token)


async def stop_user_track(bot: Bot, token: tuple[int, int], kick: int = False):
    user_id, chat_id = token

    try:
        msg_id = STORAGE[token]
    except KeyError:
        logger.info(f'Got a stale user. Removing restrictions...')
        await bot.restrict_chat_member(chat_id, user_id, permissions=ALLOW_PERMISSIONS)
        return

    logger.info(f'Stop user track for user {user_id}')

    if kick:
        logger.info(f'Kicking user {user_id}')
        await bot.ban_chat_member(chat_id, user_id)
    else:
        logger.info(f'Grant allow permissions to user {user_id}')
        await bot.restrict_chat_member(chat_id, user_id, permissions=ALLOW_PERMISSIONS)

    logger.info(f'Deleting token {token} from storage.')

    if token in ATTEMPTS:
        ATTEMPTS.remove(token)
    del STORAGE[token]

    logger.info(f'Deletting message {msg_id}')
    await bot.delete_message(chat_id, msg_id)


async def init_user_track(bot: Bot, user_id: int, chat_id: int, msg_id: int):
    token = (user_id, chat_id)
    STORAGE[token] = msg_id

    await sleep(env.MAIN_CAPTCHA_TTL)

    if token in STORAGE:
        await stop_user_track(bot, token, kick=True)


def validate_attempt(token: Tuple[int, int]) -> bool:
    if token in ATTEMPTS:
        return False

    ATTEMPTS.append(token)
    return True


async def on_user_join(msg: ChatMemberUpdated, bot: Bot):
    user_status = msg.new_chat_member
    new_user = msg.new_chat_member.user

    if isinstance(user_status, ChatMemberRestricted):
        logger.info(f'User {msg.from_user.id} already has restrictions. Skipping...')
        return

    if new_user.id != msg.from_user.id:
        logger.info(f'User {msg.from_user.first_name} added user {new_user.first_name}. Skipping...')
        return

    logger.info(f'New chat_member detected! id: {new_user.id}. Restricting...')
    await bot.restrict_chat_member(
        msg.chat.id,
        new_user.id,
        permissions=RESTRICT_PERMISSIONS
    )

    kb = get_keyboard(msg.from_user.id, env.MAIN_CAPTCHA_ANSWERS)

    link = f'<a href="tg://user?id={new_user.id}">{new_user.first_name}</a>'
    resp = f'👋🏻, {link}! \n{env.MAIN_CAPTCHA_QUESTION}'
    answer = await bot.send_message(msg.chat.id, resp, reply_markup=kb)
    create_task(init_user_track(
        bot=bot,
        user_id=new_user.id,
        chat_id=msg.chat.id,
        msg_id=answer.message_id,
    ))


async def on_user_left(msg: ChatMemberUpdated, bot: Bot):
    logger.info(f'User {msg.from_user.id} left the group {msg.chat.id}')
    token = (msg.from_user.id, msg.chat.id)
    if token in STORAGE:
        logger.info(f'Removing token {token} from storage')
        await stop_user_track(bot, token)
    # await bot.send_message(msg.chat.id, f'bye, {msg.from_user.first_name}')


async def on_capcha_attempt(call: CallbackQuery, bot: Bot):
    user_id, answer = call.data.split(':')

    if call.from_user.id != int(user_id):
        answer = random.choice(env.MAIN_CAPTCHA_WRONG_ANSWER_LIST)
        await call.answer(answer, show_alert=True)
        return

    if answer != env.MAIN_CAPTCHA_RIGHT_ANSWER:
        allow_attempt = validate_attempt((call.from_user.id, call.message.chat.id))
        logger.debug(f'{call.from_user.id} entered wrong value [{answer}]!')

        if allow_attempt:
            async def update_kb():
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        reply_markup=get_keyboard(call.from_user.id, env.MAIN_CAPTCHA_ANSWERS)
                    )
                except TelegramBadRequest:
                    return await update_kb()

            await update_kb()

            await call.answer(env.MAIN_CAPTCHA_WRONG_ANSWER_ALERT, show_alert=True)
            return
        else:
            return await stop_user_track(bot, (call.from_user.id, call.message.chat.id), kick=True)

    await call.answer(env.MAIN_CAPTCHA_RIGHT_ANSWER)
    logger.info(f'{call.from_user.id} passed the test! Removing restrictions...')

    token = (call.from_user.id, call.message.chat.id)
    await stop_user_track(bot, token)
    logger.info(f'{call.from_user.id} allowed to chat!')


def get_router() -> Router:
    router = Router()

    router.chat_member.register(on_user_join, F.chat.id == env.MAIN_CHAT_ID, ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
    router.chat_member.register(on_user_left, F.chat.id == env.MAIN_CHAT_ID, ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
    router.callback_query.register(on_capcha_attempt, F.message.chat.id == env.MAIN_CHAT_ID)
    router.shutdown.register(on_shutdown)
    return router

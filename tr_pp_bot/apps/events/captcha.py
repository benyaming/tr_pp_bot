import random
import logging
from typing import Tuple
from asyncio import sleep

import aiogram_metrics
from aiogram import Dispatcher
from aiogram.types import (
    ContentTypes,
    Message,
    CallbackQuery,
    chat_member, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
)

from tr_pp_bot.config import env
from tr_pp_bot.misc import bot, loop


logger = logging.getLogger('captcha')
logger.setLevel(logging.INFO)
logger.info('test')

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
    kb = InlineKeyboardMarkup()
    # kb.row_width = 5

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

    return kb


async def on_shutdown(_):
    for token in STORAGE:
        await stop_user_track(token)

    await aiogram_metrics.close()


async def stop_user_track(token: Tuple[int, int], kick: int = False):
    user_id, chat_id = token
    msg_id, service_msg_id = STORAGE[token]
    logger.info(f'Stop user track for user {user_id}')

    if kick:
        aiogram_metrics.manual_track('Kick user')
        logger.info(f'Kicking user {user_id}')
        await bot.kick_chat_member(chat_id, user_id)
        await bot.delete_message(chat_id, service_msg_id)
    else:
        aiogram_metrics.manual_track('Allow user to join')
        logger.info(f'Grant allow permissions to user {user_id}')
        await bot.restrict_chat_member(chat_id, user_id, permissions=ALLOW_PERMISSIONS)

    logger.info(f'Deleting token {token} from storage.')

    if token in ATTEMPTS:
        ATTEMPTS.remove(token)
    del STORAGE[token]

    logger.info(f'Deletting message {msg_id}')
    await bot.delete_message(chat_id, msg_id)


@aiogram_metrics.track('Init user track')
async def init_user_track(user_id: int, chat_id: int, msg_id: int, service_msg_id: int):
    token = (user_id, chat_id)
    STORAGE[token] = (msg_id, service_msg_id)

    await sleep(env.CAPTCHA_TTL)

    if token in STORAGE:
        await stop_user_track(token, kick=True)


def validate_attempt(token: Tuple[int, int]) -> bool:
    if token in ATTEMPTS:
        return False

    ATTEMPTS.append(token)
    return True


async def handle_new_member(msg: Message):
    user_status = await bot.get_chat_member(msg.chat.id, msg.from_user.id)

    if isinstance(user_status, chat_member.ChatMemberRestricted):
        logger.info(f'User {msg.from_user.id} already has restrictions. Skipping...')
        return

    if len(msg.new_chat_members) > 0 and msg.new_chat_members[0].id != msg.from_user.id:
        logger.info(f'User {msg.from_user.id} added user {msg.new_chat_members[0].id}. Skipping...')
        return

    logger.info(f'New chat_member detected! id: {msg.from_user.id}. Restricting...')
    await bot.restrict_chat_member(msg.chat.id, msg.new_chat_members[0].id, permissions=RESTRICT_PERMISSIONS)

    kb = get_keyboard(msg.from_user.id, env.CAPTCHA_ANSWERS)

    answer = await msg.reply(env.CAPTCHA_QUESTION, reply_markup=kb)
    loop.create_task(init_user_track(
        user_id=msg.from_user.id,
        chat_id=msg.chat.id,
        msg_id=answer.message_id,
        service_msg_id=msg.message_id
    ))


async def handle_left_member(msg: Message):
    logger.info(f'User {msg.from_user.id} left the group {msg.chat.id}')
    token = (msg.from_user.id, msg.chat.id)
    if token in STORAGE:
        logger.info(f'Removing token {token} from storage')
        await stop_user_track(token)


async def handle_button(call: CallbackQuery):
    user_id, answer = call.data.split(':')

    if call.from_user.id != int(user_id):
        answer = random.choice(env.CAPTCHA_WRONG_ANSWER_LIST)
        await call.answer(answer, show_alert=True)
        return

    if answer != env.CAPTCHA_RIGHT_ANSWER:
        allow_attempt = validate_attempt((call.from_user.id, call.message.chat.id))
        logger.debug(f'{call.from_user.id} entered wrong value [{answer}]!')

        if allow_attempt:
            await bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=get_keyboard(call.from_user.id, env.CAPTCHA_ANSWERS)
            )
            await call.answer(env.CAPTCHA_WRONG_ANSWER_ALERT, show_alert=True)
            return
        else:
            return await stop_user_track((call.from_user.id, call.message.chat.id), kick=True)

    await call.answer(env.CAPTCHA_WRONG_ANSWER_ALERT)
    logger.info(f'{call.from_user.id} passed the test! Removing restrictions...')

    token = (call.from_user.id, call.message.chat.id)
    await stop_user_track(token)
    logger.info(f'{call.from_user.id} allowed to chat!')


def register(dp: Dispatcher) -> None:
    dp.register_message_handler(handle_new_member, content_types=ContentTypes.NEW_CHAT_MEMBERS)
    dp.register_message_handler(handle_left_member, content_types=ContentTypes.LEFT_CHAT_MEMBER)
    dp.register_callback_query_handler(handle_button)

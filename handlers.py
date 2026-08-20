import asyncio
import random
from db import get_difficulty
from lexicon import LEXICON
from game_logic import show_result, check_winner, get_bot_move
from aiogram import Router
from aiogram import F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramBadRequest
import db
from keyboards import start_keyboard, diff_keyboard, get_field_keyboard

router = Router()


@router.message(Command(commands='start'))
async def send_echo(message: Message):
    user_id = message.from_user.id
    await db.add_user(user_id)
    await db.reset_field(user_id)
    difficulty = await get_difficulty(user_id)
    await message.answer(
        text=LEXICON['start'].format(difficulty=LEXICON['btn_' + difficulty]),
        reply_markup=start_keyboard
    )


@router.message(Command(commands='help'))
async def send_help(message: Message):
    await message.answer(text=LEXICON['help'])
    user_id = message.from_user.id
    difficulty = await get_difficulty(user_id)
    await message.answer(
        text=LEXICON['start'].format(difficulty=LEXICON['btn_' + difficulty]),
        reply_markup=start_keyboard
    )


@router.callback_query(F.data == 'start')
async def start_game(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    await db.add_user(user_id)
    await db.reset_field(user_id)
    await callback.message.edit_text(
        text=LEXICON['game_in_progress(you)'],
        reply_markup=await get_field_keyboard(user_id)
    )

    await db.set_start_move(user_id, random.randint(0, 1))
    if await db.get_move(user_id) == 1:
        await bot_move(callback, user_id)


@router.callback_query(F.data == 'stats')
async def show_stats(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()
    try:
        wins, loses, draws = await db.get_statistics(user_id)
        await callback.message.edit_text(
            text=f"{LEXICON['stats_info'].format(wins=wins, loses=loses, draws=draws)}",
            reply_markup=start_keyboard)
    except TelegramBadRequest:
        ...


@router.callback_query(F.data == 'difficulty')
async def show_difficulty(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON['choosing_difficulty'],
        reply_markup=diff_keyboard
    )


@router.callback_query(F.data.in_(('easy', 'medium', 'hard')))
async def change_difficulty(callback: CallbackQuery):
    await callback.answer()
    difficulty = callback.data
    user_id = callback.from_user.id
    await db.update_difficulty(user_id, difficulty)
    difficulty = await get_difficulty(user_id)
    await callback.message.edit_text(
        text=LEXICON['start'].format(difficulty=LEXICON['btn_' + difficulty]),
        reply_markup=start_keyboard
    )


async def change_statistics(callback: CallbackQuery, res: tuple[bool, int]) -> bool:
    user_id = callback.from_user.id
    if res[0]:
        winner = LEXICON[res[1]]
        board = await show_result(user_id)
        await callback.message.edit_text(
            text=LEXICON['win'].format(winner=winner, board=board),
        )
        difficulty = await get_difficulty(user_id)
        await callback.message.answer(
            text=LEXICON['start'].format(difficulty=LEXICON['btn_' + difficulty]),
            reply_markup=start_keyboard
        )
        user_id = callback.from_user.id
        if res[1] == 1:
            await db.increment_stat(user_id, 'wins')
        else:
            await db.increment_stat(user_id, 'loses')
        return True
    return False


async def check_draw(callback: CallbackQuery):
    user_id = callback.from_user.id
    field = await db.array_field(user_id)
    if 0 not in field:
        board = await show_result(user_id)
        await callback.message.edit_text(
            text=LEXICON['draw'].format(board=board)
        )
        await db.increment_stat(user_id, 'draws')
        difficulty = await get_difficulty(user_id)
        await callback.message.answer(
            text=LEXICON['start'].format(difficulty=LEXICON['btn_' + difficulty]),
            reply_markup=start_keyboard
        )
        return True
    return False


async def bot_move(callback: CallbackQuery, user_id: int) -> None:
    field = await db.array_field(user_id)
    await callback.message.edit_text(
        text=LEXICON['game_in_progress(bot)'],
        reply_markup=await get_field_keyboard(user_id)
    )
    await asyncio.sleep(0.5)

    bot_choice = await get_bot_move(field, user_id)
    field[bot_choice] = 2
    await db.update_field(user_id, db.format_field(field))
    await callback.message.edit_text(
        text=LEXICON['game_in_progress(you)'],
        reply_markup=await get_field_keyboard(user_id)
    )

    res = await check_winner(user_id)
    if await change_statistics(callback, res):
        return

    if await check_draw(callback):
        return

    await db.update_move(user_id)


@router.callback_query(F.data.in_({'0', '1', '2', '3', '4', '5', '6', '7', '8'}))
async def handle_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    field = await db.array_field(user_id)

    if await db.get_move(user_id):
        await callback.answer(
            text=LEXICON['wait_bot'],
            show_alert=True
        )
        return

    ind = callback.data
    if field[int(ind)] != 0:
        await callback.answer(text=LEXICON['busy'])
        return

    await db.update_move(user_id)
    field[int(ind)] = 1
    await db.update_field(user_id, db.format_field(field))

    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON['game_in_progress(you)'],
        reply_markup=await get_field_keyboard(user_id)
    )

    res = await check_winner(user_id)

    if await change_statistics(callback, res):
        return

    if await check_draw(callback):
        return

    await bot_move(callback, user_id)


@router.message()
async def ignore_msg(message: Message):
    await message.delete()

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db import get_field
from lexicon import LEXICON


start_btn = InlineKeyboardButton(text=LEXICON['btn_play'], callback_data='start')
stats_btn = InlineKeyboardButton(text=LEXICON['btn_stats'], callback_data='stats')
difficulty_btn = InlineKeyboardButton(text=LEXICON['btn_difficulty'], callback_data='difficulty')
start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [start_btn],
        [difficulty_btn],
        [stats_btn]
    ]
)

diff_btn_1 = InlineKeyboardButton(text=LEXICON['btn_easy'], callback_data='easy')
diff_btn_2 = InlineKeyboardButton(text=LEXICON['btn_medium'], callback_data='medium')
diff_btn_3 = InlineKeyboardButton(text=LEXICON['btn_hard'], callback_data='hard')
diff_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [diff_btn_1, diff_btn_2, diff_btn_3]]
)


async def get_field_keyboard(user_id: int) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons = []
    field = [int(i) for i in await get_field(user_id)]
    for i in range(len(field)):
        buttons.append(InlineKeyboardButton(text=LEXICON[field[i]], callback_data=str(i)))
    kb_builder.row(*buttons, width=3)
    return kb_builder.as_markup()

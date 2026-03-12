from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def invite_friend_button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎁 Запросити друзів")]
        ],
        resize_keyboard=True
    )

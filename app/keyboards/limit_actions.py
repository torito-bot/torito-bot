from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def invite_friend_inline():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Запросити друзів", callback_data="open_referral")]
        ]
    )

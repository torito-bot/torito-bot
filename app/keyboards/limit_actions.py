from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def limit_actions_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Запросити друзів", callback_data="open_referral")],
            [InlineKeyboardButton(text="💎 Придбати PRO", callback_data="buy_pro")]
        ]
    )

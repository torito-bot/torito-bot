from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def niche_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🐶 Pet products", callback_data="niche:pet products")],
            [InlineKeyboardButton(text="🚗 Car accessories", callback_data="niche:car accessories")],
            [InlineKeyboardButton(text="🍳 Kitchen gadgets", callback_data="niche:kitchen gadgets")],
            [InlineKeyboardButton(text="💪 Fitness", callback_data="niche:fitness")],
            [InlineKeyboardButton(text="🏠 Home decor", callback_data="niche:home decor")],
        ]
    )

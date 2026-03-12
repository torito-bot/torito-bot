from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def niche_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[

            [InlineKeyboardButton(text="📱 Гаджети та електроніка", callback_data="niche:gadgets")],

            [InlineKeyboardButton(text="🐶 Товари для тварин", callback_data="niche:pet products")],

            [InlineKeyboardButton(text="🏠 Товари для дому", callback_data="niche:home")],

            [InlineKeyboardButton(text="🚗 Автоаксесуари", callback_data="niche:car accessories")],

            [InlineKeyboardButton(text="💪 Фітнес та здоров’я", callback_data="niche:fitness")],

            [InlineKeyboardButton(text="💄 Краса та догляд", callback_data="niche:beauty")],

            [InlineKeyboardButton(text="🧰 Інструменти та DIY", callback_data="niche:diy")],

            [InlineKeyboardButton(text="👶 Товари для дітей", callback_data="niche:baby")],

            [InlineKeyboardButton(text="🎮 Хобі та розваги", callback_data="niche:hobby")],

            [InlineKeyboardButton(text="🌿 Eco товари", callback_data="niche:eco")],

        ]
    )

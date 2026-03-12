from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def ads_geo_selector():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇺🇦 Україна", callback_data="ads_geo:ua")],
            [InlineKeyboardButton(text="🇪🇺 Європа", callback_data="ads_geo:eu")],
            [InlineKeyboardButton(text="🇺🇸 США", callback_data="ads_geo:us")],
        ]
    )

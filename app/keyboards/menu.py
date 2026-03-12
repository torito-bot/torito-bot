from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    keyboard = [
        [KeyboardButton(text="🔥 ТОП товарів")],
        [KeyboardButton(text="⚡ Трендові товари")],
        [KeyboardButton(text="📡 Ads сканер")],
        [KeyboardButton(text="📊 Категорії")],
        [KeyboardButton(text="🎓 Запуск товарного бізнесу")],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

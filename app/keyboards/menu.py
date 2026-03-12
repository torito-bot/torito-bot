from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():
    keyboard = [
        [KeyboardButton(text="🔥 ТОП товарів")],
        [KeyboardButton(text="⚡ Трендові товари")],
        [KeyboardButton(text="📡 Ads сканер")],
        [KeyboardButton(text="🔥 Реклама 7+ днів")],
        [KeyboardButton(text="🏆 Top Score")],
        [KeyboardButton(text="🔎 Пошук по ніші")],
        [KeyboardButton(text="🎁 Запросити друзів")],
        [KeyboardButton(text="📊 Категорії")],
        [KeyboardButton(text="🎓 Запуск товарного бізнесу")],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

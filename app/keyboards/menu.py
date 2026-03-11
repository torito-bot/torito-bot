from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔥 ТОП товарів")],
            [KeyboardButton(text="⚡ Трендові товари")],
            [KeyboardButton(text="📊 Категорії")],
            [KeyboardButton(text="🎓 Запуск товарного бізнесу")]
        ],
        resize_keyboard=True
    )

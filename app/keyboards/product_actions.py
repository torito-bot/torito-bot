from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_product_actions(product_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📦 Безкоштовні постачальники",
                    callback_data=f"free_suppliers:{product_name}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇺🇦 Українські постачальники",
                    callback_data=f"ua_suppliers:{product_name}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎓 Курс запуску",
                    callback_data=f"course:{product_name}"
                )
            ],
        ]
    )

from aiogram import Router
from aiogram.types import Message

from app.database.db import log_event
from app.services.trend_service import get_trending_products
from app.keyboards.product_actions import get_product_actions

router = Router()


@router.message(lambda message: message.text == "⚡ Трендові товари")
async def trending_products(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    log_event(user_id, "open_section", "trending_products")

    products = get_trending_products()

    for p in products:
        text = (
            f"⚡ {p['name']}\n\n"
            f"📢 Рекламодавців: {p['ads']}\n"
            f"📅 Активна реклама: {p['days']} днів\n"
            f"💰 Середня ціна: ${p['price']}\n"
            f"📦 Закупка: ${p['cost']}\n"
            f"📈 Маржа: ~{p['margin']}%\n"
            f"⚔️ Конкуренція: {p['competition']}\n"
            f"🚀 Потенціал: {p['potential']}\n"
            f"🧠 Висновок: {p['recommendation']}\n"
        )

        await message.answer(text, reply_markup=get_product_actions(p["name"]))

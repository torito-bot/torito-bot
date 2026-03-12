from aiogram import Router
from aiogram.types import Message

from app.database.db import log_event
from app.keyboards.product_actions import get_product_actions
from app.services.top_score_service import get_top_score_products

router = Router()


@router.message(lambda message: message.text == "🏆 Top Score")
async def top_score(message: Message):
    user_id = message.from_user.id if message.from_user else 0
    log_event(user_id, "open_section", "top_score")

    products = get_top_score_products()

    if not products:
        await message.answer("Поки що немає товарів для Top Score.")
        return

    await message.answer("🏆 Найкращі товари за Torito Score")

    for index, p in enumerate(products, start=1):
        text = (
            f"🏆 #{index} {p['name']}\n\n"
            f"📍 Джерело: {p['source']}\n"
            f"📢 Рекламодавців: {p['ads']}\n"
            f"📅 Активна реклама: {p['days']} днів\n"
            f"💰 Середня ціна: ${p['price']}\n"
            f"📦 Закупка: ${p['cost']}\n"
            f"📈 Маржа: ~{p['margin']}%\n"
            f"⚔️ Конкуренція: {p['competition']}\n"
            f"🚀 Потенціал: {p['potential']}\n"
            f"🧠 Висновок: {p['recommendation']}\n"
            f"🎯 Torito Score: {p['score']}/100 {p['score_label']}\n"
        )

        await message.answer(text, reply_markup=get_product_actions(p["name"]))

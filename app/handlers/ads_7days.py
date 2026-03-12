from aiogram import Router
from aiogram.types import Message

from app.database.db import log_event
from app.keyboards.product_actions import get_product_actions
from app.keyboards.limit_actions import limit_actions_keyboard
from app.services.ads_7days_service import get_ads_7days_products
from app.services.limit_service import check_limit

router = Router()


@router.message(lambda message: message.text == "🔥 Реклама 7+ днів")
async def ads_7days(message: Message):
    user_id = message.from_user.id if message.from_user else 0

    ok, used, limit = check_limit(user_id)

    if not ok:
        await message.answer(
            f"⛔ Ліміт аналізів на сьогодні вичерпано\n\n"
            f"Використано: {used}/{limit}\n\n"
            f"🎁 Запроси друзів, щоб збільшити ліміт",
            reply_markup=limit_actions_keyboard()
        )
        return

    remaining = limit - used

    await message.answer(
        f"🔥 Реклама 7+ днів\n\n"
        f"Використано: {used}/{limit}\n"
        f"Залишилось: {remaining}"
    )

    log_event(user_id, "open_section", "ads_7days")

    products = get_ads_7days_products()

    if not products:
        await message.answer("Поки що немає товарів з рекламою 7+ днів.")
        return

    for p in products:
        text = (
            f"🔥 {p['name']}\n\n"
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

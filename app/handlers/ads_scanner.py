from aiogram import Router
from aiogram.types import Message

from app.database.db import log_event
from app.services.ads_scanner_service import get_meta_ads_products
from app.services.limit_service import check_limit
from app.keyboards.product_actions import get_product_actions

router = Router()


@router.message(lambda message: message.text == "📡 Ads сканер")
async def ads_scanner(message: Message):

    user_id = message.from_user.id

    ok, used, limit = check_limit(user_id)

    if not ok:
        await message.answer(
            f"⛔ Ліміт аналізів на сьогодні вичерпано\n\n"
            f"Використано: {used}/{limit}\n\n"
            f"🎁 Запроси друзів щоб збільшити ліміт\n"
            f"/ref"
        )
        return

    remaining = limit - used

    await message.answer(
        f"📡 Ads Scanner\n\n"
        f"Використано: {used}/{limit}\n"
        f"Залишилось: {remaining}\n"
    )

    log_event(user_id, "open_section", "ads_scanner")

    products = get_meta_ads_products()

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
            f"🎯 Torito Score: {p['score']}/100 {p['score_label']}"
        )

        await message.answer(
            text,
            reply_markup=get_product_actions(p["name"])
        )

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.database.db import log_event
from app.keyboards.niche_menu import niche_menu
from app.keyboards.product_actions import get_product_actions
from app.services.niche_scanner_service import search_products_by_niche
from app.services.limit_service import check_limit

router = Router()


@router.message(lambda message: message.text == "🔎 Пошук по ніші")
async def niche_help(message: Message):
    text = (
        "🔎 Пошук по ніші\n\n"
        "Обери готову нішу нижче 👇"
    )
    await message.answer(text, reply_markup=niche_menu())


@router.callback_query(F.data.startswith("niche:"))
async def pick_niche(callback: CallbackQuery):
    user_id = callback.from_user.id if callback.from_user else 0
    query = callback.data.split(":", 1)[1].strip()

    ok, used, limit = check_limit(user_id)

    if not ok:
        await callback.message.answer(
            f"⛔ Ліміт аналізів на сьогодні вичерпано\n\n"
            f"Використано: {used}/{limit}\n\n"
            f"🎁 Запроси друзів, щоб збільшити ліміт\n"
            f"/ref"
        )
        await callback.answer()
        return

    remaining = limit - used

    await callback.message.answer(
        f"🔎 Пошук по ніші\n\n"
        f"Використано: {used}/{limit}\n"
        f"Залишилось: {remaining}"
    )

    log_event(user_id, "open_section", f"niche_pick:{query}")

    products = search_products_by_niche(query)

    if not products:
        await callback.message.answer(
            f"По ніші '{query}' поки нічого не знайдено."
        )
        await callback.answer()
        return

    await callback.message.answer(f"🔎 Знайдено товари по ніші: {query}")

    for p in products:
        text = (
            f"🔎 {p['name']}\n\n"
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

        await callback.message.answer(text, reply_markup=get_product_actions(p["name"]))

    await callback.answer()

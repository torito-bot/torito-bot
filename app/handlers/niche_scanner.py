from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database.db import log_event
from app.keyboards.product_actions import get_product_actions
from app.services.niche_scanner_service import search_products_by_niche

router = Router()


@router.message(lambda message: message.text == "🔎 Пошук по ніші")
async def niche_help(message: Message):
    text = (
        "🔎 Пошук по ніші\n\n"
        "Напиши команду так:\n"
        "/pick pet products\n\n"
        "Приклади:\n"
        "/pick car accessories\n"
        "/pick kitchen gadgets\n"
        "/pick fitness\n"
        "/pick home decor"
    )
    await message.answer(text)


@router.message(Command("pick"))
async def pick_products(message: Message):
    user_id = message.from_user.id if message.from_user else 0

    full_text = (message.text or "").strip()
    parts = full_text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "Напиши запит так:\n"
            "/pick pet products"
        )
        return

    query = parts[1].strip()
    log_event(user_id, "open_section", f"niche_pick:{query}")

    products = search_products_by_niche(query)

    if not products:
        await message.answer(
            f"По ніші '{query}' поки нічого не знайдено.\n\n"
            "Спробуй інший запит:\n"
            "/pick car accessories\n"
            "/pick kitchen gadgets\n"
            "/pick fitness"
        )
        return

    await message.answer(f"🔎 Знайдено товари по ніші: {query}")

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

        await message.answer(text, reply_markup=get_product_actions(p["name"]))

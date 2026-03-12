from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.database.db import log_event
from app.keyboards.geo_selector import ads_geo_selector
from app.keyboards.product_actions import get_product_actions
from app.keyboards.limit_actions import limit_actions_keyboard
from app.services.ads_scanner_service import get_meta_ads_products_by_geo
from app.services.limit_service import check_limit

router = Router()


def geo_label(code: str) -> str:
    mapping = {
        "ua": "🇺🇦 Україна",
        "eu": "🇪🇺 Європа",
        "us": "🇺🇸 США",
    }
    return mapping.get(code.lower(), code.upper())


@router.message(lambda message: message.text == "📡 Ads сканер")
async def ads_scanner_entry(message: Message):
    await message.answer(
        "📡 Ads Scanner\n\nОбери географію для аналізу реклами 👇",
        reply_markup=ads_geo_selector()
    )


@router.callback_query(F.data.startswith("ads_geo:"))
async def ads_scanner_run(callback: CallbackQuery):
    user_id = callback.from_user.id if callback.from_user else 0
    geo_code = callback.data.split(":", 1)[1].strip().lower()

    ok, used, limit = check_limit(user_id)

    if not ok:
        await callback.message.answer(
            f"⛔ Ліміт аналізів на сьогодні вичерпано\n\n"
            f"Використано: {used}/{limit}\n\n"
            f"🎁 Запроси друзів, щоб збільшити ліміт",
            reply_markup=limit_actions_keyboard()
        )
        await callback.answer()
        return

    remaining = limit - used
    geo_name = geo_label(geo_code)

    await callback.message.answer(
        f"📡 Ads Scanner\n\n"
        f"Гео: {geo_name}\n"
        f"Використано: {used}/{limit}\n"
        f"Залишилось: {remaining}\n\n"
        f"🔎 Формую TOP 10 товарів..."
    )

    log_event(user_id, "open_section", f"ads_scanner:{geo_code}")

    products = get_meta_ads_products_by_geo(geo_code)

    if not products:
        await callback.message.answer(f"Поки що немає даних для {geo_name}.")
        await callback.answer()
        return

    await callback.message.answer(f"🏆 TOP 10 товарів для {geo_name}")

    for index, p in enumerate(products, start=1):
        text = (
            f"🏆 #{index} {p['name']}\n\n"
            f"🌍 Гео: {p['geo']}\n"
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

        await callback.message.answer(
            text,
            reply_markup=get_product_actions(p["name"])
        )

    await callback.answer()

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import ADMIN_ID
from app.services.meta_ads_ingest_runner import ingest_seed_products_for_geo
from app.services.meta_ads_ingest_service import run_meta_ads_ingest

router = Router()


def is_admin(message: Message) -> bool:
    user_id = str(message.from_user.id) if message.from_user else ""
    return bool(ADMIN_ID) and user_id == str(ADMIN_ID)


@router.message(Command("meta_seed"))
async def meta_seed(message: Message):
    if not is_admin(message):
        await message.answer("⛔ Немає доступу")
        return

    parts = (message.text or "").strip().lower().split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Використай:\n/meta_seed ua\n/meta_seed eu\n/meta_seed us")
        return

    geo = parts[1].strip()

    if geo not in {"ua", "eu", "us"}:
        await message.answer("Доступні гео: ua, eu, us")
        return

    total = ingest_seed_products_for_geo(geo)
    await message.answer(
        f"✅ Seed ingest завершено для {geo.upper()}\n"
        f"Додано/оновлено товарів: {total}"
    )


@router.message(Command("meta_live"))
async def meta_live(message: Message):
    if not is_admin(message):
        await message.answer("⛔ Немає доступу")
        return

    parts = (message.text or "").strip().lower().split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Використай:\n/meta_live eu")
        return

    geo = parts[1].strip()

    if geo != "eu":
        await message.answer("Live v1 зараз доступний тільки для: eu")
        return

    await message.answer(f"🔎 Запускаю live Meta ingest для {geo.upper()}...")

    try:
        result = run_meta_ads_ingest(geo)
        await message.answer(
            f"✅ Live ingest завершено для {geo.upper()}\n"
            f"Raw ads: {result['raw_ads_count']}\n"
            f"Products: {result['products_count']}"
        )
    except Exception as e:
        await message.answer(f"❌ Помилка live ingest: {e}")


@router.message(lambda message: (message.text or "").lower().startswith("/meta_live "))
async def meta_live_fallback(message: Message):
    await meta_live(message)


@router.message(lambda message: (message.text or "").lower().startswith("/meta_seed "))
async def meta_seed_fallback(message: Message):
    await meta_seed(message)

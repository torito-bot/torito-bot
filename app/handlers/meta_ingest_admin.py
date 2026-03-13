from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import ADMIN_ID
from app.services.meta_ads_ingest_runner import ingest_seed_products_for_geo

router = Router()


@router.message(Command("meta_seed"))
async def meta_seed(message: Message):
    user_id = str(message.from_user.id) if message.from_user else ""

    if not ADMIN_ID or user_id != str(ADMIN_ID):
        await message.answer("⛔ Немає доступу")
        return

    text_raw = (message.text or "").strip().lower()
    parts = text_raw.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Використай:\n/meta_seed ua\n/meta_seed eu\n/meta_seed us")
        return

    geo = parts[1].strip()

    if geo not in {"ua", "eu", "us"}:
        await message.answer("Доступні гео: ua, eu, us")
        return

    total = ingest_seed_products_for_geo(geo)
    await message.answer(f"✅ Seed ingest завершено для {geo.upper()}\nДодано/оновлено товарів: {total}")

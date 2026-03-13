from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import requests

from app.config import ADMIN_ID
from app.config_meta import META_ACCESS_TOKEN, META_API_VERSION

router = Router()


def is_admin(message: Message) -> bool:
    user_id = str(message.from_user.id) if message.from_user else ""
    return bool(ADMIN_ID) and user_id == str(ADMIN_ID)


@router.message(Command("meta_debug"))
async def meta_debug(message: Message):
    if not is_admin(message):
        await message.answer("⛔ Немає доступу")
        return

    if not META_ACCESS_TOKEN:
        await message.answer("❌ META_ACCESS_TOKEN не заданий")
        return

    url = f"https://graph.facebook.com/{META_API_VERSION}/ads_archive"
    params = {
        "access_token": META_ACCESS_TOKEN,
        "ad_type": "ALL",
        "ad_active_status": "ACTIVE",
        "search_terms": "phone holder",
        "ad_reached_countries": "['DE']",
        "fields": ",".join([
            "id",
            "page_id",
            "page_name",
            "ad_snapshot_url",
            "ad_delivery_start_time",
            "publisher_platforms",
            "ad_creative_bodies",
            "ad_creative_link_titles",
        ]),
        "limit": 3,
    }

    try:
        r = requests.get(url, params=params, timeout=30)
        text = r.text[:3500]
        await message.answer(f"HTTP {r.status_code}\n\n{text}")
    except Exception as e:
        await message.answer(f"❌ Debug error: {e}")

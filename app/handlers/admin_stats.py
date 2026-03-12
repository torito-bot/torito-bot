from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import ADMIN_ID
from app.database.db import (
    get_total_users,
    get_total_referrals,
    count_events,
    get_top_clicked_products,
    get_top_referrers,
)

router = Router()


@router.message(Command("stats"))
async def show_stats(message: Message):
    user_id = str(message.from_user.id) if message.from_user else ""

    if not ADMIN_ID or user_id != str(ADMIN_ID):
        await message.answer("⛔ Немає доступу")
        return

    total_users = get_total_users()
    total_referrals = get_total_referrals()
    total_starts = count_events("start")
    top_opens = count_events("open_section", "top_products")
    trending_opens = count_events("open_section", "trending_products")
    ads_scanner_opens = count_events("open_section", "ads_scanner")
    ads_7days_opens = count_events("open_section", "ads_7days")
    top_score_opens = count_events("open_section", "top_score")
    referral_opens = count_events("open_section", "referrals")
    niche_opens = count_events("open_section")
    total_clicks = count_events("click_action")

    top_clicked = get_top_clicked_products()
    top_referrers = get_top_referrers()

    clicked_text = ""
    if top_clicked:
        for event_value, total in top_clicked:
            clicked_text += f"• {event_value} — {total}\n"
    else:
        clicked_text = "• ще немає даних\n"

    ref_text = ""
    if top_referrers:
        for referrer, total in top_referrers:
            ref_text += f"• {referrer} — {total}\n"
    else:
        ref_text = "• ще немає даних\n"

    text = (
        "📊 Статистика Torito\n\n"
        f"👥 Користувачів: {total_users}\n"
        f"🎁 Усього рефералів: {total_referrals}\n"
        f"🚀 Стартів: {total_starts}\n"
        f"🔥 Відкриття ТОП товарів: {top_opens}\n"
        f"⚡ Відкриття трендових: {trending_opens}\n"
        f"📡 Відкриття Ads scanner: {ads_scanner_opens}\n"
        f"🔥 Відкриття 7+ днів: {ads_7days_opens}\n"
        f"🏆 Відкриття Top Score: {top_score_opens}\n"
        f"🔎 Усього відкриттів пошуку по нішах: {niche_opens}\n"
        f"🎁 Відкриття рефералки: {referral_opens}\n"
        f"🖱 Усього кліків по кнопках: {total_clicks}\n\n"
        "🏆 Найпопулярніші кліки:\n"
        f"{clicked_text}\n"
        "🎁 Топ реферери:\n"
        f"{ref_text}"
    )

    await message.answer(text)

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import ADMIN_ID
from app.database.db import get_total_users, count_events, get_top_clicked_products

router = Router()


@router.message(Command("stats"))
async def show_stats(message: Message):
    user_id = str(message.from_user.id) if message.from_user else ""

    if not ADMIN_ID or user_id != str(ADMIN_ID):
        await message.answer("⛔ Немає доступу")
        return

    total_users = get_total_users()
    total_starts = count_events("start")
    top_opens = count_events("open_section", "top_products")
    trending_opens = count_events("open_section", "trending_products")
    total_clicks = count_events("click_action")

    top_clicked = get_top_clicked_products()

    clicked_text = ""
    if top_clicked:
        for event_value, total in top_clicked:
            clicked_text += f"• {event_value} — {total}\n"
    else:
        clicked_text = "• ще немає даних\n"

    text = (
        "📊 Статистика Torito\n\n"
        f"👥 Користувачів: {total_users}\n"
        f"🚀 Стартів: {total_starts}\n"
        f"🔥 Відкриття ТОП товарів: {top_opens}\n"
        f"⚡ Відкриття трендових: {trending_opens}\n"
        f"🖱 Усього кліків по кнопках: {total_clicks}\n\n"
        "🏆 Найпопулярніші кліки:\n"
        f"{clicked_text}"
    )

    await message.answer(text)

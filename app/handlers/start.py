from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.database.db import add_user, log_event, set_referral
from app.keyboards.menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    user = message.from_user
    user_id = user.id if user else 0
    username = user.username if user else None
    full_name = user.full_name if user else "Unknown"

    add_user(user_id, username, full_name)
    log_event(user_id, "start", "start_command")

    referral_notice = ""

    text_raw = (message.text or "").strip()
    if text_raw.startswith("/start ref_"):
        referral_code = text_raw.replace("/start ref_", "", 1).strip()
        result = set_referral(user_id, referral_code)

        if result["status"] == "ok":
            log_event(user_id, "referral_join", referral_code)
            referral_notice = "\n🎁 Реферальний бонус активовано."
        elif result["status"] == "self":
            referral_notice = "\n⚠️ Не можна активувати власне реферальне посилання."
        elif result["status"] == "already_set":
            referral_notice = "\nℹ️ Для цього акаунта реферал уже зафіксований."

    text = (
        "🚀 Torito Bot\n\n"
        "Бот для пошуку товарів, які активно рекламуються.\n\n"
        "Тут ти зможеш:\n"
        "• знаходити трендові товари\n"
        "• дивитись аналіз реклами\n"
        "• отримувати постачальників\n"
        "• запускати товарний бізнес\n"
        f"{referral_notice}\n\n"
        "Обери дію нижче 👇"
    )

    await message.answer(text, reply_markup=main_menu())

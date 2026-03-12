from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.database.db import get_user_referral_info, log_event

router = Router()


async def send_referral_info(message: Message):
    user = message.from_user
    user_id = user.id if user else 0

    info = get_user_referral_info(user_id)
    log_event(user_id, "open_section", "referrals")

    me = await message.bot.get_me()
    bot_username = me.username or ""
    referral_link = f"https://t.me/{bot_username}?start=ref_{info['referral_code']}"

    text = (
        "🎁 Реферальна програма Torito\n\n"
        f"👥 Запрошено друзів: {info['referrals_count']}\n\n"
        "Твоє реферальне посилання:\n"
        f"{referral_link}\n\n"
        "Як це працює:\n"
        "• друг переходить за твоїм посиланням\n"
        "• бот фіксує запрошення\n"
        "• далі на це підключимо бонуси Free / Pro\n\n"
        "Пізніше сюди додамо:\n"
        "• бонусні аналізи\n"
        "• unlock premium функцій\n"
        "• рейтинг топ реферерів"
    )

    await message.answer(text)


@router.message(Command("ref"))
async def referral_command(message: Message):
    await send_referral_info(message)


@router.message(lambda message: message.text == "🎁 Запросити друзів")
async def referral_button(message: Message):
    await send_referral_info(message)

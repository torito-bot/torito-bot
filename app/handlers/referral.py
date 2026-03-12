from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.database.db import get_user_referral_info, get_user_limits, log_event

router = Router()


async def build_referral_text(message_or_callback):
    user = message_or_callback.from_user
    user_id = user.id if user else 0

    info = get_user_referral_info(user_id)
    limits = get_user_limits(user_id)
    log_event(user_id, "open_section", "referrals")

    bot = message_or_callback.bot
    me = await bot.get_me()
    bot_username = me.username or ""
    referral_link = f"https://t.me/{bot_username}?start=ref_{info['referral_code']}"

    return (
        "🎁 Реферальна програма Torito\n\n"
        f"👥 Запрошено друзів: {info['referrals_count']}\n"
        f"🆓 Базовий free-ліміт: {limits['base_limit']} аналізів\n"
        f"➕ Бонус за 1 друга: +{limits['bonus_per_friend']} аналізи\n"
        f"📈 Твій поточний ліміт: {limits['total_limit']} аналізів\n\n"
        "Твоє реферальне посилання:\n"
        f"{referral_link}\n\n"
        "Як це працює:\n"
        "• друг переходить за твоїм посиланням\n"
        "• бот фіксує запрошення\n"
        "• ти отримуєш бонус до free-ліміту"
    )


@router.message(Command("ref"))
async def referral_command(message: Message):
    text = await build_referral_text(message)
    await message.answer(text)


@router.message(lambda message: message.text == "🎁 Запросити друзів")
async def referral_button(message: Message):
    text = await build_referral_text(message)
    await message.answer(text)


@router.callback_query(F.data == "open_referral")
async def referral_inline(callback: CallbackQuery):
    text = await build_referral_text(callback)
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "buy_pro")
async def buy_pro(callback: CallbackQuery):
    text = (
        "💎 PRO доступ Torito\n\n"
        "Що дає PRO:\n"
        "• необмежений Ads Scanner\n"
        "• повний доступ до аналітики\n"
        "• ранні трендові товари\n"
        "• пріоритетні оновлення\n\n"
        "💰 Вартість: 9$ / місяць\n\n"
        "Напиши адміну для підключення:\n"
        "@your_username"
    )

    await callback.message.answer(text)
    await callback.answer()

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.database.db import log_event

router = Router()


@router.callback_query(F.data.startswith("free_suppliers:"))
async def free_suppliers(callback: CallbackQuery):
    product_name = callback.data.split(":", 1)[1]
    telegram_id = callback.from_user.id

    log_event(telegram_id, "click_action", f"free_suppliers:{product_name}")

    text = (
        f"📦 Безкоштовні постачальники для {product_name}\n\n"
        "Alibaba:\n"
        f"https://www.alibaba.com/trade/search?SearchText={product_name}\n\n"
        "1688:\n"
        f"https://s.1688.com/selloffer/offer_search.htm?keywords={product_name}\n\n"
        "Alibaba — простіше для старту\n"
        "1688 — часто дешевше, але складніше в роботі"
    )

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data.startswith("ua_suppliers:"))
async def ua_suppliers(callback: CallbackQuery):
    product_name = callback.data.split(":", 1)[1]
    telegram_id = callback.from_user.id

    log_event(telegram_id, "click_action", f"ua_suppliers:{product_name}")

    text = (
        f"🇺🇦 Українські постачальники для {product_name}\n\n"
        "У цьому блоці будуть:\n"
        "• постачальники по Україні\n"
        "• швидкий тест товару\n"
        "• запуск без довгої доставки\n\n"
        "Цей блок буде доступний у преміум-доступі."
    )

    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data.startswith("course:"))
async def course(callback: CallbackQuery):
    product_name = callback.data.split(":", 1)[1]
    telegram_id = callback.from_user.id

    log_event(telegram_id, "click_action", f"course:{product_name}")

    text = (
        f"🎓 Курс запуску для {product_name}\n\n"
        "Що буде у курсі:\n"
        "• як знаходити товар\n"
        "• як аналізувати рекламу\n"
        "• як запускати рекламу\n"
        "• як знаходити постачальників\n\n"
        "Курс скоро з’явиться у Torito."
    )

    await callback.message.answer(text)
    await callback.answer()

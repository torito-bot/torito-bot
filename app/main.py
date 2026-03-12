import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import BOT_TOKEN
from app.database.db import init_db, seed_products
from app.handlers.start import router as start_router
from app.handlers.top import router as top_router
from app.handlers.trending import router as trending_router
from app.handlers.ads_scanner import router as ads_scanner_router
from app.handlers.ads_7days import router as ads_7days_router
from app.handlers.niche_scanner import router as niche_scanner_router
from app.handlers.product_actions import router as product_actions_router
from app.handlers.admin_stats import router as admin_stats_router
from app.handlers.menu_restore import router as menu_restore_router


async def main():
    logging.basicConfig(level=logging.INFO)

    init_db()
    seed_products()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(top_router)
    dp.include_router(trending_router)
    dp.include_router(ads_scanner_router)
    dp.include_router(ads_7days_router)
    dp.include_router(niche_scanner_router)
    dp.include_router(product_actions_router)
    dp.include_router(admin_stats_router)
    dp.include_router(menu_restore_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

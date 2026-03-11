from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.menu import main_menu

router = Router()


@router.message(Command("menu"))
async def show_menu(message: Message):
    await message.answer("📍 Головне меню Torito", reply_markup=main_menu())

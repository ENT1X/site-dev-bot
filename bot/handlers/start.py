from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.database import create_user
from bot.keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await create_user(user.id, user.full_name, user.username)
    await message.answer(
        f"👋 Привет, {user.full_name}!\n\n"
        "Все функции в Mini App 👇\n"
        "Профиль, заказы, портфолио и заявки.",
        reply_markup=main_menu(),
    )

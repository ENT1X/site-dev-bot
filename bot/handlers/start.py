from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile

from bot.database import create_user, get_user, update_user_phone
from bot.keyboards import main_menu, mini_app_button, contact_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await create_user(user.id, user.full_name, user.username)
    await message.answer(
        f"👋 Привет, {user.full_name}!\n\n"
        "Я — бот для разработки сайтов. Вот что я умею:\n\n"
        "👤 Профиль — просмотр и редактирование\n"
        "📂 Портфолио — примеры наших работ\n"
        "📝 Заказать сайт — оформить заявку\n"
        "💬 Связь с нами — обратная связь\n"
        "🌐 Mini App — полноценный интерфейс в Telegram",
        reply_markup=main_menu(),
    )


@router.message(F.text == "👤 Профиль")
@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Вы не зарегистрированы. Напишите /start")
        return
    text = (
        f"👤 Ваш профиль:\n\n"
        f"Имя: {user['full_name']}\n"
        f"Username: @{user['username'] if user['username'] else 'не указан'}\n"
        f"Телефон: {user['phone'] if user['phone'] else 'не указан'}\n"
        f"Дата регистрации: {user['created_at']}"
    )
    await message.answer(text, reply_markup=main_menu())


@router.message(F.contact)
async def handle_contact(message: Message):
    phone = message.contact.phone_number
    await update_user_phone(message.from_user.id, phone)
    await message.answer(
        f"✅ Номер {phone} сохранён!",
        reply_markup=main_menu(),
    )




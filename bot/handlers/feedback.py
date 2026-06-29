from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboards import main_menu

router = Router()


class FeedbackForm(StatesGroup):
    message_text = State()


@router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext):
    await message.answer(
        "Напишите ваш вопрос или предложение. "
        "Мы ответим в ближайшее время!",
    )
    await state.set_state(FeedbackForm.message_text)


@router.message(FeedbackForm.message_text)
async def process_feedback(message: Message, state: FSMContext):
    text = (
        f"💬 Новое сообщение от @{message.from_user.username or message.from_user.full_name} "
        f"(ID: {message.from_user.id}):\n\n{message.text}"
    )
    from bot.config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(chat_id=admin_id, text=text)
        except Exception:
            pass
    await message.answer(
        "✅ Спасибо! Ваше сообщение отправлено. Мы ответим вам в ближайшее время.",
        reply_markup=main_menu(),
    )
    await state.clear()

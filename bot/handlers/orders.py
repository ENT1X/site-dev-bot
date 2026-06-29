from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.database import get_user, create_order, get_user_orders
from bot.keyboards import main_menu

router = Router()


class OrderForm(StatesGroup):
    order_type = State()
    description = State()
    budget = State()


ORDER_TYPES = {
    "1": "Лендинг",
    "2": "Корпоративный сайт",
    "3": "Интернет-магазин",
    "4": "Веб-приложение",
    "5": "Другое",
}


@router.message(F.text == "📝 Заказать сайт")
@router.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Сначала зарегистрируйтесь — /start")
        return
    text = "Выберите тип сайта:\n\n"
    for key, val in ORDER_TYPES.items():
        text += f"{key}. {val}\n"
    text += "\nОтправьте номер (1-5)"
    await message.answer(text)
    await state.set_state(OrderForm.order_type)


@router.message(OrderForm.order_type)
async def process_order_type(message: Message, state: FSMContext):
    if message.text not in ORDER_TYPES:
        await message.answer("Пожалуйста, выберите номер от 1 до 5")
        return
    await state.update_data(order_type=ORDER_TYPES[message.text])
    await message.answer("Опишите ваш проект подробнее (что должно быть на сайте, примеры):")
    await state.set_state(OrderForm.description)


@router.message(OrderForm.description)
async def process_description(message: Message, state: FSMContext):
    if len(message.text) < 10:
        await message.answer("Опишите подробнее (минимум 10 символов)")
        return
    await state.update_data(description=message.text)
    await message.answer("Какой бюджет (в рублях)? Можно указать примерно или пропустить (/skip):")
    await state.set_state(OrderForm.budget)


@router.message(OrderForm.budget, Command("skip"))
async def skip_budget(message: Message, state: FSMContext):
    data = await state.update_data(budget=None)
    await finish_order(message, state, data)


@router.message(OrderForm.budget)
async def process_budget(message: Message, state: FSMContext):
    data = await state.update_data(budget=message.text)
    await finish_order(message, state, data)


async def finish_order(message: Message, state: FSMContext, data: dict):
    user = await get_user(message.from_user.id)
    order_id = await create_order(user["id"], data["order_type"], data["description"], data.get("budget"))
    text = (
        f"✅ Заказ №{order_id} создан!\n\n"
        f"Тип: {data['order_type']}\n"
        f"Описание: {data['description']}\n"
        f"Бюджет: {data.get('budget') or 'не указан'}\n\n"
        "Мы свяжемся с вами в ближайшее время."
    )
    await message.answer(text, reply_markup=main_menu())
    await state.clear()


@router.message(F.text == "📋 Мои заказы")
@router.message(Command("orders"))
async def cmd_orders(message: Message):
    orders = await get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("У вас пока нет заказов.", reply_markup=main_menu())
        return
    text = "📋 Ваши заказы:\n\n"
    for order in orders:
        text += (
            f"№{order['id']} — {order['order_type']}\n"
            f"Статус: {order['status']}\n"
            f"Дата: {order['created_at']}\n\n"
        )
    await message.answer(text, reply_markup=main_menu())

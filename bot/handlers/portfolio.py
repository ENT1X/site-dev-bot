from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from bot.database import get_portfolio
from bot.keyboards import portfolio_inline, main_menu

router = Router()


@router.message(Command("portfolio"))
async def cmd_portfolio(message: Message):
    items = await get_portfolio()
    if not items:
        await message.answer(
            "📂 Портфолио пока пусто. Загляните позже!",
            reply_markup=main_menu(),
        )
        return
    for item in items:
        text = (
            f"<b>{item['title']}</b>\n\n"
            f"{item['description'] or ''}\n"
            f"Тип: {item['order_type'] or 'не указан'}"
        )
        kb = portfolio_inline(item['id'], item['site_url'])
        if item['image_url']:
            await message.answer_photo(
                photo=item['image_url'],
                caption=text,
                reply_markup=kb,
            )
        else:
            await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("order_same:"))
async def order_same_callback(callback: CallbackQuery):
    portfolio_id = callback.data.split(":")[1]
    await callback.message.answer(
        "📝 Отправьте /order и укажите, что хотите сайт как в портфолио.\n"
        "Или просто опишите задачу.",
        reply_markup=main_menu(),
    )
    await callback.answer()

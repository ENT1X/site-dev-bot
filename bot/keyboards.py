from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
)

from bot.config import WEBAPP_URL


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="📂 Портфолио")],
            [KeyboardButton(text="📝 Заказать сайт"), KeyboardButton(text="💬 Связь с нами")],
            [KeyboardButton(text="🌐 Mini App", web_app=WebAppInfo(url=WEBAPP_URL))],
        ],
        resize_keyboard=True,
    )


def mini_app_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Открыть Mini App",
                web_app=WebAppInfo(url=WEBAPP_URL),
            )]
        ]
    )


def portfolio_inline(portfolio_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Смотреть сайт", url="https://example.com")],
            [InlineKeyboardButton(text="📝 Заказать такой же", callback_data=f"order_same:{portfolio_id}")],
        ]
    )


def contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Отправить номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from bot.config import WEBAPP_URL


def main_menu():
    if WEBAPP_URL:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="🚀 Открыть Mini App", web_app=WebAppInfo(url=WEBAPP_URL))]],
            resize_keyboard=True,
        )
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🚀 Mini App")]],
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


def portfolio_inline(portfolio_id: int, site_url: str | None = None):
    buttons = []
    if site_url:
        buttons.append([InlineKeyboardButton(text="🔗 Смотреть сайт", url=site_url)])
    buttons.append([InlineKeyboardButton(text="📝 Заказать такой же", callback_data=f"order_same:{portfolio_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def contact_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Отправить номер", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

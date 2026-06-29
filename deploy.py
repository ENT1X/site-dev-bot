import os
import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from bot.config import BOT_TOKEN
from bot.database import init_db, get_user, get_user_orders, get_portfolio
from bot.handlers import start, portfolio, orders, feedback

logging.basicConfig(level=logging.INFO)

bot: Bot | None = None
dp: Dispatcher | None = None
bot_task: asyncio.Task | None = None


async def start_bot():
    global bot, dp
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN not set")
        return
    try:
        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
        dp.include_routers(start.router, portfolio.router, orders.router, feedback.router)
        await init_db()
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Bot failed to start: {e}")


async def stop_bot():
    if bot:
        await bot.session.close()


@asynccontextmanager
async def lifespan(application: FastAPI):
    global bot_task
    await init_db()
    bot_task = asyncio.create_task(start_bot())
    yield
    bot_task.cancel()
    await stop_bot()


app = FastAPI(lifespan=lifespan)

app.mount("/webapp", StaticFiles(directory="webapp", html=True), name="webapp")


@app.get("/api/health")
async def api_health():
    return {"status": "ok"}


@app.get("/api/user/{telegram_id}")
async def api_get_user(telegram_id: int):
    user = await get_user(telegram_id)
    return dict(user) if user else {"error": "not found"}


@app.get("/api/user/{telegram_id}/orders")
async def api_get_orders(telegram_id: int):
    orders_list = await get_user_orders(telegram_id)
    return [dict(o) for o in orders_list]


@app.get("/api/portfolio")
async def api_portfolio():
    items = await get_portfolio()
    return [dict(i) for i in items]


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

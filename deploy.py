import os
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from bot.database import init_db, get_user, get_user_orders, get_portfolio

logging.basicConfig(level=logging.INFO)

bot_task = None


async def run_bot():
    try:
        from aiogram import Bot, Dispatcher
        from aiogram.client.default import DefaultBotProperties
        from aiogram.enums import ParseMode
        from bot.handlers import start, portfolio, orders, feedback
        from bot.config import BOT_TOKEN

        if not BOT_TOKEN:
            logging.error("BOT_TOKEN not set, bot not starting")
            return

        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
        dp.include_routers(start.router, portfolio.router, orders.router, feedback.router)
        logging.info("Bot starting polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Bot crashed: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(application: FastAPI):
    global bot_task
    await init_db()
    if os.getenv("BOT_TOKEN"):
        bot_task = asyncio.create_task(run_bot())
    else:
        logging.warning("BOT_TOKEN not set, skipping bot start")
    yield
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except (asyncio.CancelledError, Exception):
            pass


app = FastAPI(lifespan=lifespan)
app.mount("/webapp", StaticFiles(directory="webapp", html=True), name="webapp")


@app.get("/api/health")
async def api_health():
    return {"status": "ok"}


@app.get("/api/debug")
async def api_debug():
    return {
        "bot_token_set": bool(os.getenv("BOT_TOKEN")),
        "webapp_url": os.getenv("WEBAPP_URL"),
        "admin_ids": os.getenv("ADMIN_IDS"),
    }


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

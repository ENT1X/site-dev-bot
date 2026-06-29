import os
import sys
import subprocess
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from bot.database import init_db, get_user, get_user_orders, get_portfolio

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.mount("/webapp", StaticFiles(directory="webapp", html=True), name="webapp")

bot_process = None


@app.on_event("startup")
async def startup():
    global bot_process
    await init_db()
    bot_token = os.getenv("BOT_TOKEN")
    if bot_token:
        logging.info("Starting bot process...")
        bot_process = subprocess.Popen(
            [sys.executable, "-m", "bot.main"],
            env={**os.environ},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


@app.on_event("shutdown")
async def shutdown():
    global bot_process
    if bot_process:
        bot_process.terminate()
        bot_process.wait()


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

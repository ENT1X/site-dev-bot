import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from bot.database import get_user, get_user_orders, get_portfolio

app = FastAPI(title="SiteDev Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
WEBAPP_DIR = BASE_DIR / "webapp"

app.mount("/webapp", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")


@app.get("/api/user/{telegram_id}")
async def api_get_user(telegram_id: int):
    user = await get_user(telegram_id)
    if not user:
        return {"error": "User not found"}
    return dict(user)


@app.get("/api/user/{telegram_id}/orders")
async def api_get_user_orders(telegram_id: int):
    orders = await get_user_orders(telegram_id)
    return [dict(o) for o in orders]


@app.get("/api/portfolio")
async def api_get_portfolio():
    items = await get_portfolio()
    return [dict(i) for i in items]


@app.get("/")
async def root():
    return {"status": "ok", "message": "SiteDev Bot API"}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

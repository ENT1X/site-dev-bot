import aiosqlite
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "data" / "database.db"


async def init_db():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                username TEXT,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_type TEXT NOT NULL,
                description TEXT NOT NULL,
                budget TEXT,
                status TEXT DEFAULT 'new',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                image_url TEXT,
                site_url TEXT,
                order_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)


async def get_user(telegram_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return await cursor.fetchone()


async def create_user(telegram_id: int, full_name: str, username: str | None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (telegram_id, full_name, username) VALUES (?, ?, ?)",
            (telegram_id, full_name, username),
        )
        await db.commit()


async def update_user_phone(telegram_id: int, phone: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET phone = ? WHERE telegram_id = ?", (phone, telegram_id))
        await db.commit()


async def create_order(user_id: int, order_type: str, description: str, budget: str | None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO orders (user_id, order_type, description, budget) VALUES (?, ?, ?, ?)",
            (user_id, order_type, description, budget),
        )
        await db.commit()
        return cursor.lastrowid


async def get_user_orders(telegram_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT o.* FROM orders o
               JOIN users u ON o.user_id = u.id
               WHERE u.telegram_id = ?
               ORDER BY o.created_at DESC""",
            (telegram_id,),
        )
        return await cursor.fetchall()


async def get_portfolio():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM portfolio ORDER BY created_at DESC")
        return await cursor.fetchall()


async def seed_portfolio():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM portfolio")
        count = (await cursor.fetchone())[0]
        if count > 0:
            return
        items = [
            ("Интернет-магазин «TrendShop»", "Модный интернет-магазин одежды с корзиной, фильтрами и онлайн-оплатой. Адаптивный дизайн, интеграция с CDEK.", "https://example.com/trendshop", "Интернет-магазин"),
            ("Лендинг «SmartHome»", "Одностраничный сайт для компании по умным домам. Анимации, форма заявки, калькулятор стоимости.", "https://example.com/smarthome", "Лендинг"),
            ("Корпоративный сайт «LawPrime»", "Сайт юридической компании с портфолио дел, блогом и личным кабинетом клиента.", "https://example.com/lawprime", "Корпоративный сайт"),
            ("Веб-приложение «TaskFlow»", "Система управления задачами с канбан-доской, командной работой и уведомлениями в Telegram.", "https://example.com/taskflow", "Веб-приложение"),
            ("Сайт-визитка «FotoArt»", "Портфолио фотографа с галереей, lightbox-просмотром и формой бронирования съёмок.", "https://example.com/fotoart", "Лендинг"),
            ("CRM «BizControl»", "Облачная CRM для малого бизнеса: сделки, клиенты, аналитика, интеграция с WhatsApp.", None, "Веб-приложение"),
        ]
        await db.executemany(
            "INSERT INTO portfolio (title, description, site_url, order_type) VALUES (?, ?, ?, ?)",
            items,
        )
        await db.commit()

from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
import db
from handlers import router
import os
import asyncio


async def main():
    await db.init_db()

    load_dotenv()
    token = os.getenv('TG_BOT_API_KEY')
    if not token:
        raise ValueError("Токен не найден")

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await db.close_db()


if __name__ == '__main__':
    asyncio.run(main())

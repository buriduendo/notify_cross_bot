import asyncio

from aiogram import Bot, Dispatcher, BaseMiddleware

from config import TOKEN
from database.models import async_main, async_session
from handlers.admin import admin_router
from handlers.user import user_router
from handlers.start import start_router
from middleware.db import DataBaseSession
from notify import start_notify_forms


async def main():
    await async_main()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.update.middleware(DataBaseSession(session_pool=async_session))
    dp.include_routers(admin_router, user_router, start_router)

    async with async_session() as session:
        await start_notify_forms(session=session)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




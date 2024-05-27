from aiogram.filters import Filter
from aiogram import types
from database.requests import get_admin_tg_ids, get_user_tg_ids
from sqlalchemy.ext.asyncio import AsyncSession


class AdminProtect(Filter):
    async def __call__(self, message: types, session: AsyncSession):
        admin_list = await get_admin_tg_ids(session)
        return message.from_user.id in admin_list


class Users(Filter):
    async def __call__(self, message: types, session: AsyncSession):
        user = await get_user_tg_ids(session)
        return message.from_user.id in user

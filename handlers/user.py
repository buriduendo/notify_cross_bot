from aiogram import Router, types, F
from filtres.user_types import Users
from database.requests import get_nearby_events, get_past_events, get_link_on_reg_lec, get_link_on_reg_ct
from sqlalchemy.ext.asyncio import AsyncSession

user_router = Router()
user_router.message.filter(Users())


@user_router.message(F.text == "Посмотреть ближайшие события")
async def nearby_events(message: types.Message, session: AsyncSession):
    events = await get_nearby_events(session)
    if events:
        for element in events:
            await message.answer(f"Название: {element.lectureName}\n"
                                 f"Мероприятие: {element.event.eventType}\n"
                                 f"Автор: {element.worker.firstName} {element.worker.lastName}\n"
                                 f"Дата: {element.event.dateOfEvent}\n"
                                 f"Время начала: {element.event.timeOfEvent}")
    else:
        await message.answer(f"Мероприятий не наблюдается")


@user_router.message(F.text == "Посмотреть прошедшие события")
async def past_events(message: types.Message, session: AsyncSession):
    events = await get_past_events(session)
    if events:
        for element in events:
            await message.answer(f"Название: {element.lectureName}\n"
                                 f"Мероприятие: {element.event.eventType}\n"
                                 f"Автор: {element.worker.firstName} {element.worker.lastName}\n"
                                 f"Дата: {element.event.dateOfEvent}\n"
                                 f"\nЗапись мероприятия по ссылке:\n{element.event.videoLink}\n"
                                 f"\nОбратная связь:\n{element.event.feedBackLink}")

    else:
        await message.answer(f"Мероприятия не проходили")


@user_router.message(F.text == "Стать лектором/спикером")
async def become(message: types.Message, session: AsyncSession):
    lecture = await get_link_on_reg_lec(session)
    cross_talk = await get_link_on_reg_ct(session)
    if lecture:
        await message.answer(f"{lecture.notificationText}\n"
                             f"{lecture.link}")
    if cross_talk:
        await message.answer(f"{cross_talk.notificationText}\n"
                             f"{cross_talk.link}")


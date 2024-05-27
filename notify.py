from config import TOKEN
from aiogram import Bot
from datetime import timedelta, datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession
from database.requests import get_user_tg_ids, get_link_on_reg_ct, get_link_on_reg_lec



bot = Bot(token=TOKEN)


async def send_reminder_7_days(users):
    # Логика для отправки напоминания за 7 дней до события
    for user in users:
        await bot.send_message(chat_id=user, text="Привет, напоиманю, что через 7 тебя ждет мероприятия от КТСГ!")


async def send_reminder_3_days(event_date, users):
    # Логика для отправки напоминания за 3 дня до события
    for user in users:
        await bot.send_message(chat_id=user, text="Привет, уже через 3 дня мы встретимся на мероприятии от КТСГ!")


async def send_reminder_5_min(users):
    #Логика для отправки напоминания за 5 минут до события
    for user in users:
        await bot.send_message(chat_id=user, text="Привет, начало через 5 минут, подключайся!!")


async def send_feedback_link(users):
    #Логика для отправки ссылки на обратную связь
    for user in users:
        await bot.send_message(chat_id=user, text="Привет, нам важно твое мнение о пройденом мероприятии, "
                                                  "оставить обратную связь можешь ниже по ссыле!\n"
                                                  "https://docs.google.com/forms/d/e/1FAIpQLSeaY3T"
                                                  "b1gX97BJ71CnRL4Ra_8QTNgRx8XG16SB2IR22pkz6ow/viewform?usp=sf_link ")


async def start_scheduler(date, time, event_id, session: AsyncSession):
    scheduler = AsyncIOScheduler()

    users = await get_user_tg_ids(session)

    event_date = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")

    # Напоминание за 7 дней до события
    scheduler.add_job(send_reminder_7_days, 'date', run_date=event_date - timedelta(days=7), args=[users])

    # Напоминание за 3 дня до события
    scheduler.add_job(send_reminder_3_days, 'date', run_date=event_date - timedelta(days=3), args=[users])

    # Напоминание за 5 минут до события
    scheduler.add_job(send_reminder_5_min, 'date', run_date=event_date - timedelta(minutes=5), args=[users])

    # Отправка ссылки на обратную связь после события
    scheduler.add_job(send_feedback_link, 'date', run_date=event_date + timedelta(hours=3), args=[users])

    scheduler.start()


async def start_notify_forms(session: AsyncSession):
    scheduler = AsyncIOScheduler()

    users = await get_user_tg_ids(session)

    scheduler.add_job(send_link_on_form_cross_talk, 'interval', weeks=12, next_run_time=datetime.now(),
                      args=[session, users])

    scheduler.add_job(send_link_on_form_lecture,
                      'interval', weeks=4, next_run_time=datetime.now() + timedelta(seconds=1), args=[session, users])

    scheduler.start()


async def send_link_on_form_cross_talk(session: AsyncSession, users):

    cross_talk = await get_link_on_reg_ct(session)
    if cross_talk:
        for user in users:
            await bot.send_message(chat_id=user, text=f"{cross_talk.notificationText}\n{cross_talk.link}")


async def send_link_on_form_lecture(session: AsyncSession, users):

    lecture = await get_link_on_reg_lec(session)
    if lecture:
        for user in users:
            await bot.send_message(chat_id=user, text=f"{lecture.notificationText}\n{lecture.link}")
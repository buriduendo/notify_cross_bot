from database.models import Worker, Event, Notification, Material
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from sqlalchemy.orm import joinedload

import datetime


async def get_admin_tg_ids(session: AsyncSession) -> list[int]:
    admin_users = await session.execute(select(Worker.tgID).where(Worker.isAdmin == True))
    return [admin.tgID for admin in admin_users.all()]


async def get_user_tg_ids(session: AsyncSession) -> list[int]:
    users = await session.execute(select(Worker.tgID).where(Worker.tgID > 0))
    user_list = list()
    for user in users:
        if user.tgID:
            user_list.append(user.tgID)

    return user_list


async def get_worker_form_email(session: AsyncSession, email_user):
    worker = await session.execute(select(Worker).where(Worker.email == email_user))
    return worker.scalar()


async def authentication(session: AsyncSession, email_user, password_user):
    email = await session.execute(
        select(Worker).where(Worker.password == password_user, Worker.email == email_user))
    return email.scalar()


async def add_tg_id_at_first_time(session: AsyncSession, email: str, password: str, tg_id: int):
    worker = await session.execute(select(Worker).where(Worker.email == email, Worker.password == password))
    worker_obj = worker.scalar()
    if worker_obj:
        worker_obj.tgID = tg_id
        worker_obj.password = ""
        await session.commit()
    else:
        raise ValueError("Worker not found")


async def get_nearby_events(session: AsyncSession):
    now = datetime.datetime.now()
    events = await session.execute(
        select(Material, Event, Worker)
        .join(Material.worker).join(Material.event)
        .options(joinedload(Material.worker), joinedload(Material.event))
        .where(
            and_(
                func.date(Event.dateOfEvent) >= now.date(),
                func.time(Event.timeOfEvent) >= now.time()
            )
        )
    )
    return events.scalars().all()


async def get_past_events(session: AsyncSession):
    events = await session.execute(
        select(Material, Event, Worker)
        .join(Material.worker).join(Material.event)
        .options(joinedload(Material.worker), joinedload(Material.event))
        .where(Event.dateOfEvent < datetime.datetime.now())
    )
    return events.scalars().all()


async def get_link_on_reg_lec(session: AsyncSession):
    link_on_lecture = await session.execute(
        select(Notification).where(Notification.notificationType == "Лекция"))
    return link_on_lecture.scalar()


async def get_link_on_reg_ct(session: AsyncSession):
    link_on_ct = await session.execute(select(Notification).where(Notification.notificationType == "CrossTalk"))
    return link_on_ct.scalar()


async def add_user_in_db(session: AsyncSession, data: dict):
    obj = Worker(
        firstName=data["firstName"],
        lastName=data["lastName"],
        email=data["email"],
        password=data["password"],
        isAdmin=data["isAdmin"]
    )
    session.add(obj)
    await session.commit()


async def add_material_in_db(session: AsyncSession, data: dict):
    obj = Material(
        lectureName=data["lectureName"],
        workerId=data["workerId"],
        eventId=0
    )
    session.add(obj)
    await session.commit()


async def add_event_id_in_material(session: AsyncSession, material_id, event_id):
    await session.execute(update(Material).where(Material.id == material_id).values(eventId=event_id,))
    await session.commit()


async def add_event_in_db(session: AsyncSession, data: dict):
    obj = Event(
        eventType=data["eventType"],
        dateOfEvent=data["dateOfEvent"],
        timeOfEvent=data["timeOfEvent"],
        eventLink=data["eventLink"]
    )
    session.add(obj)
    await session.commit()


async def get_free_materials(session: AsyncSession):
    materials = await session.execute(select(Material).where(Material.eventId == 0))
    return [material.lectureName for material in materials.scalars().all()]


async def get_material(session: AsyncSession, lecture_name):
    material = await session.execute(
        select(Material).where(Material.eventId == 0, Material.lectureName == lecture_name))
    return material.scalar()


async def get_event_id(session: AsyncSession, link):
    event = await session.execute(select(Event).where(Event.eventLink == link))
    return event.scalar().id

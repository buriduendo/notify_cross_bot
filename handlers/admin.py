from aiogram import Router, types, F
from datetime import datetime
from aiogram.filters import Command
from filtres.user_types import AdminProtect
from database.requests import (add_user_in_db, get_worker_form_email, add_material_in_db, add_event_in_db,
                               get_free_materials, get_material, add_event_id_in_material, get_event_id)
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from notify import start_scheduler
from keyboards.reply import user_kb, admin_kb


admin_router = Router()
admin_router.message.filter(AdminProtect())


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=admin_kb)


class AddUser(StatesGroup):
    firstName = State()
    lastName = State()
    email = State()
    password = State()
    isAdmin = State()
    addInDb = State()


@admin_router.message(F.text == "Добавить пользователя")
async def add_user(message: types.Message, state: FSMContext):
    await message.answer("Введите имя нового пользователя:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddUser.firstName)


@admin_router.message(AddUser.firstName)
async def add_user_first_name(message: types.Message, state: FSMContext):
    first_name = message.text
    if first_name == "отмена":
        await state.clear()
    else:
        await state.update_data(firstName=first_name)
        await message.answer("Введите фамилию нового пользователя")
        await state.set_state(AddUser.lastName)


@admin_router.message(AddUser.lastName)
async def add_user_last_name(message: types.Message, state: FSMContext):
    last_name = message.text
    if last_name == "отмена":
        await state.clear()
    else:
        await state.update_data(lastName=last_name)
        await message.answer("Введите email нового пользователя")
        await state.set_state(AddUser.email)


@admin_router.message(AddUser.email)
async def add_user_email(message: types.Message, state: FSMContext):
    email = message.text
    if email == "отмена":
        await state.clear()
    else:
        await state.update_data(email=email)
        await message.answer("Введите пароль для нового пользователя")
        await state.set_state(AddUser.password)


@admin_router.message(AddUser.password)
async def add_user_password(message: types.Message, state: FSMContext):
    password = message.text
    if password == "отмена":
        await state.clear()
    else:
        await state.update_data(password=password)
        await message.answer("Будет ли новый пользователь администратором?")
        await state.set_state(AddUser.isAdmin)


@admin_router.message(AddUser.isAdmin)
async def add_user_is_admin(message: types.Message, state: FSMContext):
    txt = message.text.lower()
    if txt == "да" or txt == "нет":
        is_admin = True if txt == "да" else False
        await state.update_data(isAdmin=is_admin)
        data = await state.get_data()
        await message.answer(f"Добавить пользователя:\n{data}")
        await state.set_state(AddUser.addInDb)
    else:
        await message.answer("Введите да или нет!")


@admin_router.message(AddUser.addInDb)
async def add_user_password(message: types.Message, session: AsyncSession, state: FSMContext):
    txt = message.text.lower()
    if txt == "да":
        data = await state.get_data()
        await add_user_in_db(session, data)
        await message.answer(f"Пользователь добавлен!", reply_markup=admin_kb)
        await state.clear()
    elif txt == "нет":
        await message.answer(f"Пользователь добавлен не был добавлен!", reply_markup=admin_kb)
        await state.clear()
    else:
        await message.answer("Введите да или нет!")


class AddMaterial(StatesGroup):
    lectureName = State()
    workerId = State()


@admin_router.message(F.text == "Добавить материал")
async def add_material(message: types.Message, state: FSMContext):
    await message.answer("Введите название лекции:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddMaterial.lectureName)


@admin_router.message(AddMaterial.lectureName)
async def add_material_lecture_name(message: types.Message, state: FSMContext):
    lecture_name = message.text
    await state.update_data(lectureName=lecture_name)
    await message.answer("Введите email сотрудника, который подготовит материал")
    await state.set_state(AddMaterial.workerId)


@admin_router.message(AddMaterial.workerId)
async def add_user_last_name(message: types.Message, state: FSMContext, session: AsyncSession):
    email = message.text
    if event_type == "отмена":
        await state.clear()
    else:
        worker = await get_worker_form_email(session, email)
        if worker:
            worker_id = worker.id
            await state.update_data(workerId=worker_id)
            data = await state.get_data()
            await add_material_in_db(session, data)
            await message.answer("Материал добавлен!", reply_markup=admin_kb)
            await state.clear()
        else:
            await message.answer("Пользователь с данной почтой не найден, введите другую или исправте ошибку!")


class AddEvent(StatesGroup):
    eventType = State()
    date = State()
    time = State()
    material = State()
    link = State()
    addMore = State()


@admin_router.message(F.text == "Создать событие")
async def add_event(message: types.Message, state: FSMContext):
    await message.answer("Введите тип события(Лекция/CrossTalk)", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddEvent.eventType)


@admin_router.message(AddEvent.eventType)
async def add_event_type(message: types.Message, state: FSMContext):
    event_type = message.text.lower()
    if event_type == "отмена":
        await state.clear()
    else:
        if event_type == "лекция":
            await state.update_data(eventType=event_type)
            await message.answer("Введите дату события(в формате dd.mm.yyyy:")
            await state.set_state(AddEvent.date)
        elif event_type == "crosstalk":
            await state.update_data(eventType=event_type)
            await message.answer("Введите дату события(в формате dd.mm.yyyy)")
            await state.set_state(AddEvent.date)
        else:
            await message.answer("Введи лекция или CrossTalk")


@admin_router.message(AddEvent.date)
async def add_event_date(message: types.Message, state: FSMContext):
    if message.text == "отмена":
        await state.clear()
    else:
        date = datetime.strptime(message.text, "%d.%m.%Y").date()
        await state.update_data(dateOfEvent=date)
        await message.answer("Введите время начала события(в формате 00:00)")
        await state.set_state(AddEvent.time)


@admin_router.message(AddEvent.time)
async def add_event_time(message: types.Message, state: FSMContext):
    if message.text == "отмена":
        await state.clear()
    else:
        time = datetime.strptime(message.text, "%H:%M").time()
        await state.update_data(timeOfEvent=time)
        await message.answer("Введите ссылку события")
        await state.set_state(AddEvent.link)


@admin_router.message(AddEvent.link)
async def add_event_link(message: types.Message, state: FSMContext, session: AsyncSession):
    link = message.text
    if link == "отмена":
        await state.clear()
    else:
        await state.update_data(eventLink=link)
        data = await state.get_data()
        materials = await get_free_materials(session)
        if materials:
            await add_event_in_db(session, data)
            await message.answer("Укажите какие материалы будет включать событие")
            for element in materials:
                await message.answer(f"{element}")
            await state.set_state(AddEvent.material)
        else:
            await message.answer("Нет доступных материалов", reply_markup=admin_kb)
            await state.clear()


@admin_router.message(AddEvent.material)
async def add_event_material(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "!стоп":
        await message.answer("Событе создано!", reply_markup=admin_kb)
        await state.clear()
    else:
        data = await state.get_data()
        event_type = data["eventType"]
        link = data["eventLink"]
        date = data["dateOfEvent"]
        time = data["timeOfEvent"]
        event_id = await get_event_id(session, link)
        if event_type == "лекция":
            txt = message.text
            mat = await get_material(session, txt)
            if mat:
                mat_id = mat.id
                await add_event_id_in_material(session, mat_id, event_id)
                await message.answer("Событе добавлено!", reply_markup=admin_kb)
                await state.clear()
                await start_scheduler(date, time, event_id, session)
            else:
                await message.answer("Ты ввел некорректное название материала!")
        else:
            txt = message.text
            mat = await get_material(session, txt)
            if mat:
                mat_id = mat.id
                await add_event_id_in_material(session, mat_id, event_id)
                await message.answer("Категория добавлена!")
                materials = await get_free_materials(session)
                if materials:
                    await message.answer('Укажите еще какие материалы будет включать событие или напишите "!стоп"')
                    for element in materials:
                        await message.answer(f"{element}")
                    await state.set_state(AddEvent.material)
                else:
                    await message.answer("Нет доступных материалов")
                    await message.answer("Событе добавлено!", reply_markup=admin_kb)
                    await start_scheduler(date, time, event_id, session)
                    await state.clear()
            else:
                await message.answer("Больше нет доступных материалов")
                await message.answer("Событе добавлено!", reply_markup=admin_kb)
                await start_scheduler(date, time, event_id, session)
                await state.clear()


@admin_router.message(F.text == "Пользовательское меню")
async def edit_user(message: types.Message):
    await message.answer("Вам доступен пользовательский функционал!", reply_markup=user_kb)


@admin_router.message(F.text == "Изменить пользователя" or F.text == "Изменить событие")
async def edit_user(message: types.Message):
    await message.answer("В процессе разработки!")


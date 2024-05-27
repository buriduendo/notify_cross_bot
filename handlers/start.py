from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.requests import get_worker_form_email, get_user_tg_ids, authentication, add_tg_id_at_first_time
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.reply import user_kb


start_router = Router()


class UserAuth(StatesGroup):
    email = State()
    password = State()


class FirstContact(UserAuth):
    @start_router.message(CommandStart())
    async def start(message: types.Message, session: AsyncSession, state: FSMContext):
        user_list = await get_user_tg_ids(session)
        if message.from_user.id not in user_list:
            await message.answer('Пожалуйста, введите ваш email:')
            await state.set_state(UserAuth.email)
        else:
            await message.answer(
                """Привет!
                \nЭтот бот создан для оповещения сотрудников КТСГ о различных мероприятиях! В настоящий момент ты можешь узнать о ближайших лекциях и митапах CrossTalks!
                \nКстати, здесь ты можешь оставить заявку на проведение лекции, или на участие в CrossTalks в качестве спикера!
                \nПо всем возникающим вопросам можно обращаться ко мне @ilovedem0cracy, я на связи с 10 до 18 часов (кроме субботы и воскресенья)""",
                reply_markup=user_kb)

    @start_router.message(UserAuth.email)
    async def check_email(message: types.Message, state: FSMContext, session: AsyncSession):
        user_email = message.text
        db_email = await get_worker_form_email(session, user_email)
        if db_email:
            await message.answer(f"Введите пароль:")
            await state.update_data(email=user_email)
            await state.set_state(UserAuth.password)
        else:
            await message.answer("Email не найден, или вы допустили оишибку.\nВведите email снова:")

    @start_router.message(UserAuth.password)
    async def check_email(message: types.Message, state: FSMContext, session: AsyncSession):
        data = await state.get_data()
        password = str(message.text)
        email = data["email"]
        auth = await authentication(session, email, password)
        if auth is not None:
            tgID = message.from_user.id
            await add_tg_id_at_first_time(session, email, password, tgID)
            await message.answer(f"Успешно")
            await message.answer(
                """Привет!
                \nЭтот бот создан для оповещения сотрудников КТСГ о различных мероприятиях! В настоящий момент ты можешь узнать о ближайших лекциях и митапах CrossTalks!
                \nКстати, здесь ты можешь оставить заявку на проведение лекции, или на участие в CrossTalks в качестве спикера!
                \nПо всем возникающим вопросам можно обращаться ко мне @ilovedem0cracy, я на связи с 10 до 18 часов (кроме субботы и воскресенья)""",
                reply_markup=user_kb)
            await state.clear()
        else:
            await message.answer(f"Неверный пароль")



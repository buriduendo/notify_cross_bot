from aiogram import types
from aiogram.types import KeyboardButton

view_nearby_event_btn = KeyboardButton(text='Посмотреть ближайшие события')
view_past_event_btn = KeyboardButton(text='Посмотреть прошедшие события')
become_btn = KeyboardButton(text='Стать лектором/спикером')

user_kb = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [view_nearby_event_btn, view_past_event_btn],
        [become_btn]
    ]
)

create_event_btn = KeyboardButton(text='Создать событие')
add_material_btn = KeyboardButton(text='Добавить материал')
add_user_btn = KeyboardButton(text='Добавить пользователя')
edit_user_btn = KeyboardButton(text='Изменить пользователя')
edit_event_btn = KeyboardButton(text='Изменить событие')
user_menu_btn = KeyboardButton(text='Пользовательское меню')

admin_kb = types.ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [add_material_btn, create_event_btn],
        [add_user_btn, user_menu_btn],
        [edit_user_btn, edit_event_btn]
    ]
)
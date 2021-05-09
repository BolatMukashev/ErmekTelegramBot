from aiogram import types
from messages import buttons


def create_keyboard_with_cancel_button(iterable_object: list):
    """Создать клавиатуру по списку + кнопка Отмена"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for el in iterable_object:
        button = types.KeyboardButton(el)
        markup.add(button)
    cancel_button = types.KeyboardButton(buttons['cancel'])
    markup.add(cancel_button)
    return markup


def create_keyboard_with_back_button(iterable_object: list):
    """Создать клавиатуру по списку + кнопка Назад"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for el in iterable_object:
        button = types.KeyboardButton(el)
        markup.add(button)
    cancel_button = types.KeyboardButton(buttons['back'])
    markup.add(cancel_button)
    return markup

from aiogram import types


def create_keyboard(iterable_object: list):
    """Создать клавиатуру по списку"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for el in iterable_object:
        button = types.KeyboardButton(el)
        markup.add(button)
    return markup

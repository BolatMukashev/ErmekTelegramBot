from aiogram import types


def create_keyboard(iterable_object: list):
    """Создать клавиатуру по списку"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for el in iterable_object:
        button = types.KeyboardButton(el)
        markup.add(button)
    cancel_button = types.KeyboardButton('🔙 Отмена')
    markup.add(cancel_button)
    return markup

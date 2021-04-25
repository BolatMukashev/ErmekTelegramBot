from aiogram import types

back_button = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button1 = types.KeyboardButton('Назад')
back_button.add(button1)

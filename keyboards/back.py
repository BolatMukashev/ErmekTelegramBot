from aiogram import types
from messages import buttons

back_button = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button1 = types.KeyboardButton(buttons['back'])
back_button.add(button1)

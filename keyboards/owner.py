from aiogram import types

owner_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button1 = types.KeyboardButton('Владелец')
button2 = types.KeyboardButton('Арендатор')
owner_buttons.add(button1, button2)

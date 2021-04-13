from aiogram import types

next_choice_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button1 = types.KeyboardButton('Добавить товар')
button2 = types.KeyboardButton('Удалить товар')
button3 = types.KeyboardButton('Завершить 📄')
next_choice_buttons.add(button1, button2)
next_choice_buttons.add(button3)

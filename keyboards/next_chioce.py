from aiogram import types
import messages

next_choice_buttons = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button1 = types.KeyboardButton(messages.buttons['add'])
button2 = types.KeyboardButton(messages.buttons['delete'])
button3 = types.KeyboardButton(messages.buttons['cancel'])
button4 = types.KeyboardButton(messages.buttons['end'])
next_choice_buttons.add(button1, button2)
next_choice_buttons.add(button3)
next_choice_buttons.add(button4)

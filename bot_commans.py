from bot import dp, bot
from functions import *
from aiogram import types
from aiogram.dispatcher import FSMContext


@dp.message_handler(commands="set_commands", state="*")
async def cmd_set_commands(message: types.Message):
    user_id = message.from_user.id
    if user_id == config.ADMIN_ID:
        commands = [types.BotCommand(command="/request", description="Новая заявка")]
        await bot.set_my_commands(commands)
        await message.answer("Команды установлены!")


@dp.message_handler(commands=["start"])
async def command_start(message: types.Message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    await message.answer(f'Привет, {full_name}!\nТвой Telegram ID: {telegram_id}')
    if telegram_id == config.ADMIN_ID:
        await message.answer('Как админу, тебе доступны команды:\n/set_commands')


@dp.message_handler(commands=["request"])
async def command_request(message: types.Message):
    telegram_id = message.from_user.id
    if check_id(telegram_id, get_trusted_id()):
        await message.answer(f'Ты допущен к этой функции')

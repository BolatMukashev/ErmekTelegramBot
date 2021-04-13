# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
from apiclient import discovery
import config


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class Request(StatesGroup):
    District: State = State()
    ShopName: State = State()
    ProductCategory = State()
    Product = State()
    Number = State()


class RequestAdd(StatesGroup):
    ProductCategory = State()
    Product = State()
    Number = State()


class DeleteProduct(StatesGroup):
    Delete = State()


# Авторизуемся и получаем service — экземпляр доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    config.CREDENTIALS_FILE_NAME,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4', http=httpAuth)


if __name__ == "__main__":
    from bot_commans import dp
    executor.start_polling(dp, skip_updates=True)

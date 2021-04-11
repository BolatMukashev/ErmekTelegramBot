from bot import dp, bot, Request, RequestAdd
from functions import *
from aiogram import types
from aiogram.dispatcher import FSMContext


@dp.message_handler(commands="set_commands", state="*")
async def cmd_set_commands(message: types.Message):
    user_id = message.from_user.id
    if user_id == config.ADMIN_ID:
        commands = [types.BotCommand(command="/new_request", description="Новая заявка")]
        await bot.set_my_commands(commands)
        await message.answer("Команды установлены!")


@dp.message_handler(commands=["start"])
async def command_start(message: types.Message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    await message.answer(f'Привет, {full_name}!\nТвой Telegram ID: {telegram_id}')
    if telegram_id == config.ADMIN_ID:
        await message.answer('Как админу, тебе доступны команды:\n/set_commands')


@dp.message_handler(commands=["new_request"], state="*")
async def command_request(message: types.Message):
    telegram_id = message.from_user.id
    if check_id(telegram_id):
        available_districts = get_the_districts_available_to_the_employee(telegram_id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for el in available_districts:
            button = types.KeyboardButton(el)
            markup.add(button)
        await message.answer(f'Выбери район', reply_markup=markup)
        await Request.District.set()


@dp.message_handler(state=Request.District, content_types=types.ContentTypes.TEXT)
async def command_request_action_one(message: types.Message, state: FSMContext):
    district = message.text
    await state.update_data(district=district)
    data = await state.get_data()
    district = data['district']
    shops = get_shops_name_in_district(district)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for el in shops:
        button = types.KeyboardButton(el)
        markup.add(button)
    await message.answer(f'Выбери название торговой точки:', reply_markup=markup)
    await Request.next()


@dp.message_handler(state=Request.ShopName, content_types=types.ContentTypes.TEXT)
async def command_request_action_two(message: types.Message, state: FSMContext):
    shop_name = message.text
    await state.update_data(shop_name=shop_name)
    products_types = get_products_types()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for product_type in products_types:
        button = types.KeyboardButton(product_type)
        markup.add(button)
    await message.answer(f'Выбери категорию товара: ', reply_markup=markup)
    await Request.next()


@dp.message_handler(state=Request.ProductCategory, content_types=types.ContentTypes.TEXT)
async def command_request_action_three(message: types.Message, state: FSMContext):
    product_category = message.text
    await state.update_data(product_category=product_category)
    products_names = get_products_names_by_type(product_category)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for product in products_names:
        button = types.KeyboardButton(product)
        markup.add(button)
    await message.answer(f'Выбери товар: ', reply_markup=markup)
    await Request.next()


@dp.message_handler(state=Request.Product, content_types=types.ContentTypes.TEXT)
async def command_request_action_four(message: types.Message, state: FSMContext):
    product = message.text
    await state.update_data(product=product)
    await message.answer(f'Количество:', reply_markup=types.ReplyKeyboardRemove())
    await Request.next()


@dp.message_handler(state=Request.Number, content_types=types.ContentTypes.TEXT)
async def command_request_action_five(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    employee = get_employee_by_id(telegram_id)
    data = await state.get_data()
    shop = get_shop_by_name_and_district(data['shop_name'], data['district'])
    product = get_product_by_name(data['product'])
    product['Количество'] = int(message.text)
    product['Сумма'] = product['Цена'] * product['Количество']
    await state.update_data(product=product)
    order_data = {'employee': employee, 'shop': shop, 'orders': [product]}
    create_new_json_file(str(telegram_id), order_data)
    shop_data = [shop["Название"], shop['ИП/ТОО'], shop['Адрес'], shop['Телефон'],
                 shop['Кассовый аппарат']]
    await message.answer(f'Торговая точка:\n{", ".join(shop_data)}')
    order_data = ['Заявка:', product['Номенклатура'], f'Количество: {product["Количество"]}',
                  f'Цена: {int(product["Цена"])} тг', f'Сумма: {int(product["Сумма"])} тг']
    await message.answer('\n'.join(order_data))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = types.KeyboardButton('Добавить товар')
    button2 = types.KeyboardButton('Завершить 📄')
    markup.add(button1, button2)
    await message.answer(f'Что дальше?', reply_markup=markup)
    await state.finish()


@dp.message_handler(text='Добавить товар')
async def text_add_product(message: types.Message):
    products_types = get_products_types()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for product_type in products_types:
        button = types.KeyboardButton(product_type)
        markup.add(button)
    await message.answer(f'Выбери категорию товара: ', reply_markup=markup)
    await RequestAdd.ProductCategory.set()


@dp.message_handler(text='Завершить 📄')
async def text_the_end(message: types.Message):
    await message.answer('Ну пока!', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=RequestAdd.ProductCategory, content_types=types.ContentTypes.TEXT)
async def command_request_add_action_one(message: types.Message, state: FSMContext):
    product_category = message.text
    await state.update_data(product_category=product_category)
    products_names = get_products_names_by_type(product_category)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for product in products_names:
        button = types.KeyboardButton(product)
        markup.add(button)
    await message.answer(f'Выбери товар: ', reply_markup=markup)
    await RequestAdd.next()


@dp.message_handler(state=RequestAdd.Product, content_types=types.ContentTypes.TEXT)
async def command_request_add_action_two(message: types.Message, state: FSMContext):
    product = message.text
    await state.update_data(product=product)
    await message.answer(f'Количество:', reply_markup=types.ReplyKeyboardRemove())
    await RequestAdd.next()


@dp.message_handler(state=RequestAdd.Number, content_types=types.ContentTypes.TEXT)
async def command_request_add_action_three(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    data = await state.get_data()
    product = get_product_by_name(data['product'])
    product['Количество'] = message.text
    await state.update_data(product=product)
    order_data = get_data_from_json_file(telegram_id)
    order_data['orders'].append(product)
    edit_data_in_json_file(telegram_id, order_data)
    shop = order_data["shop"]
    orders = order_data["orders"]
    await message.answer(f'Итого:\n{shop}\n{orders}')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = types.KeyboardButton('Добавить товар')
    button2 = types.KeyboardButton('Завершить 📄')
    markup.add(button1, button2)
    await message.answer(f'Что дальше?', reply_markup=markup)
    await state.finish()

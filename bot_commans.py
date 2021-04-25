from bot import dp, bot, Request, RequestAdd, DeleteProduct, NewShop
from functions import *
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.next_chioce import next_choice_buttons
from keyboards.generated_keyboard import create_keyboard
from keyboards.owner import owner_buttons
from keyboards.back import back_button
from models import Shop
from excel_functions import new_doc


@dp.message_handler(commands="set_commands", state="*")
async def cmd_set_commands(message: types.Message):
    user_id = message.from_user.id
    if user_id in config.ADMINS_ID:
        commands = [types.BotCommand(command="/new_request", description="Новая заявка"),
                    types.BotCommand(command="/add_new_shop", description="Добавить торговую точку"),
                    types.BotCommand(command="/statistics", description="Показать статистику")]
        await bot.set_my_commands(commands)
        await message.answer("Команды установлены!")


@dp.message_handler(commands=["start"])
async def command_start(message: types.Message):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    await message.answer(f'Привет, {full_name}!\nТвой Telegram ID: {telegram_id}')
    await message.answer('Доступные команды:\n'
                         '/new_request - Новая заявка\n'
                         '/add_new_shop - Добавить торговую точку\n'
                         '/statistics - Показать статистику')
    if telegram_id in config.ADMINS_ID:
        await message.answer('Как админу, тебе доступны команды:\n/set_commands')


@dp.message_handler(commands=["statistics"], state="*")
async def command_statistics(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    employee = get_employee_by_id(telegram_id)
    if employee:
        try:
            employee_requests = get_table_data(config.REQUESTS, 'A2', 'Z10000', list_name=employee['Сокращенное имя'])
            all_requests_count = get_all_requests_count(employee_requests)
            total_sum = get_all_requests_total_sum(employee_requests)
            top_five_payable_shops_ever = get_top_five_payable_shops_ever(employee_requests)

            requests_count_today = get_requests_count_today(employee_requests)
            total_sum_today = get_all_requests_total_sum_today(employee_requests)
            top_five_payable_shops_today = get_top_five_payable_shops_today(employee_requests)

            requests_count_on_month = get_requests_count_on_this_month(employee_requests)
            requests_total_sum_on_month = get_all_requests_total_sum_on_this_month(employee_requests)
            top_five_payable_shops_on_this_month = get_top_five_payable_shops_on_this_month(employee_requests)

            requests_in_previous_month = get_requests_count_on_previous_month(employee_requests)
            requests_total_sum_on_previous_month = get_all_requests_total_sum_on_previous_month(employee_requests)
            top_five_payable_shops_on_previous_month = get_top_five_payable_shops_on_previous_month(employee_requests)

            requests_count_on_year = get_requests_count_on_this_year(employee_requests)
            requests_total_sum_on_this_year = get_all_requests_total_sum_on_this_year(employee_requests)
            top_five_payable_shops_on_this_year = get_top_five_payable_shops_on_this_year(employee_requests)

            messages = [
                ['Твоя статистика:'],
                [f'Заявок сегодня: {requests_count_today}',
                 f'На сумму: {total_sum_today} тг',
                 top_five_payable_shops_today],
                [f'Заявок в этом месяце: {requests_count_on_month}',
                 f'На сумму: {requests_total_sum_on_month} тг',
                 top_five_payable_shops_on_this_month],
                [f'Заявок за прошлый месяц: {requests_in_previous_month}',
                 f'На сумму: {requests_total_sum_on_previous_month} тг',
                 top_five_payable_shops_on_previous_month],
                [f'Заявок в этом году: {requests_count_on_year}',
                 f'На сумму: {requests_total_sum_on_this_year} тг',
                 top_five_payable_shops_on_this_year],
                [f'Заявок за все время: {all_requests_count}',
                 f'На сумму: {total_sum} тг',
                 top_five_payable_shops_ever]
            ]
            for mes in messages:
                await message.answer('\n'.join(mes), reply_markup=types.ReplyKeyboardRemove())
                await state.finish()
        except:
            await message.answer('Что то пошло не так, попробуйте позже!', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(text='🔙 Отмена', state="*")
async def text_cancel_action(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    data = get_data_from_json_file(telegram_id)
    for order in data['orders']:
        product_name = order['Номенклатура']
        number_of_product = order['Количество']
        all_products = get_all_products()
        convert_product_in_reserve_to_quantity(all_products, product_name, number_of_product)
        order['Количество'] = 0
    edit_data_in_json_file(telegram_id, data)
    await message.answer('Действие отменено', reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


@dp.message_handler(commands=["add_new_shop"], state="*")
async def command_add_new_shop(message: types.Message):
    telegram_id = message.from_user.id
    employee = get_employee_by_id(telegram_id)
    if employee:
        available_districts = get_the_districts_available_to_the_employee(employee)
        districts_keyboard = create_keyboard(available_districts)
        await message.answer('Чтобы добавить новую торговую точку, ответьте на несколько вопросов')
        await message.answer('В каком районе расположена торговая точка?', reply_markup=districts_keyboard)
        await NewShop.District.set()


@dp.message_handler(state=NewShop.District, content_types=types.ContentTypes.TEXT)
async def command_add_new_shop_action_one(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    district = message.text
    employee = get_employee_by_id(telegram_id)
    available_districts = get_the_districts_available_to_the_employee(employee)
    if district in available_districts:
        await state.update_data(district=district)
        await message.answer('Название торговой точки?', reply_markup=types.ReplyKeyboardRemove())
        await NewShop.next()
    else:
        await message.answer('Для добавления нового района обратитесь в офис')


@dp.message_handler(state=NewShop.ShopName, content_types=types.ContentTypes.TEXT)
async def command_add_new_shop_action_two(message: types.Message, state: FSMContext):
    shop_name = message.text
    shop_name = shop_name.strip()
    await state.update_data(shop_name=shop_name)
    await message.answer('Название ИП или ТОО торговой точки?')
    await NewShop.next()


@dp.message_handler(state=NewShop.OfficialShopName, content_types=types.ContentTypes.TEXT)
async def command_add_new_shop_action_three(message: types.Message, state: FSMContext):
    official_shop_name = message.text
    official_shop_name = official_shop_name.strip()
    await state.update_data(official_shop_name=official_shop_name)
    data = await state.get_data()
    await message.answer(f'Адрес торговой точки в {data["district"]}?')
    await NewShop.next()


@dp.message_handler(state=NewShop.Address, content_types=types.ContentTypes.TEXT)
async def command_add_new_shop_action_four(message: types.Message, state: FSMContext):
    address = message.text
    address = address.strip()
    await state.update_data(address=address)
    await message.answer('Владелец или арендатор?', reply_markup=owner_buttons)
    await NewShop.next()


@dp.message_handler(state=NewShop.Owner, content_types=types.ContentTypes.TEXT)
async def command_add_new_shop_action_five(message: types.Message, state: FSMContext):
    owner = message.text
    owner = owner.strip()
    if owner == 'Владелец' or owner == 'Арендатор':
        await state.update_data(owner=owner)
        await message.answer('Напишите номер телефона торговой точки:', reply_markup=types.ReplyKeyboardRemove())
        await NewShop.next()
    else:
        await message.answer('Ошибка. В случае возникновения затруднений обращайтесь в офис.')


@dp.message_handler(state=NewShop.PhoneNumber, content_types=types.ContentTypes.TEXT)
async def command_add_new_shop_action_six(message: types.Message, state: FSMContext):
    phone_number = message.text
    phone_number = phone_number.replace(' ', '').replace('+7', '8').strip()
    if phone_number.isdigit():
        phone_number = int(phone_number)
        await state.update_data(phone_number=phone_number)
        await message.answer('Ф.И.О. или просто имя продавца?')
        await NewShop.next()
    else:
        await message.answer('Это не похоже на номер телефон. Пример: 87775553322')


@dp.message_handler(state=NewShop.SellerName, content_types=types.ContentTypes.TEXT)
async def command_add_new_shop_action_seven(message: types.Message, state: FSMContext):
    seller_name = message.text
    await state.update_data(seller_name=seller_name)
    await message.answer('Кассовый аппарат или ИИН торговой точки:')
    await NewShop.next()


@dp.message_handler(state=NewShop.CashMachine, content_types=types.ContentTypes.TEXT)
async def command_add_new_shop_action_final(message: types.Message, state: FSMContext):
    cash_machine = message.text
    cash_machine = cash_machine.strip()
    await state.update_data(cash_machine=cash_machine)
    data = await state.get_data()
    new_shop = Shop(data['district'], data['shop_name'], data['official_shop_name'], data['address'], data['owner'],
                    data['phone_number'], data['seller_name'], data['cash_machine'])
    new_shop.add_shop()
    await message.answer(f"Готово!\n"
                         f"Торговая точка была добавлена в базу!\n\n"
                         f"{data['shop_name']}\n"
                         f"{data['owner']} {data['official_shop_name']}\n"
                         f"Адрес: {data['district']}, {data['address']}\n"
                         f"Телефон: {data['phone_number']}\n"
                         f"Продавец: {data['seller_name']}\n"
                         f"Кассовый аппарат: {data['cash_machine']}")
    await state.finish()


@dp.message_handler(commands=["new_request"], state="*")
async def command_request(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    employee = get_employee_by_id(telegram_id)
    if employee:
        await Request.District.set()
        await state.update_data(employee=employee)
        available_districts = get_the_districts_available_to_the_employee(employee)
        await state.update_data(available_districts=available_districts)
        districts_keyboard = create_keyboard(available_districts)
        await message.answer('Выбери район:', reply_markup=districts_keyboard)


@dp.message_handler(state=Request.District, content_types=types.ContentTypes.TEXT)
async def command_request_action_one(message: types.Message, state: FSMContext):
    district = message.text
    data = await state.get_data()
    available_districts = data['available_districts']
    if district in available_districts:
        await state.update_data(district=district)
        all_shops = get_all_shops_in_district(district)
        await state.update_data(all_shops=all_shops)
        shops_names = get_shops_names(all_shops)
        await state.update_data(shops_names=shops_names)
        shops_keyboard = create_keyboard(shops_names)
        await message.answer(f'Выбери название торговой точки:', reply_markup=shops_keyboard)
        await Request.next()
    else:
        await message.answer(f'Выбери район из предложенных вариантов или обратись в офис')


@dp.message_handler(state=Request.ShopName, content_types=types.ContentTypes.TEXT)
async def command_request_action_two(message: types.Message, state: FSMContext):
    shop_name = message.text
    data = await state.get_data()
    shops_names = data['shops_names']
    if shop_name in shops_names:
        shop = get_shop(shop_name, data['all_shops'])
        await state.update_data(shop=shop)
        all_products = get_all_products()
        await state.update_data(all_products=all_products)
        products_types = get_products_types(all_products)
        await state.update_data(products_types=products_types)
        products_types_keyboard = create_keyboard(products_types)
        await message.answer(f'Выбери категорию товара: ', reply_markup=products_types_keyboard)
        await Request.next()
    else:
        await message.answer('Выберите магазин из предложенных.\n'
                             'Если же такого нет, можете добавить новую торговую точку /add_new_shop')


@dp.message_handler(state=Request.ProductCategory, content_types=types.ContentTypes.TEXT)
async def command_request_action_three(message: types.Message, state: FSMContext):
    product_type = message.text
    data = await state.get_data()
    products_types = data['products_types']
    if product_type in products_types:
        await state.update_data(product_type=product_type)
        products_names = get_products_names_by_type(data['all_products'], product_type)
        await state.update_data(products_names=products_names)
        products_names_keyboards = create_keyboard(products_names)
        await message.answer(f'Выбери товар: ', reply_markup=products_names_keyboards)
        await Request.next()
    else:
        await message.answer('Выберите из предложенных, или обратитесь в офис')


@dp.message_handler(state=Request.Product, content_types=types.ContentTypes.TEXT)
async def command_request_action_four(message: types.Message, state: FSMContext):
    product_name = message.text
    data = await state.get_data()
    products_names = data['products_names']
    if product_name in products_names:
        await state.update_data(product_name=product_name)
        product = get_product(data['all_products'], product_name)
        await state.update_data(product=product)
        max_number_of_product = product['Количество']
        await message.answer(f'Количество (доступно {max_number_of_product}):',
                             reply_markup=back_button)
        await Request.next()
    else:
        await message.answer('Выберите из предложенных, или обратитесь в офис')


@dp.message_handler(state=Request.Number, content_types=types.ContentTypes.TEXT)
async def command_request_action_five(message: types.Message, state: FSMContext):
    number_of_products = message.text.replace(' ', '')
    if number_of_products == 'Назад' or int(number_of_products) == 0:
        data = await state.get_data()
        products_types_keyboard = create_keyboard(data['products_types'])
        await message.answer(f'Выбери категорию товара: ', reply_markup=products_types_keyboard)
        await Request.ProductCategory.set()
        return
    if number_of_products.isdigit():
        data = await state.get_data()
        product = data['product']
        if int(number_of_products) <= int(product['Количество']):
            product['Количество'] = int(number_of_products)
            product['Сумма'] = product['Цена'] * product['Количество']
            await state.update_data(product=product)
            order_data = {'employee': data['employee'], 'shop': data['shop'],
                          'orders': [product], 'total_sum': product['Сумма']}
            telegram_id = message.from_user.id
            create_new_json_file(str(telegram_id), order_data)
            convert_product_quantity_to_reserve(data['all_products'], data['product_name'], int(number_of_products))
            shop_data = get_shop_data_from_data(order_data)
            await message.answer(f'Торговая точка:\n{", ".join(shop_data)}')
            product_data = get_product_data_from_data(order_data)
            for product in product_data:
                await message.answer('\n'.join(product))
            await message.answer(f'Общая сумма: {int(order_data["total_sum"])} тг')
            await message.answer(f'Что дальше?', reply_markup=next_choice_buttons)
            await state.finish()
        else:
            await message.answer(f'У нас столько нет!\n'
                                 f'Доступно только {product["Количество"]} единиц товара.')
    else:
        await message.answer(f'Это не число!')


@dp.message_handler(text='Добавить товар')
async def text_add_product(message: types.Message, state: FSMContext):
    await RequestAdd.ProductCategory.set()
    all_products = get_all_products()
    await state.update_data(all_products=all_products)
    products_types = get_products_types(all_products)
    await state.update_data(products_types=products_types)
    products_types_keyboard = create_keyboard(products_types)
    await message.answer(f'Выбери категорию товара: ', reply_markup=products_types_keyboard)


@dp.message_handler(state=RequestAdd.ProductCategory, content_types=types.ContentTypes.TEXT)
async def command_request_add_action_one(message: types.Message, state: FSMContext):
    product_type = message.text
    data = await state.get_data()
    products_types = data['products_types']
    if product_type in products_types:
        await state.update_data(product_type=product_type)
        products_names = get_products_names_by_type(data['all_products'], product_type)
        await state.update_data(products_names=products_names)
        products_names_keyboard = create_keyboard(products_names)
        await message.answer(f'Выбери товар: ', reply_markup=products_names_keyboard)
        await RequestAdd.next()
    else:
        await message.answer('Выберите из предложенных, или обратитесь в офис')


@dp.message_handler(state=RequestAdd.Product, content_types=types.ContentTypes.TEXT)
async def command_request_add_action_two(message: types.Message, state: FSMContext):
    product_name = message.text
    data = await state.get_data()
    products_names = data['products_names']
    if product_name in products_names:
        await state.update_data(product_name=product_name)
        product = get_product(data['all_products'], product_name)
        await state.update_data(product=product)
        max_number_of_product = product['Количество']
        await message.answer(f'Количество (доступно {max_number_of_product}):',
                             reply_markup=back_button)
        await RequestAdd.next()
    else:
        await message.answer('Выберите из предложенных, или обратитесь в офис')


@dp.message_handler(state=RequestAdd.Number, content_types=types.ContentTypes.TEXT)
async def command_request_add_action_three(message: types.Message, state: FSMContext):
    number_of_products = message.text.replace(' ', '')
    if number_of_products == 'Назад' or int(number_of_products) == 0:
        data = await state.get_data()
        products_types_keyboard = create_keyboard(data['products_types'])
        await message.answer(f'Выбери категорию товара: ', reply_markup=products_types_keyboard)
        await RequestAdd.ProductCategory.set()
        return
    if number_of_products.isdigit():
        data = await state.get_data()
        product = data['product']
        if int(number_of_products) <= int(product['Количество']):
            product['Количество'] = int(number_of_products)
            product['Сумма'] = product['Цена'] * product['Количество']
            await state.update_data(product=product)
            telegram_id = message.from_user.id
            order_data = get_data_from_json_file(telegram_id)
            products = get_products_names_from_data(order_data)
            if product['Номенклатура'] in products:
                index = get_product_index_by_name_in_data(product['Номенклатура'], order_data)
                order_data['orders'][index]['Количество'] += product['Количество']
                order_data['orders'][index]['Сумма'] += product['Сумма']
            else:
                order_data['orders'].append(product)
            order_data['total_sum'] += product['Сумма']
            edit_data_in_json_file(telegram_id, order_data)
            convert_product_quantity_to_reserve(data['all_products'], data['product_name'], int(number_of_products))
            shop_data = get_shop_data_from_data(order_data)
            await message.answer(f'Торговая точка:\n{", ".join(shop_data)}')
            product_data = get_product_data_from_data(order_data)
            for product in product_data:
                await message.answer('\n'.join(product))
            await message.answer(f'Общая сумма: {int(order_data["total_sum"])} тг')
            await message.answer(f'Что дальше?', reply_markup=next_choice_buttons)
            await state.finish()
        else:
            await message.answer(f'У нас столько нет!\n'
                                 f'Доступно только {product["Количество"]} единиц товара.')
    else:
        await message.answer(f'Это не число!')


@dp.message_handler(text='Удалить товар')
async def text_delete_product(message: types.Message):
    telegram_id = message.from_user.id
    orders = get_data_from_json_file(telegram_id)["orders"]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for order in orders:
        button = types.KeyboardButton(order['Номенклатура'])
        markup.add(button)
    cancel_button = types.KeyboardButton('Отмена')
    markup.add(cancel_button)
    await message.answer(f'Что удалить?', reply_markup=markup)
    await DeleteProduct.Delete.set()


@dp.message_handler(state=DeleteProduct.Delete, content_types=types.ContentTypes.TEXT)
async def text_delete_product_action(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == 'Отмена':
        await message.answer(f'Что дальше?', reply_markup=next_choice_buttons)
        await state.finish()
    else:
        telegram_id = message.from_user.id
        data = get_data_from_json_file(telegram_id)
        product_index = get_product_index_by_name_in_data(answer, data)
        if product_index is not None:
            data['total_sum'] -= data['orders'][product_index]['Сумма']
            number_of_product = data['orders'][product_index]['Количество']
            all_products = get_all_products()
            convert_product_in_reserve_to_quantity(all_products, answer, number_of_product)
            del data['orders'][product_index]
            edit_data_in_json_file(telegram_id, data)
            shop_data = get_shop_data_from_data(data)
            await message.answer(f'Торговая точка:\n{", ".join(shop_data)}')
            product_data = get_product_data_from_data(data)
            for product in product_data:
                await message.answer('\n'.join(product))
            await message.answer(f'Общая сумма: {int(data["total_sum"])} тг')
            await message.answer(f'Что дальше?', reply_markup=next_choice_buttons)
            await state.finish()
        else:
            await message.answer('Товар не найден')


@dp.message_handler(text='Завершить 📄')
async def text_the_end(message: types.Message):
    telegram_id = message.from_user.id
    data = get_data_from_json_file(telegram_id)
    request_number = get_last_number_in_requests() + 1
    datetime_now = time_in_uralsk()
    request_data = get_product_name_and_count_from_data(data)
    employee_name = data['employee']['Сокращенное имя']
    request = [[request_number, datetime_now, data['shop'].get('Название', 'Неизвестно'),
                data['shop'].get('ИП/ТОО', 'Неизвестно'), data['shop'].get('Адрес', 'Неизвестно'),
                request_data, data['total_sum'], data['shop'].get('Кассовый аппарат', 'Неизвестно'),
                employee_name, 'Принят']]
    append_data_in_table(config.REQUESTS, list_name='Все', user_value=request)
    lists_in_table = get_lists_names_in_table(config.REQUESTS)
    if employee_name not in lists_in_table:
        create_new_list_in_table(config.REQUESTS, employee_name)
        add_base_titles_from_the_first_page_in_list(config.REQUESTS, employee_name)
    append_data_in_table(config.REQUESTS, list_name=employee_name, user_value=request)
    add_link_to_request_status(employee_name)
    uralsk_date = time_in_uralsk_date()
    new_doc(data, request_number, uralsk_date)
    file_name = f'Счет-фактура {request_number}.xlsx'
    try:
        with open(r'./docs/' + file_name, 'rb') as document:
            await message.answer_document(document)
            delete_file(file_name)
    except:
        pass
    await message.answer('Заявка была принята!', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer('ʕ ᵔᴥᵔ ʔ', reply_markup=types.ReplyKeyboardRemove())

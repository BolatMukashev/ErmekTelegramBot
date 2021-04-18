# -*- coding: utf-8 -*-
import config
from bot import service
import os
import json
from typing import Union
import pytz
from datetime import datetime


def get_table_data(table_id: str, range1: str, range2: str, list_name: str = 'Лист1', position: str = 'ROWS'):
    """Чтение из таблицы"""
    values = service.spreadsheets().values().get(
        spreadsheetId=table_id,
        range=f'{list_name}!{range1}:{range2}',
        majorDimension=position
    ).execute()
    table_data = values['values']
    return table_data


def get_data_in_message_form(table_data: list):
    result = [' '.join(x) for x in table_data]
    result = '\n'.join(result)
    return result


def get_table_range(table_id: str, list_name: str, position: str = 'ROWS'):
    """Получить количество строк в листе таблицы"""
    values = service.spreadsheets().values().get(
        spreadsheetId=table_id,
        range=f'{list_name}!A1:Z20000',
        majorDimension=position
    ).execute()
    table_data = values['values']
    return len(table_data)


def update_data_in_table(table_id: str, list_name: str, range1: str, user_value: list, position: str = 'ROWS'):
    """Обновить данные в таблице (user_value - это список списков)"""
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=table_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": f"{list_name}!{range1}",
                 "majorDimension": position,
                 "values": user_value}
            ]
        }
    ).execute()


def append_data_in_table(table_id: str, list_name: str, user_value: list, position: str = 'ROWS'):
    """Запись в конец таблицы (user_value - это список списков)"""
    list_range = get_table_range(table_id, list_name)
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=table_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": f"{list_name}!A{list_range + 1}",
                 "majorDimension": position,
                 "values": user_value}
            ]
        }
    ).execute()


def set_link_to_cell(table_id: str, donor_list: str, donor_cell: str, recipient_list: str, recipient_cell: str):
    values = [[f'=\'{donor_list}\'!{donor_cell}']]
    body = {'values': values}
    service.spreadsheets().values().update(spreadsheetId=table_id, range=f'{recipient_list}!{recipient_cell}',
                                           valueInputOption="USER_ENTERED", body=body).execute()


def get_trusted_id() -> list:
    """Получить TelegramID всех сотрудников"""
    all_id = get_table_data(config.EMPLOYEES_LIST, range1='C2', range2='C10000', position='COLUMNS')
    all_id = [int(x) for x in all_id[0]]
    return all_id


def check_id(telegram_id: int):
    """Проверить есть ли этот ID в списке"""
    all_id = get_trusted_id()
    if telegram_id in all_id:
        return True


def get_lists_names_in_table(table_id: str) -> list:
    """Получить названия листов в таблице"""
    sheet_metadata = service.spreadsheets().get(spreadsheetId=table_id).execute()
    sheets = sheet_metadata.get('sheets', '')
    all_lists = [x['properties']['title'] for x in sheets]
    return all_lists


def get_spreadsheet_titles(table_id: str, list_name: str = 'Лист1'):
    """Получить названия заголовков в листе таблицы"""
    titles = get_table_data(table_id, 'A1', 'Z1', list_name=list_name)
    return titles[0]


def get_districts():
    """Получить доступные районы"""
    data = get_table_data(config.SHOPS, 'C2', 'C10000', position='COLUMNS')
    data = list(set(data[0], ))
    return data


def get_all_shops_in_district(district: str):
    """Получить данные о магазинах в выбранном районе в "json" формате"""
    titles = get_spreadsheet_titles(config.SHOPS, list_name=district)
    data = get_table_data(config.SHOPS, 'A2', 'Z10000', list_name=district)
    formatted_data = []
    for rows in data:
        res = {titles[idd]: value for idd, value in enumerate(rows)}
        formatted_data.append(res)
    return formatted_data


def get_shops_name_by_district(district: str) -> list:
    """Получить названия всех магазинов в районе"""
    shops = get_table_data(config.SHOPS, 'A2', 'A10000', list_name=district, position='COLUMNS')[0]
    return shops


def get_shop_by_name_and_district(shop_name: str, district: str):
    """Получить данные магазина по имени и району"""
    data = get_all_shops_in_district(district)
    for shop in data:
        if shop_name.strip() == shop['Название'].strip():
            return shop


def get_all_employees():
    """Получить данные о всех сотрудниках в "json" формате"""
    titles = get_spreadsheet_titles(config.EMPLOYEES_LIST)
    data = get_table_data(config.EMPLOYEES_LIST, 'A2', 'D10000')
    formatted_data = []
    for rows in data:
        res = {titles[idd]: value for idd, value in enumerate(rows)}
        formatted_data.append(res)
    return formatted_data


def get_employee_by_id(telegram_id: int):
    """Получить данные о сотруднике по Telegram ID"""
    if check_id(telegram_id):
        all_employees = get_all_employees()
        for employee in all_employees:
            if str(telegram_id) == employee['Telegram ID']:
                return employee


def get_the_districts_available_to_the_employee(telegram_id: int) -> list:
    """Получить список доступных сотруднику районов"""
    user = get_employee_by_id(telegram_id)
    available_districts = user['Доступные маршруты'].split(',')
    available_districts = [x.strip() for x in available_districts]
    return available_districts


def get_all_products():
    """Получить данные о всех продуктах в "json" формате"""
    titles = get_spreadsheet_titles(config.PRODUCTS)
    data = get_table_data(config.PRODUCTS, 'A2', 'Z10000')
    formatted_data = []
    for rows in data:
        res = {titles[idd]: value for idd, value in enumerate(rows)}
        res['Цена'] = int(float(res['Цена'].replace(',', '.')))
        formatted_data.append(res)
    return formatted_data


def get_products_types():
    """Получить все виды продуктов"""
    all_products = get_all_products()
    result = []
    for product in all_products:
        result.append(product['Категория товара'])
    result = sorted(list(set(result)))
    return result


def get_products_names_by_type(product_type):
    """Получить названия всех продуктов по типу продукта"""
    all_products = get_all_products()
    result = []
    for product in all_products:
        if product['Категория товара'] == product_type and product['Наличие'] == 'Да':
            result.append(product['Номенклатура'])
    return result


def get_product_by_name(product_name):
    """Получить продукт по названию"""
    all_products = get_all_products()
    for product in all_products:
        if product['Номенклатура'] == product_name:
            return product


def create_new_list_in_table(table_id: str, list_name: str):
    """Создать новый лист в таблице"""
    requests = [{'addSheet': {'properties': {'title': list_name}}}]
    body = {'requests': requests}
    try:
        service.spreadsheets().batchUpdate(spreadsheetId=table_id, body=body).execute()
    except:
        print('Такой лист уже существует')


def add_base_titles_from_the_first_page_in_list(table_id: str, list_name: str):
    """Добавить заголовки из первой страицы в нужную страницу"""
    list_names = get_lists_names_in_table(table_id)
    titles = get_spreadsheet_titles(table_id, list_names[0])
    update_data_in_table(table_id, list_name, 'A1', [titles])


def add_base_titles_from_the_first_page_in_all_pages(table_id: str):
    """Добавить заголовки из первой страицы во все страницы"""
    list_names = get_lists_names_in_table(table_id)
    titles = get_spreadsheet_titles(table_id, list_names[0])
    for user_list in list_names:
        update_data_in_table(table_id, user_list, 'A1', [titles])


def create_new_json_file(telegram_id: Union[str, int], order_data: dict):
    """Создаем файл заказа, basic_structure = {'employee': {}, 'shop': {}, 'orders': [], 'total_sum' : 0}"""
    path = os.path.join(os.getcwd(), 'employee_operations', f'{telegram_id}.json')
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(order_data, json_file, ensure_ascii=False, default=str)


def get_data_from_json_file(telegram_id: Union[str, int]) -> dict:
    """Получить данные из json файла"""
    path = os.path.join(os.getcwd(), 'employee_operations', f'{telegram_id}.json')
    with open(path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        return data


def edit_data_in_json_file(telegram_id: Union[str, int], new_data: dict):
    """Изменить данные в json файле"""
    path = os.path.join(os.getcwd(), 'employee_operations', f'{telegram_id}.json')
    with open(path, 'w', encoding='utf-8') as json_file:
        json.dump(new_data, json_file, ensure_ascii=False)


def get_products_names_from_data(data: dict) -> list:
    """Получить названия продуктов"""
    product_names = []
    for product in data['orders']:
        product_names.append(product['Номенклатура'])
    return product_names


def get_product_index_by_name_in_data(product_name: str, data: dict) -> int:
    """Получить индекс продукта"""
    for idd, product in enumerate(data['orders']):
        if product['Номенклатура'] == product_name:
            return idd


def get_shop_data_from_data(data: dict) -> list:
    """Получить данные магазниа"""
    shop = data["shop"]
    shop_data = [shop["Название"], shop['ИП/ТОО'], shop['Адрес'],
                 f'Тел.: {shop["Телефон"]}', f'Кассовый аппарат: {shop["Кассовый аппарат"]}']
    return shop_data


def get_product_data_from_data(data: dict) -> list:
    """Получить данные продуктов (список списков)"""
    orders = data["orders"]
    products_list = []
    for product in orders:
        product_data = ['Заявка:', product['Номенклатура'], f'Количество: {product["Количество"]}',
                        f'Цена: {int(product["Цена"])} тг', f'Сумма: {int(product["Сумма"])} тг']
        products_list.append(product_data)
    return products_list


def get_product_name_and_count_from_data(data: dict) -> str:
    """Получить названия и количество продуктов"""
    orders = data["orders"]
    products_list = []
    for product in orders:
        product_data = f'{product["Номенклатура"]}({product["Штрих код"]})\t📥 {product["Количество"]} шт'
        products_list.append(product_data)
    products_list = '\n'.join(products_list)
    return products_list


def get_last_number_in_requests() -> int:
    """Получить данные продуктов (список списков)"""
    numbers = get_table_data(config.REQUESTS, 'A2', 'A20000', list_name='Все', position='COLUMNS')
    last_number = int(numbers[0][-1])
    return last_number


def time_in_uralsk() -> str:
    """Получить дату и время г.Уральск/г.Атырау"""
    tz_uralsk = pytz.timezone('Asia/Atyrau')
    time_in_uralsk_now = datetime.now(tz_uralsk)
    return time_in_uralsk_now.strftime('%d.%m.%Y %H:%M:%S')


def time_in_uralsk_date() -> str:
    """Получить дату г.Уральск/г.Атырау"""
    tz_uralsk = pytz.timezone('Asia/Atyrau')
    time_in_uralsk_now = datetime.now(tz_uralsk)
    return time_in_uralsk_now.strftime('%d.%m.%Y')

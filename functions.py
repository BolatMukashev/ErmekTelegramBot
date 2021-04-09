# -*- coding: utf-8 -*-
import config
from bot import service


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
        range=f'{list_name}!A1:Z10000',
        majorDimension=position
    ).execute()
    table_data = values['values']
    return len(table_data)


# user_value - это список списков
def update_data_in_table(table_id: str, list_name: str, range1: str, user_value: list, position: str = 'ROWS'):
    """Обновить данные в таблице"""
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
    """Запись в конец таблицы"""
    list_range = get_table_range(config.TEST_TABLE, list_name)
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


def get_shops_name_in_district(district: str) -> list:
    """Получить названия всех магазинов в районе"""
    shops = get_table_data(config.SHOPS, 'A2', 'A10000', list_name=district, position='COLUMNS')[0]
    return shops


def get_shop_by_name_and_district(shop_name: str, district: str):
    """Получить данные магазина по имени и району"""
    data = get_all_shops_in_district(district)
    for shop in data:
        if shop_name == shop['Название']:
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
        res['Цена'] = float(res['Цена'].replace(',', '.'))
        formatted_data.append(res)
    return formatted_data


def get_products_types():
    """Получить все виды продуктов"""
    all_products = get_all_products()
    result = []
    for product in all_products:
        result.append(product['Вид'])
    result = sorted(list(set(result)))
    return result


def get_products_names_by_type(product_type):
    """Получить названия всех продуктов по типу продукта"""
    all_products = get_all_products()
    result = []
    for product in all_products:
        if product['Вид'] == product_type and product['Наличие'] == 'Да':
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


print(get_shop_by_name_and_district('Р-к байтерек бутик№24', '6 мкр'))

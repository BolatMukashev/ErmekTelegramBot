from functions import *
import config


def get_gaps_in_names(table_id: str):
    list_names = get_lists_names_in_table(table_id)
    for _list in list_names:
        names_in_list = get_table_data(table_id, 'A2', 'A10000', list_name=_list, position='COLUMNS')[0]
        for name in names_in_list:
            if name != name.strip():
                print(f'{_list} -> {name}')


# get_gaps_in_names(config.SHOPS)

# -*- coding: utf-8 -*-
from functions import append_data_in_table
import config


class User(object):
    def __init__(self, telegram_id, full_name, simple_name, accessible_areas):
        self.telegram_id = telegram_id
        self.full_name = full_name
        self.simple_name = simple_name
        self.accessible_areas = accessible_areas


class Shop(object):
    def __init__(self, district, shop_name, official_shop_name, address, owner, phone_number, seller_name, cash_machine,
                 remark='-'):
        self.district = district
        self.shop_name = shop_name
        self.official_shop_name = official_shop_name
        self.address = address
        self.owner = owner
        self.phone_number = phone_number
        self.seller_name = seller_name
        self.cash_machine = cash_machine
        self.remark = remark

    def add_shop(self):
        """Добавляем магазин в гугл таблицу"""
        values = [[self.shop_name, self.official_shop_name, self.address, self.owner, self.phone_number,
                  self.seller_name, self.cash_machine, self.remark]]
        append_data_in_table(config.SHOPS, list_name=self.district, user_value=values)

# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       shop
Date Created:   2015-11-05 10:00
Description:

"""

from dianjing.exception import GameException

from core.resource import Resource
from config import ConfigErrorMessage


class ItemShop(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def buy(self, item_id, amount):
        pass
        # config = ConfigItem.get(item_id)
        # if not config:
        #     raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_EXIST"))
        #
        # if config.buy_type == 0:
        #     raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_SELL"))
        #
        # if config.buy_type == 1:
        #     check = {'gold': -config.buy_cost * amount}
        # else:
        #     check = {'diamond': -config.buy_cost * amount}
        #
        # check['message'] = u"Buy Item {0}, amount {1}".format(item_id, amount)
        #
        # with Resource(self.server_id, self.char_id).check(**check):
        #     ItemManager(self.server_id, self.char_id).add_item(item_id, amount=amount)

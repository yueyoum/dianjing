# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       shop
Date Created:   2015-11-05 10:00
Description:

"""

from dianjing.exception import GameException

from core.bag import BagItem
from core.resource import Resource
from config import ConfigItem, ConfigErrorMessage


class ItemShop(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def buy(self, item_id, amount):
        config = ConfigItem.get(item_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_EXIST"))

        if config.buy_type == 0:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_SELL"))

        if config.buy_type == 1:
            check = {'gold': -config.buy_cost}
        else:
            check = {'diamond': -config.buy_cost}

        check['message'] = u"Buy Item {0}".format(item_id)

        with Resource(self.server_id, self.char_id).check(**check):
            BagItem(self.server_id, self.char_id).add([(item_id, amount)])

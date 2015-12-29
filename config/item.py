# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       item
Date Created:   2015-10-21 15:33
Description:

"""

from config.base import ConfigBase

class Item(object):
    __slots__ = ['id', 'tp', 'buy_type', 'buy_cost', 'sell_gold', 'value']
    def __init__(self):
        self.id = 0
        self.tp = 0
        self.buy_type = 0
        self.buy_cost = 0
        self.sell_gold = 0
        self.value = 0

class ConfigItem(ConfigBase):
    EntityClass = Item
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, _id):
        """

        :rtype : Item
        """
        return super(ConfigItem, cls).get(_id)

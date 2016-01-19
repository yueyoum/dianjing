# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       item
Date Created:   2015-10-21 15:33
Description:

"""

from config.base import ConfigBase


class Item(object):
    __slots__ = ['id', 'tp', 'group_id', 'quality', 'buy_type', 'buy_cost', 'sell_gold', 'value',
                 ]

    def __init__(self):
        self.id = 0
        self.tp = 0
        self.group_id = 0
        self.quality = 0
        self.buy_type = 0
        self.buy_cost = 0
        self.sell_gold = 0
        self.value = 0


class Equipment(object):
    __slots__ = [
        'id', 'need_club_level',
        'template_0',
        'template_1', 'template_2',
    ]

    def __init__(self):
        self.id = 0
        self.need_club_level = 0

        self.template_0 = []
        self.template_1 = []
        self.template_2 = []


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

class ConfigEquipment(ConfigBase):
    EntityClass = Equipment
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Equipment
        """
        return super(ConfigEquipment, cls).get(_id)

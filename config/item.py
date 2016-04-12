# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       item
Date Created:   2015-10-21 15:33
Description:

"""

import copy
import random
from config.base import ConfigBase


class ItemNew(object):
    __slots__ = [
        'id', 'tp', 'quality', 'stack_max'
    ]

    def __init__(self):
        self.id = 0
        self.tp = 0
        self.quality = 0
        self.stack_max = 0

class ItemUse(object):
    __slots__ = [
        'id', 'use_item_id', 'use_item_amount', 'result'
    ]

    def __init__(self):
        self.id = 0
        self.use_item_id = 0
        self.use_item_amount = 0
        self.result = []

    def using_result(self):
        result = {}
        for group in self.result:
            item = copy.deepcopy(group)
            for i in range(1, len(item)):
                item[i][2] += item[i-1][2]

            prob = random.randint(1, 1000)
            for _id, _amount, _prob in item:
                if _prob >= prob:
                    if _id in result:
                        result[_id] += _amount
                    else:
                        result[_id] = _amount

                    break

        return result.items()


class ItemMerge(object):
    __slots__ = [
        'id', 'amount', 'to_id', 'renown', 'crystal'
    ]

    def __init__(self):
        self.id = 0
        self.amount = 0
        self.to_id = 0
        self.renown = 0
        self.crystal = 0


class EquipmentLevel(object):
    __slots__ = [
        'attack', 'attack_percent', 'defense', 'defense_percent',
        'manage', 'manage_percent', 'operation', 'operation_percent',
        'update_item_need'
    ]

    @classmethod
    def create(cls, data):
        obj = cls()
        for key in cls.__slots__:
            setattr(obj, key, data[key])

        return obj

    def __init__(self):
        self.attack = 0
        self.attack_percent = 0
        self.defense = 0
        self.defense_percent = 0
        self.manage = 0
        self.manage_percent = 0
        self.operation = 0
        self.operation_percent = 0
        self.update_item_need = []


class EquipmentNew(object):
    __slots__ = [
        'id', 'tp', 'renown', 'max_level', 'levels'
    ]

    def __init__(self):
        self.id = 0
        self.tp = 0
        self.renown = 0
        self.max_level = 0
        self.levels = {}
        """:type: dict[int, EquipmentLevel]"""

class ItemExp(object):
    __slots__ = [
        'id', 'exp'
    ]

    def __init__(self):
        self.id = 0
        self.exp = 0


class ConfigItemNew(ConfigBase):
    EntityClass = ItemNew
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: ItemNew
        """
        return super(ConfigItemNew, cls).get(_id)

class ConfigItemUse(ConfigBase):
    EntityClass = ItemUse
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: ItemUse
        """
        return super(ConfigItemUse, cls).get(_id)


class ConfigItemMerge(ConfigBase):
    EntityClass = ItemMerge
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: ItemMerge
        """
        return super(ConfigItemMerge, cls).get(_id)


class ConfigEquipmentNew(ConfigBase):
    EntityClass = EquipmentNew
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigEquipmentNew, cls).initialize(fixture)
        for obj in cls.INSTANCES.values():
            levels = {}
            for k, v in obj.levels.iteritems():
                levels[int(k)] = EquipmentLevel.create(v)

            obj.levels = levels

    @classmethod
    def get(cls, _id):
        """

        :rtype: EquipmentNew
        """
        return super(ConfigEquipmentNew, cls).get(_id)

class ConfigItemExp(ConfigBase):
    EntityClass = ItemExp
    INSTANCES = {}
    FILTER_CACHE = {}

    ALL_ITEM_IDS = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigItemExp, cls).initialize(fixture)
        cls.ALL_ITEM_IDS = cls.INSTANCES.keys()

    @classmethod
    def get(cls, _id):
        # type: (int) -> ItemExp
        return super(ConfigItemExp, cls).get(_id)
# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       territory
Date Created:   2016-05-13 10-11
Description:

"""

import random

from config.base import ConfigBase

class _Inspire(object):
    __slots__ = ['max_times', 'reward', 'exp']
    def __init__(self):
        self.max_times = 0
        self.reward = []
        self.exp = 0

    def get_reward(self):
        prob = random.randint(1, 100)
        for _id, _amount, _prob in self.reward:
            if _prob >= prob:
                return [_id, _amount]

        return []


class _Level(object):
    __slots__ = ['exp', 'product_rate', 'product_limit', 'events', 'inspire']
    def __init__(self):
        self.exp = 0
        self.product_rate = 0
        self.product_limit = 0
        self.events = []
        self.inspire = None
        """:type: _Inspire"""

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def create(cls, data):
        obj = cls()
        obj.exp = data['exp']
        obj.product_rate = data['product_rate']
        obj.product_limit = data['product_limit']
        obj.events = data['events']

        obj.inspire = _Inspire()
        obj.inspire.max_times = data['inspire']['max_times']
        obj.inspire.reward = data['inspire']['reward']
        obj.inspire.exp = data['inspire']['exp']

        return obj

class _SlotBuildingLevel(object):
    __slots__ = ['extra_product', 'cost_amount']
    def __init__(self):
        self.extra_product = []
        self.cost_amount = []


class _Slot(object):
    __slots__ = ['need_building_level', 'need_vip_level', 'exp_modulus', 'building_levels']
    def __init__(self):
        self.need_building_level = 0
        self.need_vip_level = 0
        self.exp_modulus = 0
        self.building_levels = {}
        """:type: dict[int, _SlotBuildingLevel]"""

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def create(cls, data):
        obj = cls()
        obj.need_building_level = data['need_building_level']
        obj.need_vip_level = data['need_vip_level']
        obj.exp_modulus = data['exp_modulus']

        for k, v in data['building_levels'].iteritems():
            _sbl = _SlotBuildingLevel()
            _sbl.extra_product = v['extra_product']
            _sbl.cost_amount = v['cost_amount']

            obj.building_levels[int(k)] = _sbl

        return obj

    def get_extra_product(self, building_level):
        return random.choice(self.building_levels[building_level].extra_product)

    def get_cost_amount(self, building_level, hour_index):
        return self.building_levels[building_level].cost_amount[hour_index]


class TerritoryBuilding(object):
    __slots__ = [
        'id', 'levels', 'slots'
    ]

    def __init__(self):
        self.id = 0
        self.levels = {}
        """:type: dict[int, _Level]"""
        self.slots = {}
        """:type: dict[int, _Slot]"""

    def get_extra_product(self, slot_id, building_level):
        """

        :rtype: [int, int]
        """
        return random.choice(self.slots[slot_id].building_levels[building_level].extra_product)

    def get_cost_amount(self, slot_id, building_level, method):
        """

        :rtype: int
        """
        return self.slots[slot_id].building_levels[building_level].cost_amount[method]


class ConfigTerritoryBuilding(ConfigBase):
    EntityClass = TerritoryBuilding
    INSTANCES = {}
    """:type: dict[int, TerritoryBuilding]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigTerritoryBuilding, cls).initialize(fixture)

        for _, v in cls.INSTANCES.iteritems():
            v.levels = {int(_lv): _Level.create(_data) for _lv, _data in v.levels.iteritems()}
            v.slots = {int(_s): _Slot.create(_data) for _s, _data in v.slots.iteritems()}


    @classmethod
    def get(cls, _id):
        """

        :rtype: TerritoryBuilding
        """
        return super(ConfigTerritoryBuilding, cls).get(_id)



###########################

class InspireCost(object):
    __slots__ = ['id', 'diamond']
    def __init__(self):
        self.id = 0
        self.diamond = 0

class ConfigInspireCost(ConfigBase):
    EntityClass = InspireCost
    INSTANCES = {}
    FILTER_CACHE = {}

    _REVERSED = []
    @classmethod
    def initialize(cls, fixture):
        super(ConfigInspireCost, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            cls._REVERSED.append((k, v.diamond))

        cls._REVERSED.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get(cls, _id):
        for a, b in cls._REVERSED:
            if _id >= a:
                return b

        raise RuntimeError("ConfigInspireCost cannot get {0}".format(_id))

#########################

class StaffProduct(object):
    __slots__ = ['id', 'product']
    def __init__(self):
        self.id = 0
        self.product = []

    def get_product(self, hour_index):
        a, b, c = random.choice(self.product[hour_index])
        return [a, random.randint(b, c)]

class ConfigTerritoryStaffProduct(ConfigBase):
    EntityClass = StaffProduct
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: StaffProduct
        """
        super(ConfigTerritoryStaffProduct, cls).get(_id)
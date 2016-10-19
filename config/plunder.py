# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       plunder
Date Created:   2016-08-18 14:36
Description:

"""
import random

from config.base import ConfigBase

class BaseStationLevel(object):
    __slots__ = ['id', 'product', 'exp']
    def __init__(self):
        self.id = 0
        self.product = []
        self.exp = 0

    def get_product(self, percent):
        product = []
        for _id, _amount in self.product:
            _amount = int(_amount * 1.0 * percent / 100)
            if _amount:
                product.append((_id, _amount))

        return product


class Income(object):
    __slots__ = ['id', 'percent', 'exp', 'extra_income']
    def __init__(self):
        self.id = 0
        self.percent = 0
        self.exp = 0
        self.extra_income = []

    def get_extra_income(self):
        prob = random.randint(1, 100)
        for _id, _amount, _prob in self.extra_income:
            if _prob >= prob:
                return [(_id, _amount)]

        return []

class BuyTimesCost(object):
    __slots__ = ['id', 'cost']
    def __init__(self):
        self.id = 0
        self.cost = 0

class NPC(object):
    __slots__ = ['id', 'level_low', 'level_high', 'way_one', 'way_two', 'way_three']
    def __init__(self):
        self.id = 0
        self.level_low = 0
        self.level_high = 0
        self.way_one = []
        self.way_two = []
        self.way_three = []

    def get_way_info(self):
        return random.choice(self.way_one), random.choice(self.way_two), random.choice(self.way_three)

    def to_doc(self, station_level):
        from utils.functional import make_string_id
        from config import ConfigName

        station_level_range = range(station_level-1, station_level+2)
        level = random.choice(station_level_range)
        if level < 1:
            level = 1
        if level > ConfigBaseStationLevel.MAX_LEVEL:
            level = ConfigBaseStationLevel.MAX_LEVEL

        return {
            'id': 'npc:{0}'.format(make_string_id()),
            'spied': False,
            'name': ConfigName.get_random_name(),
            'station_level': level,
            'ways_npc': self.get_way_info()
        }


class DailyReward(object):
    __slots__ = ['id', 'reward']
    def __init__(self):
        self.id = 0
        self.reward = []

class ConfigBaseStationLevel(ConfigBase):
    EntityClass = BaseStationLevel
    INSTANCES = {}
    FILTER_CACHE = {}

    MAX_LEVEL = 0

    @classmethod
    def initialize(cls, fixture):
        super(ConfigBaseStationLevel, cls).initialize(fixture)
        cls.MAX_LEVEL = max(cls.INSTANCES.keys())

    @classmethod
    def get(cls, _id):
        """

        :rtype: BaseStationLevel
        """
        return super(ConfigBaseStationLevel, cls).get(_id)


class ConfigPlunderIncome(ConfigBase):
    EntityClass = Income
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Income
        """
        return super(ConfigPlunderIncome, cls).get(_id)

class ConfigPlunderBuyTimesCost(ConfigBase):
    EntityClass = BuyTimesCost
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigPlunderBuyTimesCost, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            cls.LIST.append((k, v.cost))

        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get_cost(cls, times):
        for t, cost in cls.LIST:
            if times >= t:
                return cost

        raise RuntimeError("ConfigPlunderBuyTimesCost, Error times: {0}".format(times))


class ConfigPlunderNPC(ConfigBase):
    EntityClass = NPC
    INSTANCES = {}
    FILTER_CACHE = {}

    MAP = {}

    @classmethod
    def get_by_level(cls, lv):
        """

        :rtype: NPC
        """
        if lv not in cls.MAP:
            for _, v in cls.INSTANCES.iteritems():
                if v.level_low <= lv <= v.level_high:
                    cls.MAP[lv] = v
                    break
            else:
                raise RuntimeError("ConfigPlunderNPC, Can not find config for level: {0}".format(lv))

        return cls.MAP[lv]

class ConfigPlunderDailyReward(ConfigBase):
    EntityClass = DailyReward
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: DailyReward
        """
        return super(ConfigPlunderDailyReward, cls).get(_id)
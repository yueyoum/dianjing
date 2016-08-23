# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       plunder
Date Created:   2016-08-18 14:36
Description:

"""

from config.base import ConfigBase

class BaseStationLevel(object):
    __slots__ = ['id', 'product', 'exp']
    def __init__(self):
        self.id = 0
        self.product = []
        self.exp = 0

class Income(object):
    __slots__ = ['id', 'percent', 'exp', 'extra_income']
    def __init__(self):
        self.id = 0
        self.percent = 0
        self.exp = 0
        self.extra_income = 0

class BuyTimesCost(object):
    __slots__ = ['id', 'cost']
    def __init__(self):
        self.id = 0
        self.cost = 0


class ConfigBaseStationLevel(ConfigBase):
    EntityClass = BaseStationLevel
    INSTANCES = {}
    FILTER_CACHE = {}

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
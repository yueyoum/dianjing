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
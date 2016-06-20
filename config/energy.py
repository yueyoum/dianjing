# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       energy
Date Created:   2016-06-20 11-08
Description:

"""

from config.base import ConfigBase

class BuyCost(object):
    __slots__ = ['id', 'cost']
    def __init__(self):
        self.id = 0
        self.cost = 0

class ConfigEnergyBuyCost(ConfigBase):
    EntityClass = BuyCost
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []
    @classmethod
    def initialize(cls, fixture):
        super(ConfigEnergyBuyCost, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            cls.LIST.append((k, v.cost))

        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get_cost(cls, times):
        for a, b in cls.LIST:
            if times >= a:
                return b

        raise RuntimeError("ConfigBuyCost, Error times: {0}".format(times))

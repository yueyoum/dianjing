# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       store
Date Created:   2016-05-23 11-52
Description:

"""
import random
from config.base import ConfigBase

class StoreType(object):
    __slots__ = [
        'id', 'money_id', 'refresh_hour_interval'
    ]

    def __init__(self):
        self.id = 0
        self.money_id = 0
        self.refresh_hour_interval = 0


class Store(object):
    __slots__ = [
        'id', 'tp', 'club_level_min', 'club_level_max',
        'condition_id', 'condition_value',
        'times_limit', 'content'
    ]
    
    def __init__(self):
        self.id = 0
        self.tp = 0
        self.club_level_min = 0
        self.club_level_max = 0
        self.condition_id = 0
        self.condition_value = 0
        self.times_limit = 0
        self.content = []
    
    
    def get_random_content_index(self):
        """

        :rtype: int
        """
        return random.choice(range(len(self.content)))


class StoreRefresh(object):
    __slots__ = ['id', 'cost']
    def __init__(self):
        self.id = 0
        self.cost = []


    def get_cost_diamond(self, times):
        for k, v in self.cost:
            if times >= k:
                return v

        raise RuntimeError("Error ConfigStoreRefreshCost, Invalid times: {0}".format(times))

class ConfigStoreType(ConfigBase):
    EntityClass = StoreType
    INSTANCES = {}
    """:type: dict[int, StoreType]"""
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: StoreType
        """
        return super(ConfigStoreType, cls).get(_id)


class ConfigStore(ConfigBase):
    EntityClass = Store
    INSTANCES = {}
    """:type: dict[int, Store]"""
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Store
        """
        return super(ConfigStore, cls).get(_id)


    @classmethod
    def refresh(cls, tp, club_level):
        goods = []
        for k, v in cls.INSTANCES.iteritems():
            if v.tp != tp:
                continue

            if v.club_level_min and v.club_level_min > club_level:
                continue

            if v.club_level_max and v.club_level_max < club_level:
                continue

            goods.append((k, v.get_random_content_index()))

        return goods


class ConfigStoreRefreshCost(ConfigBase):
    EntityClass = StoreRefresh
    INSTANCES = {}
    """:type: dict[int, StoreRefresh]"""
    FILTER_CACHE = {}


    @classmethod
    def get_cost(cls, tp, times):
        return cls.INSTANCES[tp].get_cost_diamond(times)
